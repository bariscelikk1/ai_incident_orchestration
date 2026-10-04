from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class IncidentStatus(StrEnum):
    RECEIVED = "received"
    INVESTIGATING = "investigating"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    service: str = Field(default="payment-api", min_length=2, max_length=80)


class Evidence(BaseModel):
    id: str
    source: str
    content: str
    score: float | None = None


class Diagnosis(BaseModel):
    severity: str
    likely_cause: str
    confidence: int = Field(ge=0, le=100)
    recommendation: str
    evidence_ids: list[str]
    missing_evidence: list[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event: str
    detail: str


class Incident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    service: str
    status: IncidentStatus = IncidentStatus.RECEIVED
    evidence: list[Evidence] = Field(default_factory=list)
    diagnosis: Diagnosis | None = None
    audit: list[AuditEvent] = Field(default_factory=list)


class DecisionRequest(BaseModel):
    decision: str = Field(pattern="^(approve|reject)$")
    actor: str = Field(default="demo-engineer", min_length=2, max_length=80)
    reason: str = Field(default="Reviewed available evidence", max_length=500)

