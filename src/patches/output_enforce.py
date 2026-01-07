from .base import OutputPatch, PatchLog

class OutputEnforcementPatch(OutputPatch):
    name = "output_enforce"

    def __init__(self, blocklist: list[str], replacement_text: str, max_output_chars: int):
        self.blocklist = [b.lower().strip() for b in blocklist if b.strip()]
        self.replacement_text = replacement_text
        self.max_output_chars = int(max_output_chars)

    def apply(self, prompt: str, output: str):
        original = output or ""
        out = original[: self.max_output_chars]

        hit = None
        low = out.lower()
        for term in self.blocklist:
            if term and term in low:
                hit = term
                break

        if hit:
            return self.replacement_text, PatchLog(self.name, True, "blocked_and_replaced", {"match": hit})

        if out != original:
            return out, PatchLog(self.name, True, "truncated", {"max_output_chars": self.max_output_chars})

        return out, PatchLog(self.name, False, "no_violation")
