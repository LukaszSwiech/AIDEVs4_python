import logging
import asyncio
from .mcp_agent import client as mcp_client

from .agent import run_proxy_agent
from ..common.logs import setup_logging
from ..common.agent import make_mcp_tool_executor
from ..common.ai import token_usage

async def init_mcp() -> mcp_client.MCPClient:
    client = mcp_client.MCPClient()
    await client.connect_to_server()
    return client

async def main():

    setup_logging()

    client = await init_mcp()

    try:
        execute_tool =  make_mcp_tool_executor(client.server_name, client.session.call_tool)
        tools = client.open_ai_tools

        solve_exercise = await run_proxy_agent(tools, execute_tool)
        logging.info(f"Agent zakonczyl zadanie. Jego odpowiedz to {solve_exercise}")

    finally:
        logging.info("Shutting down MCP server...")
        await client.cleanup()
        token_usage.log_total()

if __name__ == "__main__":
    asyncio.run(main())