# This file defines the OutputEnforcementPatch class, which is an OutputPatch that enforces output constraints

from .base import OutputPatch, PatchLog
class OutputEnforcementPatch(OutputPatch):
    name = "output_enforce"

    def __init__(self, blocklist: list[str], replacement_text: str, max_output_chars: int):
        self.blocklist = [str(b).lower().strip() for b in (blocklist or []) if str(b).strip()]
        self.replacement_text = str(replacement_text or "")
        try:
            self.max_output_chars = int(max_output_chars)
        except Exception:
            self.max_output_chars = 0  # treat as "no truncation" fallback

    def apply(self, prompt, output):
        # normalize types (important: garak / your pipeline may pass odd objects)
        if not isinstance(prompt, str):
            prompt = str(prompt)
        if output is None:
            output = ""
        if not isinstance(output, str):
            output = str(output)

        original = output
        details = {"original_len": len(original)}

        # truncation (only if max_output_chars is positive)
        if self.max_output_chars and self.max_output_chars > 0:
            out = original[: self.max_output_chars]
        else:
            out = original  # no truncation
        details["post_trunc_len"] = len(out) 

        # Check for blocklist terms (case-insensitive on truncated output)
        hit = None
        low = out.lower()
        for term in self.blocklist:
            if term and term in low:
                hit = term
                break

        # enforcement: replace if any hit
        if hit:
            # If output is already replacement text, don't claim triggered
            if out == self.replacement_text:
                return out, PatchLog(
                    patch=self.name, 
                    triggered=False, action="already_replaced", details={"match": hit, **details})
            return self.replacement_text, PatchLog(
                patch=self.name,
                triggered=True,
                action="blocked_and_replaced",
                details={"match": hit, **details},)

        # if truncation changed content, report truncation
        if out != original:
            return out, PatchLog(
                patch=self.name,
                triggered=True,
                action="truncated",
                details={"max_output_chars": self.max_output_chars, **details},
            )
        
        # clean pass-through
        return out, PatchLog(
            patch=self.name,
            triggered=False,
            action="no_violation",
            details=details,
        )