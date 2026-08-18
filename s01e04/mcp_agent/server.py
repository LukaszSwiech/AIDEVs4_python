import logging
from mcp.server.fastmcp import FastMCP
from typing import Annotated
from pydantic import Field
from openai import BadRequestError, APIError

from ...common.logs import setup_logging
from ..config import TASK_NAME
from ...common.master_config import API_KEY, AIDEV_ANSWER_URL
from ...common.utils import fetch_file, fetch_page
from ...common.ai import chat

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

    if not is_fetch_error(result):
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
async def understand_image(
    image_url: Annotated[
        str,
        Field(
            description=(
                "Complete URL address of the image file to analyze. "
                "This is not a local filesystem path. If the documentation only "
                "mentions a filename (not a full URL), construct the URL yourself: "
                "take the directory portion of the documentation URL you fetched "
                "it from and append that filename to it."
            )
        ),
    ],
    question: Annotated[
        str,
        Field(
            description=(
                "Question to ask about the image. If you don't know in advance "
                "what the image contains, start generic (e.g. 'Describe everything "
                "visible in this image in as much detail as possible'). If the image "
                "turns out to contain a table, list, diagram, map or any other "
                "structured/textual data, explicitly ask for a full transcription of "
                "every entry (all rows, labels, codes, numbers) rather than a "
                "summary - a summary may omit values you need later."
            )
        ),
    ],
) -> str:
    """
    Analyze an image and answer questions about it. Use this to identify people, objects, scenes, or any visual content in images.
    """
    desc_image_content = [{
        "role": "user",
        "content": [
            { "type": "input_image", "image_url": image_url },
            { "type": "input_text", "text": question }
        ]

    }]

    try:
        describe_image = await chat(desc_image_content)
    except BadRequestError as e:
        return {
            "status": "error",
            "data": str(e),
            "recovery_hints": [
                "The request itself was rejected as malformed - retrying unchanged will fail identically.",
                "Check that image_url is a real, reachable URL (not a local path) and points to an actual image file.",
            ]
        }
    except APIError as e:
        return {
            "status": "error",
            "data": str(e),
            "recovery_hints": [
                "This looks like a transient problem with the vision service (rate limit, timeout, or server error), not bad input.",
                "Retry this same call once. If it fails again, assume the service is not responding right now.",
            ]
        }

    return {
        "status": "ok",
        "data": describe_image.output_text,
        "hints": [
            "Treat this as part of the documentation content, not just a description - if it contains a table, codes, route data or other structured values, use them exactly as transcribed when filling in the declaration, do not paraphrase or round them.",
            "If this text looks incomplete or vague for what you expected from this image, call this tool again on the same image_url with a more specific question rather than assuming the image had no relevant data.",
        ]
    }

@mcp.tool(structured_output=False)
def send_answer(
    answer_declaration: Annotated[
        str,
        Field(
            description=(
                "The complete, final text of the filled-out shipment declaration - "
                "this IS the solution to the task, not a summary or explanation of it. "
                "It must match the template found in the documentation exactly: same "
                "field order, same labels, same separators and formatting as the "
                "example. This text is sent verbatim as the 'answer' field in the "
                "request to the Hub's /verify endpoint, so it must contain nothing "
                "else - no commentary, no markdown, no extra notes before or after "
                "the declaration itself."
            )
        ),
    ],
) -> dict:
    """
    Send the final declaration to the Hub for verification and, if accepted, receive the flag.
    """
    result = fetch_page("POST",AIDEV_ANSWER_URL, json={"apikey": API_KEY, "task": TASK_NAME, "answer": {"declaration": answer_declaration},})

    if "Error" not in result:
        return {
            "status": "ok",
            "data": result,
            "hint": "The declaration was accepted. Look for a 'flag' field in this response and return it as your final answer."
        }
    
    details = result.get("Details")
    api_code = details.get("code") if isinstance(details, dict) else None
    error_description = details.get("description") if isinstance(details, dict) else None

    if api_code == -21:
        return {
            "status": "rejected",
            "sent_answer": answer_declaration,
            "hub_error": error_description or details,
            "recovery_hints": [
                "Read the message returned by the Hub carefully - it usually names which field or rule caused the rejection.",
                "Do not resend the exact same declaration text unchanged - it will be rejected again for the same reason.",
                "Re-check every field of the declaration one by one against the template and rules found in the documentation: field order, labels, separators and formatting must match exactly.",
                "Pay special attention to fields that require deriving or calculating a value rather than copying it verbatim - the route code, the fee/payment category, and the weight format are the most common sources of mistakes.",
                "If the Hub's message does not point to a specific field, re-read the documentation instead of guessing - you may have missed a rule or a file.",
            ]
        }
    
    return {
        "status": "error",
        "data": result,
        "recovery_hints": [
            "This is a failure of the hub system, not bad data.",
            "Retry this same call once. If it fails again, assume that server is not responding right now.",
        ],
    }

def is_fetch_error(result: bytes | dict) -> bool:
    return isinstance(result, dict)

if __name__ == "__main__":
    logging.info("Starting MCP Server...")
    mcp.run(transport="stdio")
