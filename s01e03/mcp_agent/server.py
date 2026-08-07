from mcp.server.fastmcp import FastMCP
import logging

from ..config import TASK_NAME, DESTINATION, PACKAGE_URL
from ...common.master_config import API_KEY
from ...common.utils import fetch_page

mcp = FastMCP(f"{TASK_NAME}")
logging.getLogger("mcp.server").setLevel(logging.WARNING)

@mcp.tool(structured_output=False)
def check_package(packageid:str) -> dict:
    """Sprawdza status i aktualną lokalizację paczki na podstawie jej ID."""
    package_info = fetch_page("POST", PACKAGE_URL, json={"apikey": API_KEY, "action": "check", "packageid": packageid} )
    return package_info

@mcp.tool(structured_output=False)
def redirect_package(packageid:str, code:str) -> dict:
    """Przekierowuje paczkę do nowego miejsca docelowego. Wymaga kodu zabezpieczającego."""
    confirmation = fetch_page("POST", PACKAGE_URL, json={"apikey": API_KEY, "action": "redirect", "packageid": packageid, "destination": DESTINATION, "code": code})
    return confirmation

if __name__ == "__main__":
    logging.info("Starting MCP Server...")
    mcp.run(transport="stdio")