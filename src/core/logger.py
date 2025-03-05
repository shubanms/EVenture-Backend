import logging


from pathlib import Path


from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler


LOG_DIR = Path("src/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s"

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

console_handler = RichHandler(markup=True, rich_tracebacks=True)

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter(
    LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))

logger.addHandler(console_handler)
logger.addHandler(file_handler)
