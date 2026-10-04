from app.retrieval import RunbookRetriever


def test_database_incident_retrieves_database_runbook(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    results = RunbookRetriever().search(
        "payment requests time out because every database connection is active", limit=1
    )
    assert results[0].id == "RUNBOOK-DB-01"


def test_queue_incident_retrieves_queue_runbook(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    results = RunbookRetriever().search(
        "payment worker heartbeat missing and consumer stalled", limit=1
    )
    assert results[0].id == "RUNBOOK-QUEUE-01"

