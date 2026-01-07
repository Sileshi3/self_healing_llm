from src.patches.policy_prompt import SystemPolicyPromptPatch
from src.patches.input_sanitize import InputSanitizePatch
from src.patches.output_enforce import OutputEnforcementPatch

def test_policy_prompt_prepends():
    p = SystemPolicyPromptPatch("DO NOT DO BAD THINGS")
    out, log = p.apply("hello")
    assert "SYSTEM POLICY" in out
    assert log.triggered is True

def test_input_sanitize_zero_width():
    p = InputSanitizePatch(True, True, False)
    out, log = p.apply("hi\u200b there")
    assert out == "hi there"
    assert log.triggered is True

def test_output_enforce_blocklist():
    p = OutputEnforcementPatch(["i hate humans"], "REFUSE", 1000)
    out, log = p.apply("x", "I hate humans!!!")
    assert out == "REFUSE"
    assert log.triggered is True
    assert log.action == "blocked_and_replaced"
