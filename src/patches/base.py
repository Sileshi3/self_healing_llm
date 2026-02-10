# This file defines the base classes and data structures for the patching system,
# including the PatchLog, PromptPatch, and OutputPatch classes.
 
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class PatchLog:
    patch: str
    triggered: bool
    action: str 
    details: Dict[str, Any] = field(default_factory=dict)

class PromptPatch:
    name: str = "prompt_patch"

    def apply(self, prompt: str, output=None) -> tuple[str, PatchLog]:
        raise NotImplementedError

class OutputPatch:
    name: str = "output_patch"

    def apply(self, prompt: str, output: str) -> tuple[str, PatchLog]:
        raise NotImplementedError