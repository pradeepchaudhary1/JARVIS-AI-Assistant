import license_manager
from brain.tier_gate import TierGate
from brain.orchestrator import Brain


def test_tier_gate_basic_blocks_professional_intent(monkeypatch):
    monkeypatch.setattr(license_manager, "read_license_data", lambda: ("user@example.com", "basic"))
    gate = TierGate()
    assert gate.current_tier == "basic"
    assert gate.is_allowed("open_app") is True
    assert gate.is_allowed("web_search") is False


def test_tier_gate_never_blocks_general_conversation(monkeypatch):
    monkeypatch.setattr(license_manager, "read_license_data", lambda: ("user@example.com", "basic"))
    gate = TierGate()
    assert gate.is_allowed("unknown") is True
    assert gate.is_allowed("time") is True


def test_brain_blocks_web_search_on_basic_tier(monkeypatch):
    monkeypatch.setattr(license_manager, "read_license_data", lambda: ("user@example.com", "basic"))
    brain = Brain()
    result = brain.process("search youtube lofi music")

    assert result.get("status") == "tier_blocked"
    assert "upgrade" in result.get("assistant_reply", "").lower()

    print("✅ Tier gate blocks Professional-only feature on Basic tier")


def test_brain_allows_open_app_on_basic_tier(monkeypatch):
    monkeypatch.setattr(license_manager, "read_license_data", lambda: ("user@example.com", "basic"))
    brain = Brain()
    result = brain.process("open chrome")

    assert result.get("status") == "success"

    print("✅ Basic tier allows its own features normally")


if __name__ == "__main__":
    test_tier_gate_basic_blocks_professional_intent()
    test_tier_gate_never_blocks_general_conversation()
    test_brain_blocks_web_search_on_basic_tier()
    test_brain_allows_open_app_on_basic_tier()
    print("\n✅ ALL PHASE 2.6a TESTS PASSED")