import os

OPENAI_KEY = os.environ["OPENAI_KEY"]
API_KEY = os.environ["API_KEY"]
AIDEV_URL = os.environ["AIDEV_URL"]
AIDEV_ANSWER_URL = AIDEV_URL + "verify"
MODEL = "gpt-5-mini"

TASK_NAMES = {"s01e01": "people", "s01e02": "findhim", "s01e03": "proxy", "s01e04": "sendit", "s01e05": "railway"}