TAGS_SCHEMA = {
            "format": {
                "type": "json_schema",
                "name": "tags",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["tags"],
                    "additionalProperties": False
                }
            }
        }