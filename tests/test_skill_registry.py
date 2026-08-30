from pathlib import Path
import textwrap

import brain.orchestrator as orchestrator


def _write_skill(skills_dir: Path, name: str, content: str):
    (skills_dir / name).write_text(textwrap.dedent(content), encoding="utf-8")


def test_well_formed_skill_loads_and_matches(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(
        skills_dir,
        "demo_skill.py",
        """
        SKILL_NAME = "demo_skill"
        TRIGGER_PHRASES = ["heartbeat check", "system check"]
        MIN_TIER = "basic"

        def execute(command: str, context: dict) -> dict:
            return {"status": "success", "type": "skill", "message": "ok"}
        """,
    )

    from brain.skill_registry import SkillRegistry

    registry = SkillRegistry(skills_dir)

    assert registry.match("system check").SKILL_NAME == "demo_skill"
    assert registry.match("hello world") is None


def test_missing_required_attribute_is_skipped(caplog, tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(
        skills_dir,
        "bad_skill.py",
        """
        SKILL_NAME = "bad_skill"
        TRIGGER_PHRASES = ["broken trigger"]

        def execute(command: str, context: dict) -> dict:
            return {"status": "success", "type": "skill", "message": "bad"}
        """,
    )
    _write_skill(
        skills_dir,
        "valid_skill.py",
        """
        SKILL_NAME = "valid_skill"
        TRIGGER_PHRASES = ["check valid skill"]
        MIN_TIER = "professional"

        def execute(command: str, context: dict) -> dict:
            return {"status": "success", "type": "skill", "message": "valid"}
        """,
    )

    from brain.skill_registry import SkillRegistry

    with caplog.at_level("WARNING"):
        registry = SkillRegistry(skills_dir)

    assert "skipping skill" in caplog.text.lower()
    assert registry.match("check valid skill").SKILL_NAME == "valid_skill"


def test_is_tier_sufficient_ranks_basic_pro_and_lifetime():
    from brain.skill_registry import SkillRegistry

    registry = SkillRegistry()

    class Skill:
        MIN_TIER = "basic"

    class SkillProfessional:
        MIN_TIER = "professional"

    class SkillLifetime:
        MIN_TIER = "lifetime"

    assert registry.is_tier_sufficient(Skill(), "basic", {}) is True
    assert registry.is_tier_sufficient(SkillProfessional(), "basic", {}) is False
    assert registry.is_tier_sufficient(SkillProfessional(), "professional", {}) is True
    assert registry.is_tier_sufficient(SkillLifetime(), "pro", {}) is True
    assert registry.is_tier_sufficient(SkillLifetime(), "professional", {}) is False


def test_no_match_returns_none(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(
        skills_dir,
        "demo_skill.py",
        """
        SKILL_NAME = "demo_skill"
        TRIGGER_PHRASES = ["jarvis are you there"]
        MIN_TIER = "basic"

        def execute(command: str, context: dict) -> dict:
            return {"status": "success", "type": "skill", "message": "hit"}
        """,
    )

    from brain.skill_registry import SkillRegistry

    registry = SkillRegistry(skills_dir)
    assert registry.match("open the app") is None


def test_real_example_ping_skill_integration():
    brain = orchestrator.Brain()
    brain.tier_gate.current_tier = "basic"

    result = brain.process("jarvis are you there")

    assert result.get("status") == "success"
    assert result.get("assistant_reply") == "Yes sir, all systems online."
    assert result.get("tool_result", {}).get("message") == "Yes sir, all systems online."
