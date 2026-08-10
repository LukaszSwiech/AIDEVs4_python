# SUMMARY:
# 1. MCP host/client/server: the package tools live in a separate stdio subprocess, discovered at
#    runtime via list_tools() and converted to OpenAI function schemas. The host namespaces tool
#    names (proxy__check_package) to prevent cross-server collisions and strips the prefix on call.
# 2. Tools designed for the model, not for a developer: self-describing schemas (Annotated +
#    pydantic Field) carry the contract, so the system prompt no longer has to explain the tools.
# 3. Dynamic hints/recovery_hints in every tool response: success hints reinforce the next step,
#    error hints prescribe recovery.
# 4. A long-lived conversational agent instead of a one-shot script: the AI Devs hub drives a
#    multi-turn chat against an HTTP webhook exposed through an SSH reverse tunnel the script opens
#    and tears down itself; per-sessionID history keeps the persona coherent across turns.
# 5. Concurrency: a single asyncio loop owns the MCP session while ThreadingHTTPServer serves
#    requests from worker threads; tool calls within one turn run in parallel.
# 6. Also: strict function-calling schemas, small model (gpt-5-mini), prompt caching (stable system
#    prefix + prompt_cache_key), AsyncExitStack + try/finally for deterministic cleanup of the MCP
#    subprocess and the SSH tunnel, persona prompt with a hidden objective. Reusing: common/ai.chat,
#    common/utils.fetch_page, common/token_usage.TokenUsage, common/master_config.
#
# TODO: no graceful degradation on OpenAI rate limits — the webhook returns 500 and drops the
# operator's session instead of stalling in persona.

import logging
from rich.logging import RichHandler
from rich.console import Console
import threading
import asyncio
import subprocess

from ..common.master_config import PUBLIC_URL, AIDEV_ANSWER_URL, API_KEY, FROG_PROXY_SERVER, FROG_PROXY_PORT
from .config import TASK_NAME, REMOTE_TUNNEL
from ..common.utils import fetch_page
from .mcp_agent import client as mcp_client
from .webhook import server as webhook_server
from ..common.ai import token_usage

handlers = []
handlers.append(RichHandler(console=Console(stderr=True), rich_tracebacks=True))

logging.basicConfig(level=logging.INFO,format="%(message)s", handlers=handlers)

async def init_mcp() -> mcp_client.MCPClient:
    client = mcp_client.MCPClient()
    await client.connect_to_server()
    return client

def start_proxy_server():
    proxy_command = ["ssh", "-f", "-R", REMOTE_TUNNEL, FROG_PROXY_SERVER, "-p", FROG_PROXY_PORT, "-N"]
    kill_proxy_server()
    subprocess.run(proxy_command, check=True)

def kill_proxy_server():
    subprocess.run(["pkill", "-f", REMOTE_TUNNEL])

async def main():
 
    task_trigger = {
        "apikey": API_KEY,
        "task": TASK_NAME,
        "answer": {
            "url": PUBLIC_URL,
            "sessionID": "init"
            }
        }
    
    client = await init_mcp()

    try:
        start_proxy_server()

        loop = asyncio.get_running_loop()
        shutdown_event = asyncio.Event()

        server_thread = threading.Thread(target=webhook_server.run, args=(loop, client, shutdown_event), daemon=True)
        server_thread.start()

        init_task_result = fetch_page("POST", AIDEV_ANSWER_URL, json=task_trigger)
        if "Error" in init_task_result:
            logging.error(f"Failed to initiate task: {init_task_result}")
            return
        
        await shutdown_event.wait()
    finally:
        logging.info("Shutting down MCP server...")
        await client.cleanup()
        kill_proxy_server()
        token_usage.log_total()

if __name__ == "__main__":
    asyncio.run(main())