# SUMMARY:
# 1. Lesson technique applied: MCP (Model Context Protocol) — the two package tools run in a
#    separate stdio subprocess; the client discovers them at runtime via list_tools() and
#    converts their schemas to OpenAI function definitions, so the agent's toolset is never
#    hardcoded on the client side.
# 2. A long-lived conversational agent instead of a one-shot script: the AI Devs hub drives a
#    multi-turn chat against an HTTP webhook that the script exposes publicly through an SSH
#    reverse tunnel it opens and tears down itself; per-sessionID history keeps the persona
#    coherent across turns until the hub returns the flag.
# 3. Concurrency: a single asyncio loop owns the MCP session while ThreadingHTTPServer serves
#    requests from worker threads — the two are bridged with run_coroutine_threadsafe and
#    call_soon_threadsafe; tool calls within one turn run in parallel via asyncio.gather.
# 4. Techniques: function calling (strict JSON schemas), small model (gpt-5-mini), prompt caching
#    (stable system prefix + prompt_cache_key), AsyncExitStack + try/finally for deterministic
#    cleanup of the MCP subprocess and the SSH tunnel, persona prompt with a hidden objective.
# 5. Reusing: common/ai.chat, common/utils.fetch_page, common/token_usage.TokenUsage,
#    common/master_config.

import logging
from rich.logging import RichHandler
from rich.console import Console
import threading
import asyncio
import subprocess

from ..common.master_config import PUBLIC_URL, AIDEV_ANSWER_URL, API_KEY, FROG_PROXY_SERVER, FROG_PROXY_PORT, FROG_PUBLIC_PORT
from .config import TASK_NAME, WEBHOOK_PORT, REMOTE_TUNNEL
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