from openai import AsyncOpenAI

from ..common.master_config import OPENAI_KEY, MODEL
from ..common.token_usage import TokenUsage

client = AsyncOpenAI(
    api_key=OPENAI_KEY
)
token_usage = TokenUsage()

async def chat(msg: str, model: str=MODEL, prompt_cache_key: str=None, text: str=None, tools: str=None):
    response =  await client.responses.create(
        model=model,
        input=msg,
        prompt_cache_key=prompt_cache_key,
        text=text,
        tools=tools,
    )
    token_usage.add(response.usage)
    return response