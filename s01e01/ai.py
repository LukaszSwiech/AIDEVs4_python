import os

from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ["OPEN_AI_KEY"]
)

async def chat(input, tools=None):
    response =  await client.responses.create(
        model="gpt-5-mini",
        input=input,
        prompt_cache_key="job-classifier-1",
        text={
            "format": {
                "type": "json_schema",
                "name": "tags",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["tags"],
                    "additionalProperties": False
                }
            }
        },
    )
    return response