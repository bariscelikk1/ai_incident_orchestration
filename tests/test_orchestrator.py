import pytest

from app.diagnosis import DemoDiagnoser
from app.models import IncidentCreate, IncidentStatus
from app.orchestrator import IncidentOrchestrator
from app.store import IncidentStore


@pytest.mark.asyncio
async def test_investigation_is_grounded_and_waits_for_approval(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    service = IncidentOrchestrator(IncidentStore(), DemoDiagnoser())
    incident = await service.investigate(
        IncidentCreate(
            title="Payment requests are timing out",
            description="Customers cannot complete payments and latency rose sharply.",
            service="payment-api",
        )
    )

    assert incident.status == IncidentStatus.AWAITING_APPROVAL
    assert incident.diagnosis is not None
    assert incident.diagnosis.confidence == 91
    available_ids = {item.id for item in incident.evidence}
    assert set(incident.diagnosis.evidence_ids) == available_ids


@pytest.mark.asyncio
async def test_decision_is_recorded_once(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    store = IncidentStore()
    service = IncidentOrchestrator(store, DemoDiagnoser())
    incident = await service.investigate(
        IncidentCreate(
            title="Payment requests are timing out",
            description="Customers cannot complete payments and latency rose sharply.",
            service="payment-api",
        )
    )

    approved = service.decide(incident.id, "approve", "reviewer", "Evidence checked")
    assert approved.status == IncidentStatus.APPROVED
    assert approved.audit[-1].event == "recommendation_approved"
    with pytest.raises(ValueError, match="not awaiting approval"):
        service.decide(incident.id, "approve", "reviewer", "Duplicate")

