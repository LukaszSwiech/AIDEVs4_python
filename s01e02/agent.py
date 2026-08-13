import json

from . import prompt
from .tools import tools
from .config import MAX_LLM_ITERATIONS
from .tools import handlers
from ..common.agent import make_local_tool_executor, run_agent

async def run_proxy_agent(user_prompt: str, powerplant_list: str) -> str:
    content = json.dumps({"suspects": user_prompt, "power_plants": powerplant_list}, ensure_ascii=False)
    history = [{"role": "system", "content": prompt.SUSPECT_SEARCH_AGENT},
            {"role": "user", "content": content}]

    execute_tool = make_local_tool_executor(handlers.handlers)

    agent_response = await run_agent(history, tools.tools, execute_tool, MAX_LLM_ITERATIONS, "findhim_agent", {"verbosity": "low"}, "s01e02")
    return agent_response