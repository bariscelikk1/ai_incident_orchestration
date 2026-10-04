from __future__ import annotations

from app.diagnosis import Diagnoser, get_diagnoser
from app.models import AuditEvent, Incident, IncidentCreate, IncidentStatus
from app.store import IncidentStore
from app.tools import search_logs, search_runbooks


class IncidentOrchestrator:
    def __init__(self, store: IncidentStore, diagnoser: Diagnoser | None = None) -> None:
        self.store = store
        self.diagnoser = diagnoser or get_diagnoser()

    async def investigate(self, request: IncidentCreate) -> Incident:
        incident = Incident(**request.model_dump())
        incident.audit.append(AuditEvent(event="incident_received", detail=request.description))
        incident.status = IncidentStatus.INVESTIGATING

        logs = search_logs(request.service)
        runbooks = search_runbooks(f"{request.title}. {request.description}")
        incident.evidence = [*logs, *runbooks]
        incident.audit.append(
            AuditEvent(
                event="evidence_collected",
                detail=f"Collected {len(logs)} logs and {len(runbooks)} runbook passages",
            )
        )

        incident.diagnosis = await self.diagnoser.diagnose(incident, incident.evidence)
        incident.status = IncidentStatus.AWAITING_APPROVAL
        incident.audit.append(
            AuditEvent(
                event="diagnosis_proposed",
                detail=f"Confidence {incident.diagnosis.confidence}%",
            )
        )
        return self.store.save(incident)

    def decide(self, incident_id: str, decision: str, actor: str, reason: str) -> Incident:
        incident = self.store.get(incident_id)
        if not incident:
            raise KeyError(incident_id)
        if incident.status != IncidentStatus.AWAITING_APPROVAL:
            raise ValueError("Incident is not awaiting approval")

        incident.status = (
            IncidentStatus.APPROVED if decision == "approve" else IncidentStatus.REJECTED
        )
        incident.audit.append(
            AuditEvent(event=f"recommendation_{decision}d", detail=f"{actor}: {reason}")
        )
        return self.store.save(incident)

