import logging
import asyncio
import json
from typing import Any
from collections.abc import Callable, Awaitable

from .ai import chat

# TODO (proposed by AI assistant; implement when there is more time)
#
# 1. make_local_tool_executor - sync handlers block the event loop.
#    Handlers are plain `def`, so `asyncio.gather` in run_agent gives no real
#    concurrency and a network-bound handler stalls everything else on the loop.
#    Fix: inspect.iscoroutinefunction(fn) -> `await fn(**args)`,
#    otherwise -> `await asyncio.to_thread(fn, **args)`.
#    Harmless in single-script tasks, matters once the loop is shared with a
#    webhook server and an MCP session.

class MaxToolRoundExceeded(Exception):
    """The agent kept requesting tools until the round limit was reached."""

ToolExecutor = Callable[[Any], Awaitable[dict]]

def _tool_output(call_id: str, output: str) -> dict:
    return {"type": "function_call_output", "call_id": call_id, "output": output}

def make_local_tool_executor(handlers: dict[str, Callable]) -> ToolExecutor:
    """Errors are returned as tool output, never raised - run_agent depends on this."""
    async def execute_tool(item) -> dict:
        try:
            args = json.loads(item.arguments)
            result = handlers[item.name](**args)
        except Exception as e:
            result = {"Error": str(e)}
        logging.info(f"Calling tool -> {item.name}")
        return _tool_output(item.call_id, json.dumps(result))
    return execute_tool

def make_mcp_tool_executor(mcp_server_name: str, mcp_session_call_tool: Callable[..., Awaitable[Any]]) -> ToolExecutor:
    """Errors are returned as tool output, never raised - run_agent depends on this."""
    async def execute_tool(item) -> dict:
        try:
            args = json.loads(item.arguments)
            tool_name = item.name.removeprefix(f"{mcp_server_name}__")
            result = await mcp_session_call_tool(name=tool_name, arguments=args)
        except Exception as e:
            return _tool_output(item.call_id, json.dumps({"Error": str(e)}))

        text_block = next((b for b in result.content if b.type == 'text'), None)
        if text_block:
            return _tool_output(item.call_id, text_block.text)
        return _tool_output(item.call_id, f"Tool {item.name} returned no text content.")
    return execute_tool

async def run_agent(history: list, tools: list[dict], execute_tool: ToolExecutor, max_tool_rounds: int, prompt_cache_key: str|None = None, text: dict|None = None, agent_name: str |None = None) -> str:
    """Run the tool-calling loop until the model replies without requesting tools.

    `history` is mutated in place: model output and tool results are appended to the
    caller's list, so the caller keeps the full conversation after this returns.

    `execute_tool` receives one function_call item and must return a
    `function_call_output` dict. It must not raise - an exception would leave a
    function_call in `history` with no matching output, which invalidates every
    later request in that conversation.
    """
    for i in range(max_tool_rounds):
        logging.info(f"""#############
Iteration: {i+1} for Agent: {agent_name}
#############""")
        response = await chat(history, tools=tools, prompt_cache_key=prompt_cache_key, text=text)
        history += response.output
        
        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            logging.info(f"-> {response.output_text}")
            return response.output_text

        for item in tool_calls:
            logging.info(f"Agent called tool: {item.name} with args: {item.arguments}")
        outputs = await asyncio.gather(*(execute_tool(item) for item in tool_calls))
        history += outputs
        for output in outputs:
            logging.info(f'Tool_output: {output}')

    raise MaxToolRoundExceeded(
        f"Agent {agent_name} did not finish within {max_tool_rounds} tool rounds."
    )