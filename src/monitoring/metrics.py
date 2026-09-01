import logging
import json
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitoring")


def log_request(method: str, path: str, status_code: int, duration: float):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "status": status_code,
        "duration_ms": duration * 1000,
    }
    logger.info(json.dumps(log_entry))
