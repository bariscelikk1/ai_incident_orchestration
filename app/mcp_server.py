from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from app.tools import search_logs as search_logs_impl
from app.tools import search_runbooks as search_runbooks_impl


mcp = MCPServer(
    name="SentinelFlow Tools",
    instructions="Use these tools to collect evidence for simulated payment incidents.",
)


@mcp.tool()
def search_logs(service: str, query: str = "") -> list[dict]:
    """Search simulated service logs and return evidence records."""
    return [item.model_dump() for item in search_logs_impl(service, query)]


@mcp.tool()
def search_runbooks(query: str, limit: int = 2) -> list[dict]:
    """Search operational runbooks using Hugging Face semantic embeddings when configured."""
    return [item.model_dump() for item in search_runbooks_impl(query, limit)]

