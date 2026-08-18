from mcp.server.fastmcp import FastMCP
import logging
from typing import Annotated
from pydantic import Field

from ...common.logs import setup_logging
from ..config import TASK_NAME
from ...common.master_config import API_KEY, AIDEV_ANSWER_URL
from ...common.utils import fetch_file

mcp = FastMCP(f"{TASK_NAME}")
setup_logging()

@mcp.tool(structured_output=False)
def fetch_documentation(
    docu_url: Annotated[str, Field(description="Complete URL address of the *.txt or *.md file to download")]
) -> dict:
    """
    Downloads a text file (markdown/txt) from the provided URL and returns its content as text.
    """
    result = fetch_file("GET", docu_url)

    if "Error" not in result:
        return {
            "status": "ok",
            "data": result.decode("utf-8"),
            "hints":  [
                 "If this text contains an include-style directive that names another file (e.g. referencing 'zalacznik-A.md'), that is not a link to open literally - build the next URL yourself by taking the directory of the URL you just fetched and appending the referenced filename to it."
            ]
        }

    error_description = result.get("Error")
    if ' 404 ' in  error_description:
        return {
            "status": "not_found",
            "data": result,
            "recovery_hints": [
                "The URL does not exist on the server. This usually happens when a filename mentioned in the document text (e.g. from an include directive) was treated as a link to open directly, instead of being combined with the directory of the document you were already reading.",
                "Take the directory portion of the URL that last worked and append only the referenced filename - do not invent a different path or wording like 'open link'.",
                "Do not repeat the exact same URL - it will fail identically. Correct the URL before calling this tool again.",
            ]
        }

    return {
        "status": "error",
        "data": result,
        "recovery_hints": [
            "This is not a 404, so the URL itself is likely fine - this looks like a transient problem with the hub server.",
            "Retry this same call once. If it fails again, assume that server is not responding right now.",
        ]
    }

@mcp.tool(structured_output=False)
def understand_image(
    image_url: Annotated[str, Field(description="Path to the image file relative to the project root (e.g., 'images/photo.jpg')")],
    question: Annotated[str, Field(description="Question to ask about the image (e.g., 'Who is in this image?', 'Describe the person's appearance')")]
) -> dict:
    """
    Analyze an image and answer questions about it. Use this to identify people, objects, scenes, or any visual content in images.
    """
    image_description = fetch_page("GET", image_url)
    question = "TO DO. paste the downloaded img to vision model and add question"
    return image_description

@mcp.tool(structured_output=False)
def understand_file(
    file_name: Annotated[str, Field(description="TO_DO")]
) -> dict:
    """
    "TO_DO"
    """
    file = open(file_name, 'r')

    file = fetch_page("GET", file_name)
    return file

@mcp.tool(structured_output=False)
def send_answer(
    answer: Annotated[str, Field(description="TO_DO")],

) -> dict:
    """
    "TO_DO"
    """
    result = fetch_page("POST",AIDEV_ANSWER_URL, json={"apikey": API_KEY, "task": TASK_NAME, "answer": answer})
    logging.info(result)
    return result

if __name__ == "__main__":
    logging.info("Starting MCP Server...")
    mcp.run(transport="stdio")
