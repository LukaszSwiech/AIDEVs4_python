import logging
import re
from typing import Any
from collections.abc import Callable, Awaitable

from . import prompt
from .config import MAX_LLM_ITERATIONS
from ..common.agent import make_local_tool_executor, run_agent, MaxToolRoundExceeded

flag_pattern = r"\{FLG:\w+\}"

async def run_proxy_agent(tools:list[dict],  execute_tool: Callable[[Any], Awaitable[dict]]) -> str:
    history = [{"role": "system", "content": prompt.SENDIT_AGENT}]

    for i in range (MAX_LLM_ITERATIONS):
        try:
            text_response = await run_agent(history, tools, execute_tool, MAX_LLM_ITERATIONS, "sendit", {"verbosity": "low"}, "s01e04")
        except MaxToolRoundExceeded:
            logging.warning(f"sendit agent hit max tool rounds on outer iteration {i + 1}/{MAX_LLM_ITERATIONS}.")
            history.append({
                "role" : "user",
                "content" : (
                    "You exceeded the tool-call round limit this turn without finishing the task. "
                    "Continue from where you left off: finish the remaining tool calls, "
                    "and this time reach a final answer faster."
                )
            })
            continue
        
        match = re.search(flag_pattern, text_response)
        if match:
            flag = match.group(0)
            return flag
        
        logging.info(f"sendit agent replied without a flag on outer iteration {i + 1}/{MAX_LLM_ITERATIONS}")

        history.append({
            "role" : "assistant",
            "content" : text_response
        })

    return"Agent nie zdazyl udzielic odpowiedzi. Przekroczono limit iteracji"