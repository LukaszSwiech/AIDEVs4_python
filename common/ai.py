import re

from ..common.master_config import DEFAULT_MODEL
from ..common.token_usage import TokenUsage
from ..common.providers import create_client, PROVIDER_REGISTRY

token_usage = TokenUsage()

async def chat(msg: list[dict], model: str = DEFAULT_MODEL, prompt_cache_key: str |None = None, response_format: dict|None = None, tools: list[dict]|None = None, verbosity: str|None = None):
    provider_key = resolve_model_for_provider(model)

    provider = PROVIDER_REGISTRY[provider_key]

    client = create_client(provider.base_url, provider.api_key)

    completion =  await client.chat.completions.create(
        model=model,
        messages=msg,
        prompt_cache_key=prompt_cache_key,
        tools=tools,
        response_format=response_format,
        verbosity=verbosity
    )

    if completion.usage:
        token_usage.add(completion.usage)
    return completion

def resolve_model_for_provider(model:str) -> str:
    provider_key = re.split(r"[-/]", model, maxsplit=1)[0]
    return provider_key