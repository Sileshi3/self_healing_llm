from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class PatchLog:
    patch: str
    triggered: bool
    action: str
    details: Optional[Dict[str, Any]] = None

class PromptPatch:
    name: str = "prompt_patch"

    def apply(self, prompt: str) -> tuple[str, PatchLog]:
        raise NotImplementedError

class OutputPatch:
    name: str = "output_patch"

    def apply(self, prompt: str, output: str) -> tuple[str, PatchLog]:
        raise NotImplementedError
