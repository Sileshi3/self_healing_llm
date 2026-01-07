import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from ..patches.base import PatchLog

PATCH_LOG_PATH = Path("results") / "patch_audit.jsonl"
PATCH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_patch_event(run_ctx: Dict[str, Any], plog: PatchLog) -> None:
    rec = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "run_id": run_ctx.get("run_id"),
        "target": run_ctx.get("target"),
        "patch": plog.patch,
        "triggered": plog.triggered,
        "action": plog.action,
        "details": plog.details or {},
    }
    with open(PATCH_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=True) + "\n")
