import os
import json

from requests import post, exceptions

URL = (
    os.environ["AIDEV_URL"] + "/verify"
)

def send_answer(task_name, answer):
    agent_message = {
        "apikey": os.environ["API_KEY"],
        "task": task_name,
        "answer": answer
        }
    try:
        agent_answer = post(URL, json=agent_message)
    except exceptions.RequestException as e:
        raise RuntimeError(f"Failed to POST the response: {e}") from e
    
    # print(agent_message)

    try:
        print(agent_answer.json())
    except json.JSONDecodeError:
        print(f"Server returned non-JSON: {agent_answer.text}")