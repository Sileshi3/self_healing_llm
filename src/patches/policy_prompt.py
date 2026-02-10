# This file defines the SystemPolicyPromptPatch class, which is a PromptPatch that prepends a system policy  
from .base import PromptPatch, PatchLog

class SystemPolicyPromptPatch(PromptPatch):
    name = "policy_prompt"

    HEADER = "[SYSTEM POLICY]\n"
    USER_TAG = "\n\n[USER]\n"

    def __init__(self, system_policy: str):
        self.system_policy = (system_policy or "").strip()

    def apply(self, prompt: str, output=None):
        if not isinstance(prompt, str):
            prompt = str(prompt)
            
        if not self.system_policy:
            return prompt, PatchLog(
                patch=self.name,
                triggered=False,
                action="no_policy_configured",
                details={}
            )
        
        # If policy already present, don't prepend again
        if prompt.startswith(self.HEADER):
            return prompt, PatchLog(
                patch=self.name,
                triggered=False,
                action="already_has_system_policy",
                details={}
            )
        
        patched = f"{self.HEADER}{self.system_policy}{self.USER_TAG}{prompt}"

        return patched, PatchLog(
            patch=self.name,
            triggered=True,
            action="prepended_system_policy",
            details={"chars_added": len(patched) - len(prompt),
                     "policy_chars": len(self.system_policy),
                    }
        )  
