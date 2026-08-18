import logging
import re
from typing import Any
from collections.abc import Callable, Awaitable

from . import prompt
from .config import MAX_LLM_ITERATIONS
from ..common.agent import make_local_tool_executor, run_agent, MaxToolRoundExceeded

flag_pattern = r"\{FLG:\w+\}"
user_message = "Prepare and send the transport declaration for the shipment from Gdańsk to Żarnowiec. Start by fetching the documentation."

async def run_proxy_agent(tools:list[dict],  execute_tool: Callable[[Any], Awaitable[dict]]) -> str:
    history = [{"role": "system", "content": prompt.SENDIT_AGENT},
               {"role": "user", "content": user_message}]
 
    try:
        text_response = await run_agent(history, tools, execute_tool, MAX_LLM_ITERATIONS, "sendit", {"verbosity": "low"}, "s01e04")
    except MaxToolRoundExceeded:
        logging.warning(f"sendit agent hit max iterations without final answer. History: {history}")
        return "Agent nie zdazyl udzielic odpowiedzi. Przekroczono limit iteracji"
    
    match = re.search(flag_pattern, text_response)
    if match:
        flag = match.group(0)
        return flag
    logging.warning(f"sendit agent didn't return the FLG in the last answer. Agent history of executions: {history}")
    return "Agent nie zwrocil poprawnej flagi."