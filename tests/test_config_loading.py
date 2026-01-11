# import pytest
# from src.core.patch_manager import PatchManager
# from src.core.build_patches import build_patch_manager  # <-- change if your module is different


# def test_build_patch_manager_enables_expected_patches():
#     cfg = {
#         "patches_settings": {
#             "policy_prompt": {
#                 "enabled": True,
#                 "system_policy": "SAFE"
#             },
#             "input_sanitize": {
#                 "enabled": True,
#                 "strip_zero_width": True,
#                 "collapse_whitespace": True,
#                 "remove_injection_markers": True
#             },
#             "output_enforce": {
#                 "enabled": True,
#                 "blocklist": ["bomb"],
#                 "replacement_text": "BLOCKED",
#                 "max_output_chars": 4000
#             }
#         }
#     }

#     pm = build_patch_manager(cfg)
#     assert isinstance(pm, PatchManager)

#     # ensure patch names are loaded
#     prompt_names = [p.name for p in pm.prompt_patches]
#     output_names = [p.name for p in pm.output_patches]

#     assert "policy_prompt" in prompt_names
#     assert "input_sanitize" in prompt_names
#     assert "output_enforce" in output_names


# def test_build_patch_manager_respects_enabled_false():
#     cfg = {
#         "patches_settings": {
#             "policy_prompt": {"enabled": False, "system_policy": "SAFE"},
#             "input_sanitize": {"enabled": True, "strip_zero_width": True, "collapse_whitespace": True, "remove_injection_markers": True},
#             "output_enforce": {"enabled": False, "blocklist": ["bomb"], "replacement_text": "BLOCKED", "max_output_chars": 10}
#         }
#     }

#     pm = build_patch_manager(cfg)
#     prompt_names = [p.name for p in pm.prompt_patches]
#     output_names = [p.name for p in pm.output_patches]

#     assert "policy_prompt" not in prompt_names
#     assert "input_sanitize" in prompt_names
#     assert "output_enforce" not in output_names


# def test_build_patch_manager_defaults_do_not_crash():
#     # minimal config: should not crash; should build with empty lists or defaults
#     cfg = {"patches_settings": {}}
#     pm = build_patch_manager(cfg)
#     assert isinstance(pm, PatchManager)
import yaml
from src.core.build_patches import build_patch_manager  # adjust import to your project

def test_build_patch_manager_from_yaml(tmp_path):
    cfg_text = """
patches_settings:
  policy_prompt:
    enabled: true
    system_policy: "RULES"
  input_sanitize:
    enabled: true
    strip_zero_width: true
    collapse_whitespace: true
    remove_injection_markers: true
  output_enforce:
    enabled: true
    blocklist: ["bomb"]
    replacement_text: "BLOCKED"
    max_output_chars: 100
"""
    cfg = yaml.safe_load(cfg_text)
    pm = build_patch_manager(cfg)

    assert pm is not None
    assert len(pm.prompt_patches) == 2
    assert len(pm.output_patches) == 1

    assert pm.prompt_patches[0].name == "policy_prompt"
    assert pm.prompt_patches[1].name == "input_sanitize"
    assert pm.output_patches[0].name == "output_enforce"
