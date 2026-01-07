from .base import PromptPatch, PatchLog

class SystemPolicyPromptPatch(PromptPatch):
    name = "policy_prompt"

    def __init__(self, system_policy: str):
        self.system_policy = system_policy.strip()

    def apply(self, prompt: str):
        if not self.system_policy:
            return prompt, PatchLog(self.name, False, "no_policy_configured")

        patched = f"[SYSTEM POLICY]\n{self.system_policy}\n\n[USER]\n{prompt}"
        return patched, PatchLog(self.name, True, "prepended_system_policy", {"chars_added": len(patched) - len(prompt)})
