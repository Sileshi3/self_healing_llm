import re
from .base import PromptPatch, PatchLog

ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")

class InputSanitizePatch(PromptPatch):
    name = "input_sanitize"

    def __init__(self, strip_zero_width: bool, collapse_whitespace: bool, remove_injection_markers: bool):
        self.strip_zero_width = strip_zero_width
        self.collapse_whitespace = collapse_whitespace
        self.remove_injection_markers = remove_injection_markers

    # def apply(self, prompt):
    def apply(self, prompt: str, output: str):
        if not isinstance(prompt, str):
            prompt = str(prompt)
        original = prompt
        actions = []
        details = {}

        # 1. Zero-width (invisible payloads)
        if self.strip_zero_width:
            prompt2 = ZERO_WIDTH_RE.sub("", prompt)
            if prompt2 != prompt:
                actions.append("stripped_zero_width")
                details["zero_width_removed_chars"] = len(prompt) - len(prompt2)
            prompt = prompt2

        # 2. Excessive whitespace normalization
        if self.collapse_whitespace:
            prompt2 = re.sub(r"\s+", " ", prompt).strip()
            if prompt2 != prompt:
                actions.append("collapsed_whitespace")
                details["whitespace_normalized"] = True
            prompt = prompt2

        # 3. Remove common prompt injection markers such as "----------" or "IGNORE ANY PREVIOUS INSTRUCTIONS"
        if self.remove_injection_markers: 
            prompt2 = prompt.replace("----------", "").replace("IGNORE ANY PREVIOUS", "IGNORE_PREVIOUS")
            if prompt2 != prompt:
                actions.append("mutated_injection_markers")
                details["injection_markers_mutated"] = True
            prompt = prompt2

        triggered = (prompt != original)

        # One clean action string + details if no changes
        actions="|".join(actions) if actions else "no_change"

        return prompt, PatchLog(
            patch=self.name,
            triggered=triggered,
            action=actions,
            details=details
        ) 

