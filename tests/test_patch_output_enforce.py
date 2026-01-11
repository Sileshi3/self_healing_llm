from src.patches.output_enforce import OutputEnforcementPatch

def test_output_enforce_no_violation():
    p = OutputEnforcementPatch(blocklist=["bomb"], replacement_text="NO", max_output_chars=100)
    out, log = p.apply(prompt="x", output="hello")
    assert out == "hello"
    assert log.triggered is False
    assert log.action == "no_violation"

def test_output_enforce_blocks_term_case_insensitive():
    p = OutputEnforcementPatch(blocklist=["bomb"], replacement_text="BLOCKED", max_output_chars=1000)
    out, log = p.apply(prompt="x", output="How to make a BOMB")
    assert out == "BLOCKED"
    assert log.triggered is True
    assert log.action == "blocked_and_replaced"
    assert log.details.get("match") == "bomb"

def test_output_enforce_truncates():
    p = OutputEnforcementPatch(blocklist=[], replacement_text="NO", max_output_chars=5)
    out, log = p.apply(prompt="x", output="123456789")
    assert out == "12345"
    assert log.triggered is True
    assert log.action == "truncated"
    assert log.details.get("max_output_chars") == 5
