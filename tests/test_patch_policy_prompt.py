from src.patches.policy_prompt import SystemPolicyPromptPatch

def test_policy_prompt_disabled_when_empty():
    p = SystemPolicyPromptPatch(system_policy="")
    out, log = p.apply("hi")
    assert out == "hi"
    assert log.triggered is False
    assert log.action == "no_policy_configured"

def test_policy_prompt_prepends_policy():
    p = SystemPolicyPromptPatch(system_policy="RULES")
    out, log = p.apply("hi")
    assert out.startswith("[SYSTEM POLICY]\nRULES")
    assert "[USER]\nhi" in out
    assert log.triggered is True
    assert log.action == "prepended_system_policy"
    assert "chars_added" in log.details
