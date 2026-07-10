from openai import AsyncOpenAI

from .tools import tools
from ..common.token_usage import TokenUsage
from ..common.master_config import OPENAI_KEY, MODEL

client = AsyncOpenAI(
    api_key=OPENAI_KEY
)
token_usage = TokenUsage()

async def chat(msg, tools=tools.tools):
    response =  await client.responses.create(
        model=MODEL,
        #reasoning={"effort": "low"},
        text={"verbosity": "low"},
        tools=tools,
        input=msg,
        prompt_cache_key="findhim_agent",
    )

    token_usage.add(response.usage)
    return response