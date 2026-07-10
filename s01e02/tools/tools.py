tools = [
  {
        "type": "function",
        "name": "search_location_coordinates",
        "description": 'Search for GPS coordinates of a location using Nominatim (OpenStreetMap). Use for geocoding power plant cities.',
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": 'City, e.g. "Zabrze", "Opole" or "Katowice"',
                },
            },
            "required": ['location'],
            "additionalProperties": False
        },
        "strict": True
    },
  {
        "type": "function",
        "name": "get_min_distance_to_plant",
        "description": 'Given a power plant GPS position and ALL locations of one suspect, returns the minimum distance (km) between that suspect and the plant. Pass suspect name/surname so the result is labelled — do not rely on memory to track which suspect these locations belong to.',
        "parameters": {
            "type": "object",
            "properties": {
                "name": { "type": 'string', "description": 'First name of the suspect whose locations you are checking' },
                "surname": { "type": 'string', "description": 'Last name of the suspect whose locations you are checking' },
                "plant_code": { "type": 'string', "description": 'Code of the power plant, e.g. PWR3847PL' },
                "plant_lat": { "type": 'number', "description": 'Latitude of the power plant' },
                "plant_lon": { "type": 'number', "description": 'Longitude of the power plant' },
                "suspect_locations": {
                    "type": 'array',
                    "description": 'Array of {latitude, longitude} objects as passed in the user message',
                    "items": {
                    "type": 'object',
                    "properties": {
                        "latitude": { "type": 'number' },
                        "longitude": { "type": 'number' },
                    },
                    "required": ['latitude', 'longitude'],
                    "additionalProperties": False
                    },
                },
            },
            "required": ['name', 'surname', 'plant_code', 'plant_lat', 'plant_lon', 'suspect_locations'],
            "additionalProperties": False
        },
        "strict": True
    },
  {
        "type": "function",
        "name": "get_suspect_access_level",
        "description": 'Given a suspect name, surname and birth year, returns the access level of that suspect.',
        "parameters": {
            "type": "object",
            "properties": {
                "name": { "type": 'string', "description": 'First name of the suspect whose locations you are checking' },
                "surname": { "type": 'string', "description": 'Last name of the suspect whose locations you are checking' },
                "born": { "type": 'number', "description": 'Birth year of the suspect whose locations you are checking' },
            },
            "required": ['name', 'surname', 'born'],
             "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "send_answer",
        "description": "Send the final answer to the AIDEV hub for verification.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": { "type": 'string', "description": 'First name of the suspect whose locations you are checking' },
                "surname": { "type": 'string', "description": 'Last name of the suspect whose locations you are checking' },
                "access_level": { "type": 'number', "description": 'Access level of the suspect, e.g. 3' },
                "plant_code": { "type": 'string', "description": 'Code of the power plant, e.g. PWR3847PL' },
            },
            "required": ['name', 'surname', 'access_level', 'plant_code'],
            "additionalProperties": False
        },
        "strict": True
    },
]