import contextvars
import logging
import sys
from datetime import datetime
from pathlib import Path

# Creating a variable which can be provides
nodeId = contextvars.ContextVar("node_id", default="0")


def setNodeId(node_id: str) -> None:
    nodeId.set(node_id)


def getNodeId() -> str:
    return nodeId.get()


class NodeIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.node_id = getNodeId()
        return True


logger = logging.getLogger("Bitcoin")
logger.setLevel(logging.INFO)

formatting = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - Node=%(node_id)s - %(message)s"
)

# NOTE : Note you can add handlers from your own side
# CONSOLE HANDLER
# NOTE : Right Now I am commenting this, you can uncomment it according to your own needs

# consoleHandler = logging.StreamHandler(sys.stdout)
# consoleHandler.setLevel(logging.INFO)
# consoleHandler.setFormatter(formatting)

# FILE HANDLER
# NOTE:
logDir = Path("logs")
logDir.mkdir(exist_ok=True)
ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logFile = logDir / f"Bitcoin_{ts}.log"

fileHandler = logging.FileHandler(logFile, mode="w", encoding="utf-8")
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatting)
# FORMAT

# Attaching various handlers to logging handlers
# logger.addHandler(consoleHandler)
logger.addHandler(fileHandler)
logger.addFilter(NodeIdFilter())
