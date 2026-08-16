import logging
from typing import Any
from collections.abc import Callable, Awaitable

from . import prompt
from .config import MAX_LLM_ITERATIONS
from ..common.agent import make_local_tool_executor, run_agent, MaxToolRoundExceeded

async def run_proxy_agent(msg: str, tools:list[dict],  execute_tool: Callable[[Any], Awaitable[dict]]) -> str:
    history = [{"role": "system", "content": prompt.SENDIT_AGENT},
            {"role": "user", "content": msg}]

    for _ in range (MAX_LLM_ITERATIONS):
        try:
            await run_agent(history, tools, execute_tool, MAX_LLM_ITERATIONS, "sendit", {"verbosity": "low"}, "s01e04")
        except MaxToolRoundExceeded:
            logging.warning(f"Agent {history} hit max iterations without final answer.")
            return"Agent nie zdazyl udzielic odpowiedzi. Przekroczono limit iteracji"
    return"Agent nie zdazyl udzielic odpowiedzi. Przekroczono limit iteracji"