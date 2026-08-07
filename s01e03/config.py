import os

from ..common.master_config import TASK_NAMES, AIDEV_URL, FROG_PUBLIC_PORT

PACKAGE_URL = (
    AIDEV_URL + "api/packages"
)

TASK_DIR = os.path.dirname(__file__)
TASK_FOLDER = os.path.basename(TASK_DIR)

INPUT_PATH = TASK_DIR + "/input/"
OUTPUT_PATH = TASK_DIR + "/output/"

TASK_NAME = TASK_NAMES[TASK_FOLDER]

MAX_LLM_ITERATIONS = 30

DESTINATION = "PWR6132PL"

WEBHOOK_PORT = 8888
REMOTE_TUNNEL = FROG_PUBLIC_PORT + ":localhost:" + str(WEBHOOK_PORT)