import json
import asyncio
import logging
from ..common.ai import chat
from . import prompt
from .config import MAX_LLM_ITERATIONS

sessions: dict[str, list] = {}

def _tool_output(call_id: str, output: str) -> dict:
    return {"type": "function_call_output", "call_id": call_id, "output": output}

async def execute_tool(item, mcp_client) -> dict:
    try:
        args = json.loads(item.arguments)
        result = await mcp_client.session.call_tool(name=item.name, arguments=args)
    except Exception as e:
        return _tool_output(item.call_id, json.dumps({"Error": str(e)}))

    text_block = next((b for b in result.content if b.type == 'text'), None)
    if text_block:
        return _tool_output(item.call_id, text_block.text)
    return _tool_output(item.call_id, f"Tool {item.name} returned no text content.")

async def run_agent(session_id: str, msg:str, mcp_client:object) -> str:
    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": prompt.PROXY_AGENT_SYSTEM}]

    sessions[session_id].append({"role": "user", "content": msg})

    for iteration in range(1, MAX_LLM_ITERATIONS + 1):
        response = await chat(sessions[session_id], tools=mcp_client.open_ai_tools, prompt_cache_key="proxy_agent", text={"verbosity": "low"})
        sessions[session_id] += response.output
        
        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            logging.info(f"-> {session_id}: {response.output_text}")
            return response.output_text

        for item in tool_calls:
            logging.info(f"Agent called tool: {item.name} with args: {item.arguments}")
        outputs = await asyncio.gather(*(execute_tool(item, mcp_client) for item in tool_calls))
        sessions[session_id] += outputs
        for output in outputs:
            logging.info(f'Tool_output: {output}')

    logging.warning(f"Agent {session_id} hit max iterations without final answer.")
    return "Agent nie zdazyl udzielic odpowiedzi. Przekroczono limit iteracji"