from math import radians, sin, cos, sqrt, atan2, inf
from time import sleep

from requests import get, post, exceptions
from ...common.utils import fetch_page
from ..config import TASK_NAME, NOMINATIM_URL, NOMINATIM_HEADER, SUSPECT_ACCESS_LEVEL_URL
from ...common.master_config import API_KEY, AIDEV_ANSWER_URL

handlers = {}
EARTH_RADIUS = 6371.0

def tool(fn):
    handlers[fn.__name__] = fn
    return fn

@tool
def search_location_coordinates(location: str) -> dict:
    results = fetch_page("GET", NOMINATIM_URL, params= {"q": location}, headers=NOMINATIM_HEADER)
    sleep(1.1)
    if isinstance(results, dict) and "Error" in results:
        return {"Error": f"Geocoding failed for '{location}'", "details:": results}
    if not results:
        return {"Error": f"No coordinates found for '{location}'"}
    coordinates = results[0]
    return {"lat" : float(coordinates["lat"]),"lon":  float(coordinates["lon"])}

@tool
def get_suspect_access_level(name: str, surname: str, born: int) -> str:
    result = fetch_page("POST", SUSPECT_ACCESS_LEVEL_URL, json={"apikey": API_KEY, "name": name, "surname": surname, "birthYear": born})
    if "Error" in result:
        return {"Error": f"Couldn't retrieve access level for {name} {surname}", "details:": result}
    return result.get("accessLevel") if result is not None else None
        
@tool
def get_min_distance_to_plant(name: str, surname: str, plant_code: str, plant_lat: float, plant_lon: float, suspect_locations: list) -> tuple:
    min_distance = min(haversine(plant_lat, plant_lon, location["latitude"], location["longitude"]) for location in suspect_locations)
    return {"name": name, "surname": surname, "plant_code": plant_code, "distance_km": min_distance}

@tool
def send_answer(name: str, surname: str, access_level: str, plant_code: str) -> str:
    answer = {
        "name": name,
        "surname": surname,
        "accessLevel": access_level,
        "powerPlant": plant_code
    }
    result = fetch_page("POST",AIDEV_ANSWER_URL, json={"apikey": API_KEY, "task": TASK_NAME, "answer": answer})
    print(result)
    return result

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = EARTH_RADIUS * c
    return distance