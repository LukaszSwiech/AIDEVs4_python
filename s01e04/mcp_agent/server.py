from mcp.server.fastmcp import FastMCP
import logging
from typing import Annotated
from pydantic import Field

from ...common.logs import setup_logging
from ..config import TASK_NAME, OUTPUT_PATH
from ...common.master_config import API_KEY, AIDEV_ANSWER_URL
from ...common.utils import fetch_page

mcp = FastMCP(f"{TASK_NAME}")
setup_logging()

@mcp.tool(structured_output=False)
def fetch_documentation(
    docu_url: Annotated[str, Field(description="URL to a *.md file which should be fetched")]
) -> dict:
    """
    """
    try:
        documentation = fetch_page("GET", docu_url)
    except:
        "ups, it didn't work"
    return "Successfully saved the file in the /output directory"

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
