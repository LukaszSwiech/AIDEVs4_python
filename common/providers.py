from dataclasses import dataclass
from functools import cache
from openai import AsyncOpenAI

from .master_config import OPENAI_KEY, NVIDIA_KEY

@dataclass
class LLMProvider:
    base_url: str
    api_key: str
    supports_prompt_cache: bool
    supports_verbosity: bool

PROVIDER_REGISTRY = {
    "gpt":    LLMProvider(base_url="https://api.openai.com/v1", api_key=OPENAI_KEY, supports_prompt_cache=True,  supports_verbosity=True),
    "nvidia": LLMProvider(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_KEY, supports_prompt_cache=False, supports_verbosity=False),
}

@cache
def create_client(base_url:str, api_key:str) -> AsyncOpenAI:
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )
    return client