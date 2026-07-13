import os
import csv
import asyncio
import json

from . import answer
from . import schema
from ..common.ai import chat, token_usage
from ..common.utils import fetch_file
from .config import SYSTEM_PROMPT, URL, OUTPUT_PATH, TASK_NAME

CURRENT_YEAR = 2026
MAX_BIRTH_YEAR = CURRENT_YEAR - 20
MIN_BIRTH_YEAR = CURRENT_YEAR - 40
POTENTIAL_SUS_FILEPATH = os.path.join(OUTPUT_PATH, "people.csv")
SUS_PATH = os.path.join(OUTPUT_PATH, "suspects.json")


def get_suspects_csv_file(url: str, output_path: str) -> None:
    result = fetch_file("GET", url, stream=True)
    if isinstance(result, dict) and "Error" in result:
        raise RuntimeError("Error fetching CSV file.")
    with open(output_path, 'wb') as fd:
        fd.write(result)

def get_potential_suspects(file_path: str) -> list:
    potential_suspects = []
    try:
        with open(file_path, 'r') as suspects_file:
            file_reader = csv.DictReader(suspects_file, delimiter=',')
            for line in file_reader:
                birth_year = int(line['birthDate'].split("-")[0])
                if line['gender'] == 'M' and line['birthPlace'] == 'Grudziądz' and MIN_BIRTH_YEAR <= birth_year <= MAX_BIRTH_YEAR:
                    potential_suspects.append(line)
    except OSError as e:
        raise RuntimeError(f"Could not open/read file {file_path}: {e}") from e
    return potential_suspects

async def get_suspect_list(suspects: list) -> list:
    suspect_list = []
    tasks = [chat([SYSTEM_PROMPT, {"role": "user", "content": suspect['job']}], text=schema.TAGS_SCHEMA, prompt_cache_key="job-classifier-1") for suspect in suspects]
    responses = await asyncio.gather(*tasks)

    for suspect, response in zip(suspects, responses):
        tag = json.loads(response.output_text)["tags"]
        if 'transport' in tag:
            suspect_list.append({"name": suspect["name"],
                                    "surname": suspect["surname"],
                                    "gender": suspect["gender"],
                                    "born": suspect['birthDate'].split("-")[0],
                                    "city": suspect["birthPlace"],
                                    "tags": tag
            })
    return suspect_list

async def main() -> None:

    get_suspects_csv_file(URL, POTENTIAL_SUS_FILEPATH)
    potential_suspects = get_potential_suspects(POTENTIAL_SUS_FILEPATH)
    list_of_suspects = await get_suspect_list(potential_suspects)

    answer.send_answer(TASK_NAME, list_of_suspects)
    token_usage.log_total()

    with open(SUS_PATH, mode='w') as f:
        f.write(json.dumps(list_of_suspects))

if __name__ == "__main__":
    asyncio.run(main())