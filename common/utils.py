from requests import request, exceptions

def _fetch(method: str, url: str, parse_json: bool=True, **kwargs) -> dict|None:
    try:
        r = request(method, url, **kwargs)
        r.raise_for_status()
        return (r.json() if parse_json else r.content)
    except exceptions.HTTPError:
        try:
            details = r.json()
        except ValueError:
            details = r.text[:300]
        return {"Error": f"HTTP {r.status_code} from {url}", "Details:": details}
    except exceptions.RequestException as e:
        return {"Error": str(e)}
    
def fetch_page(method: str, url: str, **kwargs) -> list:
    return _fetch(method, url, **kwargs)

def fetch_file(method: str, url: str, **kwargs) -> str:
    return _fetch(method, url, parse_json=False, **kwargs)