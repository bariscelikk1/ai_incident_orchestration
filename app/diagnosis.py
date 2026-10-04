from __future__ import annotations

import json
import os
from typing import Protocol

import httpx

from app.models import Diagnosis, Evidence, Incident


class Diagnoser(Protocol):
    async def diagnose(self, incident: Incident, evidence: list[Evidence]) -> Diagnosis: ...


class DemoDiagnoser:
    """Deterministic diagnosis that makes the repository runnable without an API key."""

    async def diagnose(self, incident: Incident, evidence: list[Evidence]) -> Diagnosis:
        combined = " ".join(item.content.lower() for item in evidence)
        evidence_ids = [item.id for item in evidence]
        if "connection" in combined and ("5/5" in combined or "pool" in combined):
            return Diagnosis(
                severity="high",
                likely_cause="The payment API exhausted its database connection pool.",
                confidence=91,
                recommendation=(
                    "Compare the pool configuration with the latest deployment and restore the "
                    "approved value after an engineer approves the change."
                ),
                evidence_ids=evidence_ids,
                missing_evidence=["Current database connection count from production metrics"],
            )
        if "heartbeat" in combined or "consumer" in combined:
            return Diagnosis(
                severity="high",
                likely_cause="The payment queue consumer appears to be stalled.",
                confidence=84,
                recommendation="Inspect the consumer and restart the worker after approval.",
                evidence_ids=evidence_ids,
                missing_evidence=["Current queue depth"],
            )
        return Diagnosis(
            severity="medium",
            likely_cause="The available evidence is insufficient for a confident diagnosis.",
            confidence=35,
            recommendation="Collect service metrics and deployment events before taking action.",
            evidence_ids=evidence_ids,
            missing_evidence=["Service metrics", "Recent deployment events"],
        )


class OpenAICompatibleDiagnoser:
    def __init__(self) -> None:
        self.api_key = os.environ["LLM_API_KEY"]
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "gpt-4.1-mini")

    async def diagnose(self, incident: Incident, evidence: list[Evidence]) -> Diagnosis:
        evidence_text = "\n".join(f"[{item.id}] {item.content}" for item in evidence)
        prompt = f"""Investigate this simulated software incident.
Use only the supplied evidence. Return JSON with severity, likely_cause, confidence (0-100),
recommendation, evidence_ids, and missing_evidence. Every evidence ID must exist below.

Incident: {incident.title}\n{incident.description}\nService: {incident.service}

Evidence:\n{evidence_text}
"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cautious incident copilot. Never invent evidence.",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        diagnosis = Diagnosis.model_validate(json.loads(content))
        allowed = {item.id for item in evidence}
        if not set(diagnosis.evidence_ids).issubset(allowed):
            raise ValueError("Model cited evidence that was not provided")
        return diagnosis


def get_diagnoser() -> Diagnoser:
    if os.getenv("LLM_API_KEY"):
        return OpenAICompatibleDiagnoser()
    return DemoDiagnoser()

