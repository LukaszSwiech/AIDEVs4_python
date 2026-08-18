import os

from ..common.master_config import TASK_NAMES

TASK_DIR = os.path.dirname(__file__)
TASK_FOLDER = os.path.basename(TASK_DIR)

INPUT_PATH = TASK_DIR + "/input/"
OUTPUT_PATH = TASK_DIR + "/output/"

TASK_NAME = TASK_NAMES[TASK_FOLDER]

MAX_LLM_ITERATIONS = 30

DOCU_URL = "https://hub.ag3nts.org/dane/doc/index.md"