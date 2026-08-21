import logging
from . import prompt
from .config import MAX_LLM_ITERATIONS
from ..common.agent import run_agent, MaxToolRoundExceeded
from typing import Any
from collections.abc import Callable, Awaitable

sessions: dict[str, list] = {}

async def run_proxy_agent(session_id: str, msg:str, tools:list[dict],  execute_tool: Callable[[Any], Awaitable[dict]]) -> str:
    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": prompt.PROXY_AGENT_SYSTEM}]

    sessions[session_id].append({"role": "user", "content": msg})

    try:
        return await run_agent(history=sessions[session_id], tools=tools, execute_tool=execute_tool, max_tool_rounds=MAX_LLM_ITERATIONS, prompt_cache_key="proxy_agent", agent_name="s01e03", verbosity="low")
    except MaxToolRoundExceeded:
        logging.warning(f"Agent {session_id} hit max iterations without final answer.")
        return"Agent nie zdazyl udzielic odpowiedzi. Przekroczono limit iteracji"