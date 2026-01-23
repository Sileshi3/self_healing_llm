import yaml
import json
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import Any, Dict

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Attach extra structured fields (if any)
        for k, v in getattr(record, "__dict__", {}).items():
            if k.startswith("_"):
                continue
            if k in ("args", "msg", "name", "levelname", "levelno", "pathname",
                     "filename", "module", "exc_info", "exc_text", "stack_info",
                     "lineno", "funcName", "created", "msecs", "relativeCreated",
                     "thread", "threadName", "processName", "process"):
                continue
            # Keep JSON-safe values; stringify anything complex
            try:
                json.dumps(v)
                base[k] = v
            except TypeError:
                base[k] = str(v)

        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(base, ensure_ascii=False)


def get_logger(name: str = "self_healing_llm") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(JsonFormatter())
    logger.addHandler(sh)

    # File rotation
    log_dir = os.getenv("APP_LOG_DIR", "/app/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.jsonl")

    fh = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    logger.addHandler(fh)

    logger.propagate = False
    return logger


def load_config(path:str):
    with open(path,"r",encoding="utf-8") as f:
        return yaml.safe_load(f) or {} 

def load_config_json(path:str):
    with open(path, "r", encoding="utf-8") as f:
         return json.load(f)