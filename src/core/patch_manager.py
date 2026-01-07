from __future__ import annotations
from typing import List  
from ..patches.base import PromptPatch, OutputPatch
from dataclasses import dataclass

# @dataclass
# class PatchManager:
#     prompt_patches: List[PromptPatch]
#     output_patches: List[OutputPatch]

#     #Run all prompt-side patches in order.
#     def apply_prompt_patches(self, prompt: str) -> str:
#         out=prompt
#         for p in self.prompt_patches:
#             # Each patch should implement .apply(text: str) -> str
#             out = p.apply(out)
#             # log_patch_event(run_ctx, plog)
#         return out

#     #Run all output-side patches in order
#     def apply_output(self, text: str) -> str:
#         out=text
#         for p in self.output_patches:
#             out = p.apply(out)
#         return out

  
from typing import List

class PatchManager:
    def __init__(self, prompt_patches: List, output_patches: List):
        self.prompt_patches = prompt_patches or []
        self.output_patches = output_patches or []

    def apply_prompt(self, prompt: str) -> str:
        x = prompt
        for p in self.prompt_patches:
            # common conventions: p.apply(x) or p.patch(x)
            if hasattr(p, "apply"):
                x = p.apply(x)
            elif hasattr(p, "patch"):
                x = p.patch(x)
            else:
                raise AttributeError(f"{p.__class__.__name__} has no apply()/patch()")
        return x

    def apply_output(self, text: str) -> str:
        x = text
        for p in self.output_patches:
            if hasattr(p, "apply"):
                x = p.apply(x)
            elif hasattr(p, "patch"):
                x = p.patch(x)
            else:
                raise AttributeError(f"{p.__class__.__name__} has no apply()/patch()")
        return x
