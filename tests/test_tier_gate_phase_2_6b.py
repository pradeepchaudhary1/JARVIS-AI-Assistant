from pathlib import Path

import brain.orchestrator as orchestrator
import license_manager
from brain.tier_gate import TierGate


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_license(email: str, tier: str):
    (REPO_ROOT / ".jarvis_license").write_text(f"{email}\n{tier}\n", encoding="utf-8")


def test_license_tier_is_loaded_from_license_file(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    _write_license("user@example.com", "professional")
    gate = TierGate()
    assert gate.current_tier == "professional"


def test_missing_or_invalid_tier_defaults_to_basic(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    _write_license("user@example.com", "unknown")
    gate = TierGate()
    assert gate.current_tier == "basic"

    (REPO_ROOT / ".jarvis_license").unlink(missing_ok=True)
    gate = TierGate()
    assert gate.current_tier == "basic"


def test_basic_dangerous_command_is_tier_blocked(monkeypatch):
    brain = orchestrator.Brain()
    brain.tier_gate.current_tier = "basic"
    result = brain.process("shutdown computer")
    assert result.get("status") == "tier_blocked"
    assert result.get("assistant_reply") == "Sir, this command isn't available on your current plan."


def test_professional_dangerous_command_uses_confirmation_flow(monkeypatch):
    brain = orchestrator.Brain()
    brain.tier_gate.current_tier = "professional"
    result = brain.process("shutdown computer")
    assert result.get("status") == "confirmation_required"
    assert "potentially dangerous command" in result.get("assistant_reply", "").lower()


def test_basic_command_limit_is_enforced(monkeypatch):
    brain = orchestrator.Brain()
    brain.tier_gate.current_tier = "basic"

    class DummyBackend:
        def __init__(self):
            self.count = 0

        def increment_daily_usage(self, email: str):
            self.count += 1
            return self.count

    backend = DummyBackend()
    monkeypatch.setattr(orchestrator, "get_memory_backend", lambda: backend)
    monkeypatch.setattr(license_manager, "read_license_data", lambda: ("user@example.com", "basic"))

    for _ in range(50):
        assert brain._check_daily_limit() is None

    result = brain._check_daily_limit()
    assert result["status"] == "limit_reached"
    assert result["assistant_reply"] == "Sir, aaj ki command limit khatam ho gayi."


def test_pro_and_lifetime_are_unlimited(monkeypatch):
    for tier in ("pro", "lifetime"):
        brain = orchestrator.Brain()
        brain.tier_gate.current_tier = tier

        class DummyBackend:
            def increment_daily_usage(self, email: str):
                return 9999

        monkeypatch.setattr(orchestrator, "get_memory_backend", lambda: DummyBackend())
        monkeypatch.setattr(license_manager, "read_license_data", lambda: ("user@example.com", tier))

        assert brain._check_daily_limit() is None


def test_tier_gate_keeps_unknown_and_time_unblocked():
    gate = TierGate()
    assert gate.is_allowed("unknown") is True
    assert gate.is_allowed("time") is True
    assert gate.is_allowed("general") is True
