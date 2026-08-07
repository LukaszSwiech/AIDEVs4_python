from contextlib import AsyncExitStack
import logging
import pathlib

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None
        self.open_ai_tools: list[dict] = []

    async def _build_openai_tools(self):
        response = await self.session.list_tools()
        self.open_ai_tools = [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema | {"additionalProperties": False},
                "strict": True,
            }
            for tool in response.tools
        ]

    async def connect_to_server(self):
        """Connect to an MCP server"""
        command = "uv"
        mcp_server_path = pathlib.Path(__file__).resolve().parents[3]
        
        server_params = StdioServerParameters(
            command=command,
            args=["run", "--env-file", "craft/.env", "--project", "craft", "python", "-m", "craft.s01e03.mcp_agent.server"],
            cwd=mcp_server_path,
            encoding= "utf-8"
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()
        await self._build_openai_tools()
        logging.info(f"Connected to server with tools: {self.open_ai_tools}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()