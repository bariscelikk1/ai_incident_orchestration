import pytest
from mcp import Client

from app.mcp_server import mcp


@pytest.mark.asyncio
async def test_mcp_exposes_and_executes_evidence_tools():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools.tools}
        result = await client.call_tool("search_logs", {"service": "payment-api"})

    assert names == {"search_logs", "search_runbooks"}
    assert result.structured_content is not None
    assert result.structured_content["result"][0]["id"] == "LOG-101"
