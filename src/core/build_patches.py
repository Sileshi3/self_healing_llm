 
from src.core.patch_manager import PatchManager
from src.patches.policy_prompt import SystemPolicyPromptPatch
from src.patches.input_sanitize import InputSanitizePatch
from src.patches.output_enforce import OutputEnforcementPatch

def build_patch_manager(cfg) -> PatchManager:
    p1cfg = cfg["patches"]["policy_prompt"]
    p2cfg = cfg["patches"]["input_sanitize"]
    p3cfg = cfg["patches"]["output_enforce"]

    prompt_patches = []
    output_patches = []

    if p1cfg.get("enabled"):
        prompt_patches.append(SystemPolicyPromptPatch(p1cfg.get("system_policy", "")))

    if p2cfg.get("enabled"):
        prompt_patches.append(InputSanitizePatch(
            strip_zero_width=p2cfg.get("strip_zero_width", True),
            collapse_whitespace=p2cfg.get("collapse_whitespace", True),
            remove_injection_markers=p2cfg.get("remove_injection_markers", True),
        ))

    if p3cfg.get("enabled"):
        output_patches.append(OutputEnforcementPatch(
            blocklist=p3cfg.get("blocklist", []),
            replacement_text=p3cfg.get("replacement_text", "I can’t help with that."),
            max_output_chars=p3cfg.get("max_output_chars", 4000),
        ))

    return PatchManager(prompt_patches, output_patches)
