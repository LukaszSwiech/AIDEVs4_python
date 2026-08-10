import logging
from rich.console import Console
from rich.logging import RichHandler

LEVEL_STYLES = {
    logging.DEBUG: "dim cyan",
    logging.INFO: "white",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "bold white on red",
}

QUIET_LOGGERS = ("httpx", "httpcore", "mcp.server", "openai", "urllib3")

class LevelColorHandler(RichHandler):
    def render_message(self, record: logging.LogRecord, message: str):
        text = super().render_message(record, message)
        text.style = LEVEL_STYLES.get(record.levelno, "white")
        return text

def setup_logging(level: int = logging.INFO, quiet: tuple[str, ...] = QUIET_LOGGERS) -> None:
    handler = LevelColorHandler(
        console=Console(stderr=True),
        rich_tracebacks=True,
        show_path=False,
    )
    logging.basicConfig(level=level, format="%(message)s", handlers=[handler], force=True)
    for name in quiet:
        logging.getLogger(name).setLevel(logging.WARNING)
