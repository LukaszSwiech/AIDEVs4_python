import os

from ..common.master_config import TASK_NAMES, AIDEV_URL, API_KEY

INPUT_FILENAME = "suspects.json"

POWERPLANT_LOCATIONS_URL = (
    AIDEV_URL + "data/" + API_KEY +"/findhim_locations.json"
)

SUSPECT_LOCATIONS_URL = (
    AIDEV_URL + "api/location"
)

SUSPECT_ACCESS_LEVEL_URL = (
    AIDEV_URL + "api/accesslevel"
)

TASK_DIR = os.path.dirname(__file__)
TASK_FOLDER = os.path.basename(TASK_DIR)

INPUT_PATH = TASK_DIR + "/input/"
OUTPUT_PATH = TASK_DIR + "/output/"

TASK_NAME = TASK_NAMES[TASK_FOLDER]

MAX_LLM_ITERATIONS = 30

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search?format=json&limit=1"
NOMINATIM_HEADER = {
    'User-Agent': 'AIDEVs4-Task (educational)',
    }