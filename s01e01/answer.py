import json

from ..common.master_config import AIDEV_URL, API_KEY
from ..common.utils import fetch_page

URL = (AIDEV_URL + "/verify")

def send_answer(task_name, answer):
    agent_message = {
        "apikey": API_KEY,
        "task": task_name,
        "answer": answer
        }
    answer = fetch_page("POST", URL, json=agent_message)
    if isinstance(answer, dict) and "Error" in answer:
        raise RuntimeError("Failed to POST the response.")

    print(answer)