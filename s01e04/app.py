import logging
import asyncio

from .mcp_agent import client as mcp_client

from ..common.logs import setup_logging
from ..common.agent import make_mcp_tool_executor

async def init_mcp() -> mcp_client.MCPClient:
    client = mcp_client.MCPClient()
    await client.connect_to_server()
    return client

async def main():
    setup_logging()

    client = await init_mcp()

    execute_tool =  make_mcp_tool_executor(client.server_name, client.session.call_tool)
    tools = client.open_ai_tools

    

if __name__ == "__main__":
    asyncio.run(main())