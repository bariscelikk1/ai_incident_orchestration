from __future__ import annotations

from threading import Lock

from app.models import Incident


class IncidentStore:
    """In-memory MVP store. Replace with Postgres before multi-user production use."""

    def __init__(self) -> None:
        self._items: dict[str, Incident] = {}
        self._lock = Lock()

    def save(self, incident: Incident) -> Incident:
        with self._lock:
            self._items[incident.id] = incident.model_copy(deep=True)
        return incident

    def get(self, incident_id: str) -> Incident | None:
        with self._lock:
            incident = self._items.get(incident_id)
            return incident.model_copy(deep=True) if incident else None

    def all(self) -> list[Incident]:
        with self._lock:
            return [item.model_copy(deep=True) for item in self._items.values()]


store = IncidentStore()

