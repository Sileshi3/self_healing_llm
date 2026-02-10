# This file defines the build_patch_manager function, which constructs a PatchManager 
# instance based on the provided configuration and ablation settings. 
from src.core.patch_manager import PatchManager
from src.patches.policy_prompt import SystemPolicyPromptPatch
from src.patches.input_sanitize import InputSanitizePatch
from src.patches.output_enforce import OutputEnforcementPatch

def build_patch_manager(cfg,ablation_cfg) -> PatchManager:  
    
    cfg=cfg or {}
    ablation_cfg=ablation_cfg or {}

    settings=ablation_cfg.get("ablation_setting") or {}
    patches=cfg.get("patches_settings") or {}

    p1cfg_setting = settings.get("policy_prompt") or patches.get("prompt_policy") or {}
    p2cfg_setting = settings.get("input_sanitize") or {}
    p3cfg_setting = settings.get("output_enforce") or {}

    # prefer explicit 'patches' keys, fall back to 'patches_settings'
    p1cfg = patches.get("policy_prompt") or patches.get("prompt_policy") or {}
    p2cfg = patches.get("input_sanitize") or {}
    p3cfg = patches.get("output_enforce") or {}

    prompt_patches = []
    output_patches = []

    if p1cfg_setting.get("enabled"):

        prompt_patches.append(SystemPolicyPromptPatch(p1cfg.get("system_policy", "")))

    if p2cfg_setting.get("enabled"):
        prompt_patches.append(
            InputSanitizePatch(
                strip_zero_width=p2cfg.get("strip_zero_width", True),
                collapse_whitespace=p2cfg.get("collapse_whitespace", True),
                remove_injection_markers=p2cfg.get("remove_injection_markers", True),
                strip_control_chars=p2cfg.get("strip_control_chars", True),
                normalize_unicode=p2cfg.get("normalize_unicode", True)
            )
        )

    if p3cfg_setting.get("enabled"):
        output_patches.append(
            OutputEnforcementPatch(
                blocklist=p3cfg.get("blocklist", []),
                replacement_text=p3cfg.get("replacement_text", "I can’t help with that."),
                max_output_chars=p3cfg.get("max_output_chars", 4000),
            )
        )

    return PatchManager(prompt_patches, output_patches)
