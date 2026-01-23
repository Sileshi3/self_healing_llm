from typing import List, Any, Tuple
from src.core.config import get_logger
from dataclasses import asdict  
from src.patches.base import PatchLog

logger = get_logger()

class PatchManager:
    def __init__(self, prompt_patches: List, output_patches: List):
        self.prompt_patches = prompt_patches or []
        self.output_patches = output_patches or []

    def _extract_value(self, res: Any) -> Any:
        # Patches may return either the transformed value or a (value, PatchLog) tuple
        if isinstance(res, (tuple, list)) and len(res) > 0:
            return res[0]
        return res

    def apply_prompt_with_logs(self, prompt: str, request_id: str | None = None) -> Tuple[str, list]:
        #Run prompt-side patches in order. Accepts patches that return either a string or a (string, PatchLog) tuple.

        x = prompt
        logs = []
        for p in self.prompt_patches:
            x, log = p.apply(prompt,x)  # patch returns (new_text, patchlog)
            logs.append(log)
        # log patch decision
        logger.info(
            "patches_applied_output",
             extra={
                "request_id": request_id,
                "patches": [asdict(l) if hasattr(l, "__dict__") else str(l) for l in logs],
                "prompt_len": len(prompt) if isinstance(prompt, str) else None,
                "patched_prompt_len": len(x) if isinstance(x, str) else None,
            },

        )
        return x, logs 

    def apply_prompt(self, prompt: str, request_id: str | None = None) -> str:
        patched, _logs = self.apply_prompt_with_logs(prompt, request_id=request_id)
        return patched

    def apply_output_with_logs(self, prompt: str, output: str, request_id: str | None = None) -> Tuple[str, list[PatchLog]]:
        """Run output-side patches in order.
        Patches may implement either:
         - apply(prompt: str, output: str) -> (output, PatchLog)
         - apply(output: str) -> (output, PatchLog)
        I try the two-arg form first if a `prompt` is provided, otherwise fall back to single-arg calls.  
        """
        x = output
        logs: List[PatchLog] = []
        for p in self.output_patches:
            x, log = p.apply(prompt, x)  # (new_output, patchlog)
            logs.append(log) 
        logger.info(
            "patches_applied_output",
                extra={
                    "request_id": request_id,
                    "patches": [asdict(l) for l in logs],
                    "prompt_len": len(prompt) if isinstance(prompt, str) else None,
                    "patched_prompt_len": len(x) if isinstance(x, str) else None,  # <-- must be x
                    },
                )

        
        return x, logs
    
    def apply_output(self, prompt: str, output: str, request_id: str | None = None) -> str:
        patched, _logs = self.apply_output_with_logs(prompt, output, request_id=request_id)
        return patched

# patch_manager = PatchManager(prompt_patches=[], output_patches=[])

 
