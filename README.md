# SentinelFlow

SentinelFlow is a one-week portfolio MVP for evidence-grounded incident orchestration. It investigates simulated payment incidents, calls MCP tools to collect logs and runbooks, proposes a diagnosis, and requires an engineer to approve or reject the recommendation.

## What the demo proves

- The application separates tool access from model reasoning through MCP.
- Runbook retrieval can use Hugging Face embeddings and has a no-key fallback.
- Diagnoses use structured output and may cite only evidence collected by the workflow.
- Recommendations stop at a human approval gate.
- Every material transition appears in the incident audit history.
- The default deterministic diagnoser makes the repository runnable without paid services.

## Run locally

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. API documentation is available at `/docs`, and the Streamable HTTP MCP endpoint is `/api/mcp/`.

## Enable real model integrations

Copy `.env.example` to `.env` and export the values in your shell or deployment environment.

- `HF_TOKEN` enables semantic runbook embeddings through Hugging Face. Without it, retrieval uses deterministic lexical similarity.
- `LLM_API_KEY` enables an OpenAI-compatible diagnosis provider. Without it, the deterministic demo provider is used.
- `LLM_BASE_URL` and `LLM_MODEL` select the compatible provider and model.

Never commit `.env` or API keys.

## Test

```bash
pytest
```

The tests verify retrieval, evidence grounding, the approval gate and protection against duplicate decisions.

## Deploy to Vercel

Import the GitHub repository into Vercel and configure the optional secrets in Project Settings. `api/index.py` exposes the FastAPI ASGI application, while `vercel.json` routes requests to it.

The MVP uses an in-memory store, so incidents can disappear when a serverless instance restarts. Replace `IncidentStore` with hosted Postgres before presenting persistence as a production feature.

## Scope

This project deliberately uses simulated data and never performs a real remediation action. Its purpose is to demonstrate orchestration, MCP integration, retrieval, structured model output, approval controls and evaluation—not autonomous infrastructure access.
