import os
import csv
import asyncio
import json

from requests import get, exceptions

import ai
import prompt
import answer

TASK_NAME = 'people'
CURRENT_YEAR = 2026
MAX_BIRTH_YEAR = CURRENT_YEAR - 20
MIN_BIRTH_YEAR = CURRENT_YEAR - 40
SYSTEM_PROMPT={"role": "system", "content": prompt.JOB_CLASSIFIER_SYSTEM}
FILENAME = "people.csv"
OUTPUT_PATH = "s01e01/output/"
URL = (
    os.environ["AIDEV_URL"] + "/data/" + os.environ["API_KEY"] + "/people.csv"
)

def get_potential_suspects(path: str, filename: str) -> list:
    potential_suspects = []

    try:
        with open(os.path.join(path, filename), 'r') as suspects_file:
            file_reader = csv.DictReader(suspects_file, delimiter=',')
            for line in file_reader:
                birth_year = int(line['birthDate'].split("-")[0])
                if line['gender'] == 'M' and line['birthPlace'] == 'Grudziądz' and MIN_BIRTH_YEAR <= birth_year <= MAX_BIRTH_YEAR:
                    potential_suspects.append(line)
    except OSError as e:
        raise RuntimeError(f"Could not open/read file {filename}: {e}") from e

    return potential_suspects

async def get_suspect_list(suspects: list) -> list:

    suspect_list = []
    cached_tokens = 0
    total_time_taken_to_complete = 0

    tasks = [ai.chat([SYSTEM_PROMPT, {"role": "user", "content": suspect['job']}]) for suspect in suspects]

    responses = await asyncio.gather(*tasks)

    for suspect, response in zip(suspects, responses):
        tag = json.loads(response.output_text)["tags"]

        cached_tokens += (response.usage.input_tokens_details.cached_tokens)
        total_time_taken_to_complete += (response.completed_at - response.created_at)

        if 'transport' in tag:
            suspect_list.append({"name": suspect["name"],
                                    "surname": suspect["surname"],
                                    "gender": suspect["gender"],
                                    "born": suspect['birthDate'].split("-")[0],
                                    "city": suspect["birthPlace"],
                                    "tags": tag
            })

    return suspect_list, cached_tokens, total_time_taken_to_complete

async def main() -> None:
    try:
        r = get(URL, stream=True)
        r.raise_for_status()
        with open(os.path.join(OUTPUT_PATH, FILENAME), 'wb') as fd:
            fd.write(r.content)
    except exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching CSV: {e.code} {e.reason}") from e

    potential_suspects = get_potential_suspects(OUTPUT_PATH, FILENAME)
    list_of_suspects, saved_tokens, time_taken = await get_suspect_list(potential_suspects)

    answer.send_answer(TASK_NAME, list_of_suspects)
    print(f"By caching system prompt you saved {saved_tokens} tokens")
    print(f"It took {time_taken} s to receive all answers from the ai model") 

    with open("s01e01/output/suspects.json", mode='w') as f:
        f.write(json.dumps(list_of_suspects))

if __name__ == "__main__":
    asyncio.run(main())