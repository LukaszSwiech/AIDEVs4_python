import asyncio
import json

from . import prompt
from . import ai
from .config import MAX_LLM_ITERATIONS
from .tools import handlers

async def execute_tool(item) -> dict:
    try:
        args = json.loads(item.arguments)
        result = handlers.handlers[item.name](**args)
    except Exception as e:
        result = {"Error": str(e)}
    print(f"Calling tool -> {item.name}")
    return {
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result)
    }

async def run_agent(user_promt: str, powerplant_list: str) -> str:
    content = json.dumps({"suspects": user_promt, "power_plants": powerplant_list}, ensure_ascii=False)
    history = [{"role": "system", "content": prompt.SUSPECT_SEARCH_AGENT},
            {"role": "user", "content": content}]

    for i in range(MAX_LLM_ITERATIONS):
        print(f"""#############
Iteration: {i+1}
#############""")
        response = await ai.chat(history)
        history += response.output

        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            print(f"Agent returend answer -> {response.output_text}")
            return response.output_text

        outputs = await asyncio.gather(*(execute_tool(item) for item in tool_calls))
        history += outputs
    else:
        print("Max number of iterations reached")