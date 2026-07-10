# SUMMARY:
# 1. Lesson technique applied: tool-calling agent with a contextual feedback loop — the model
#    geocodes plant cities (Nominatim), computes min haversine distance per suspect/plant pair,
#    checks access levels, and reports to the hub; tool errors and hub rejections are returned
#    as function_call_output so the model self-corrects and retries the next candidate.
# 2. Techniques: function calling (strict JSON schemas), small model (gpt-5-mini), prompt caching
#    (stable prefix + prompt_cache_key, ~95% cached input), token usage tracking, enriched tool errors.
# 3. Reusing: common/utils.fetch_page, common/token_usage.TokenUsage, common/master_config.

import json
import asyncio
from dataclasses import dataclass, field

from . import config
from ..common.master_config import API_KEY
from ..common.utils import fetch_page
from .agent import run_agent
from .ai import token_usage

@dataclass
class Suspect:
    name: str
    surname: str
    born: int
    locations: list = field(default_factory=list)

def load_suspects_from_file(path: str, filename: str) -> list:
    try:
        with open(path + filename, mode='r') as f:
            list_of_suspects = json.load(f)
            return list_of_suspects
    except OSError as e:
        raise RuntimeError(f"Could not open/read file {filename}: {e}") from e

def get_suspect_locations(name: str, surname: str) -> list:
    result = fetch_page("POST", config.SUSPECT_LOCATIONS_URL, json = {"apikey": API_KEY, "name": name, "surname": surname})
    if isinstance(result, dict) and "Error" in result:
        raise RuntimeError(f"Could not fetch suspect location: {result}")
    return result

def get_powerplant_locations() -> list:
    result = fetch_page("GET", config.POWERPLANT_LOCATIONS_URL)
    if isinstance (result, dict) and "Error" in result:
        raise RuntimeError(f"Could not fetch power plants: {result}")
    return result

def main() -> None:
    suspects = []
    list_of_suspects = load_suspects_from_file(config.INPUT_PATH, config.INPUT_FILENAME)

    powerplant_list = get_powerplant_locations()

    for suspect in list_of_suspects:
        suspect_location_list = get_suspect_locations(suspect["name"], suspect["surname"])
        suspects.append(Suspect(suspect["name"], suspect["surname"], suspect["born"], locations=suspect_location_list))

    asyncio.run(run_agent([ob.__dict__ for ob in suspects], powerplant_list))
    token_usage.log_total()

if __name__ == "__main__":
    main()