from __future__ import annotations

import contextlib
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.data import DEMO_INCIDENTS
from app.mcp_server import mcp
from app.models import DecisionRequest, Incident, IncidentCreate
from app.orchestrator import IncidentOrchestrator
from app.store import store


mcp_app = mcp.streamable_http_app(
    streamable_http_path="/",
    stateless_http=True,
    json_response=True,
)


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="SentinelFlow",
    description="Evidence-grounded payment incident investigation",
    version="0.1.0",
    lifespan=lifespan,
)
app.mount("/api/mcp", mcp_app)
orchestrator = IncidentOrchestrator(store)
web_path = Path(__file__).parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(web_path)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mcp": "/api/mcp/"}


@app.get("/api/demo-incidents")
async def demo_incidents() -> list[dict[str, str]]:
    return DEMO_INCIDENTS


@app.get("/api/incidents")
async def list_incidents() -> list[Incident]:
    return store.all()


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str) -> Incident:
    incident = store.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.post("/api/incidents", status_code=201)
async def create_incident(request: IncidentCreate) -> Incident:
    try:
        return await orchestrator.investigate(request)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Investigation failed: {exc}") from exc


@app.post("/api/incidents/{incident_id}/decision")
async def decide(incident_id: str, request: DecisionRequest) -> Incident:
    try:
        return orchestrator.decide(
            incident_id, request.decision, request.actor, request.reason
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Incident not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

