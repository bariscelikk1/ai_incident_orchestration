from __future__ import annotations

from app.data import LOGS
from app.models import Evidence
from app.retrieval import RunbookRetriever


def search_logs(service: str, query: str = "") -> list[Evidence]:
    """Return prepared log records for a service, optionally filtered by query words."""
    words = {word.lower() for word in query.split() if len(word) > 3}
    matches: list[Evidence] = []
    for item in LOGS:
        if item["service"] != service:
            continue
        content = item["content"]
        if words and not any(word in content.lower() for word in words):
            continue
        matches.append(Evidence(id=item["id"], source="log", content=content))
    return matches


def search_runbooks(query: str, limit: int = 2) -> list[Evidence]:
    """Find runbooks that are semantically related to an incident description."""
    return RunbookRetriever().search(query=query, limit=limit)

