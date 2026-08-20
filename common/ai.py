from openai import AsyncOpenAI

from ..common.master_config import OPENAI_KEY, MODEL
from ..common.token_usage import TokenUsage

client = AsyncOpenAI(
    api_key=OPENAI_KEY
)

token_usage = TokenUsage()

async def chat(msg: list[dict], model: str = MODEL, prompt_cache_key: str |None = None, response_format: dict|None = None, tools: list[dict]|None = None):
    completion =  await client.chat.completions.create(
        model=model,
        messages=msg,
        prompt_cache_key=prompt_cache_key,
        tools=tools,
        response_format=response_format
    )

    if completion.usage:
        token_usage.add(completion.usage)
    return completion

#Implementaion of Stage A — the chat.completions foundation:

# 1. Migrate ai.py from client.responses.create to client.chat.completions.create — the input shape changes (messages with role: "tool" instead of function_call_output) and so does the output shape (choices[0].message, message.tool_calls with function.name / function.arguments).
# 2. Adapt agent.py to the new response shape (the places that currently read response.output*).
# 3. Change the tool definition format in the tasks: Responses uses flat {type, name, parameters}, chat.completions uses nested {type: "function", "function": {name, parameters}}.
# 4. Map usage (prompt_tokens/completion_tokens instead of input_tokens/output_tokens) in TokenUsage.
# 5. Per-model configuration: recognize the prefix → base_url + API key (NVIDIA exposes Nemotron through an OpenAI-compatible endpoint on build.nvidia.com, and a developer key is free). After this step Nemotron works.

# async def chat(msg: list[dict], model: str = MODEL, prompt_cache_key: str |None = None, text: dict|None = None, tools: list[dict]|None = None):
#     response =  await client.responses.create(
#         model=model,
#         input=msg,
#         prompt_cache_key=prompt_cache_key,
#         text=text,
#         tools=tools,
#     )
#     token_usage.add(response.usage)
#     return response