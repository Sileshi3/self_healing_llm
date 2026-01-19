import re
from .base import PromptPatch, PatchLog
import unicodedata

ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")

class InputSanitizePatch(PromptPatch):
    name = "input_sanitize"

    def __init__(self, strip_zero_width: bool, collapse_whitespace: bool,
                  remove_injection_markers: bool, normalize_unicode:bool,
                  strip_control_chars:bool):
        self.strip_zero_width = strip_zero_width
        self.collapse_whitespace = collapse_whitespace
        self.remove_injection_markers = remove_injection_markers
        self.normalize_unicode=normalize_unicode
        self.strip_control_chars=strip_control_chars

    def apply(self, prompt, output=None):
        if not isinstance(prompt, str):
            prompt = str(prompt)
        original = prompt
        actions = []
        
        if self.normalize_unicode: 
            prompt2=unicodedata.normalize('NFKC', prompt)
            if prompt2 != prompt:
                actions.append("univode_normalized")
            prompt = prompt2 

        if self.strip_control_chars:
            prompt2=re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
            if prompt2 != prompt:
                actions.append("stripe_control")
            prompt = prompt2  

        if self.strip_zero_width:
            prompt2 = ZERO_WIDTH_RE.sub("", prompt)
            if prompt2 != prompt:
                actions.append("stripped_zero_width")
            prompt = prompt2

        if self.collapse_whitespace:
            prompt2 = re.sub(r"\s+", " ", prompt).strip()
            if prompt2 != prompt:
                actions.append("collapsed_whitespace")
            prompt = prompt2

        if self.remove_injection_markers:
            prompt2 = prompt.replace("----------", "").replace("IGNORE ANY PREVIOUS", "IGNORE_PREVIOUS")
            if prompt2 != prompt:
                actions.append("mutated_injection_markers")
            prompt = prompt2

        triggered = (prompt != original)
        return prompt, PatchLog(self.name, triggered, " | ".join(actions) if actions else "no_change")
