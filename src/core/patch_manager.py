from __future__ import annotations 
# from ..patches.base import PromptPatch, OutputPatch
# from dataclasses import dataclass

from typing import List, Optional, Any
# import inspect

class PatchManager:
    def __init__(self, prompt_patches: List, output_patches: List):
        self.prompt_patches = prompt_patches or []
        self.output_patches = output_patches or []

    def _extract_value(self, res: Any) -> Any:
        # Patches may return either the transformed value or a (value, PatchLog) tuple
        if isinstance(res, (tuple, list)) and len(res) > 0:
            return res[0]
        return res

    def apply_prompt(self, prompt: str) -> str:
        #Run prompt-side patches in order. Accepts patches that return either a string or a (string, PatchLog) tuple.

        x = prompt
        for p in self.prompt_patches:
            if hasattr(p, "apply"):
                try:
                    res = p.apply(x)
                except TypeError:
                    # fallback to patch()
                    if hasattr(p, "patch"):
                        res = p.patch(x)
                    else:
                        raise
            elif hasattr(p, "patch"):
                res = p.patch(x)
            else:
                raise AttributeError(f"{p.__class__.__name__} has no apply()/patch()")

            x = self._extract_value(res)

        return x

    def apply_output(self, output: str, prompt: Optional[str] = None) -> str:
        """Run output-side patches in order.

        Patches may implement either:
         - apply(prompt: str, output: str) -> (output, PatchLog)
         - apply(output: str) -> (output, PatchLog)

        I try the two-arg form first if a `prompt` is provided, otherwise fall
        back to single-arg calls.  
        """
        x = output
        for p in self.output_patches:
            res = None
            # prefer two-arg form when prompt is available
            if prompt is not None:
                try:
                    res = p.apply(prompt, x)
                except TypeError:
                    res = None

            if res is None:
                if hasattr(p, "apply"):
                    try:
                        res = p.apply(x)
                    except TypeError:
                        # try patch() if present
                        if hasattr(p, "patch"):
                            res = p.patch(x)
                        else:
                            raise
                elif hasattr(p, "patch"):
                    res = p.patch(x)
                else:
                    raise AttributeError(f"{p.__class__.__name__} has no apply()/patch()")

            x = self._extract_value(res)

        return x
