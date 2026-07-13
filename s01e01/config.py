import os

from . import prompt
from ..common.master_config import TASK_NAMES, API_KEY, AIDEV_URL

SYSTEM_PROMPT={"role": "system", "content": prompt.JOB_CLASSIFIER_SYSTEM}

TASK_DIR = os.path.dirname(__file__)
TASK_FOLDER = os.path.basename(TASK_DIR)

INPUT_PATH = TASK_DIR + "/input/"
OUTPUT_PATH = TASK_DIR + "/output/"

TASK_NAME = TASK_NAMES[TASK_FOLDER]

URL = (
    AIDEV_URL + "data/" + API_KEY + "/people.csv"
)