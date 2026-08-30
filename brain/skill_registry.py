import importlib.util
import logging
from pathlib import Path
from typing import Optional


class SkillRegistry:
    """Auto-discovers and matches locally defined JARVIS skills."""

    TIER_PRIORITY = {
        "basic": 0,
        "professional": 1,
        "pro": 2,
        "lifetime": 2,
    }

    def __init__(self, skills_dir: Optional[str | Path] = None):
        base_dir = Path(skills_dir) if skills_dir is not None else Path(__file__).resolve().parent.parent / "skills"
        self.skills_dir = Path(base_dir)
        self._skills = []
        self._trigger_lookup = {}
        self._load_skills()

    def _load_skills(self):
        if not self.skills_dir.exists():
            return

        for path in sorted(self.skills_dir.glob("*.py")):
            if path.name in {"__init__.py"} or path.name.startswith("_"):
                continue

            module = self._load_module(path)
            if module is None:
                continue

            if not self._validate_module(module):
                continue

            self._skills.append(module)

            for trigger in getattr(module, "TRIGGER_PHRASES", []):
                normalized = str(trigger).strip().lower()
                if normalized and normalized not in self._trigger_lookup:
                    self._trigger_lookup[normalized] = module

    def _load_module(self, path: Path):
        module_name = f"jarvis_skill_{path.stem}_{abs(hash(str(path.resolve())))}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            logging.warning("Skipping skill '%s': could not create import spec.", path.name)
            return None

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # pragma: no cover - warning path only
            logging.warning("Skipping skill '%s' due to import error: %s", path.name, exc)
            return None

        return module

    def _validate_module(self, module):
        required = ["SKILL_NAME", "TRIGGER_PHRASES", "MIN_TIER", "execute"]
        missing = [name for name in required if not hasattr(module, name)]

        if missing:
            logging.warning(
                "Skipping skill '%s': missing required attribute(s): %s",
                getattr(module, "SKILL_NAME", "unknown"),
                ", ".join(missing),
            )
            return False

        trigger_phrases = getattr(module, "TRIGGER_PHRASES", [])
        if not isinstance(trigger_phrases, list) or not trigger_phrases:
            logging.warning("Skipping skill '%s': TRIGGER_PHRASES must be a non-empty list.", getattr(module, "SKILL_NAME", "unknown"))
            return False

        return True

    def match(self, command: str):
        """Case-insensitive substring match against TRIGGER_PHRASES."""
        if not command:
            return None

        lowered = command.lower()
        for trigger_phrase, skill_module in self._trigger_lookup.items():
            if trigger_phrase in lowered:
                return skill_module

        return None

    def is_tier_sufficient(self, skill, current_tier: str, tiers_config: dict) -> bool:
        """Compare the current tier with the skill's minimum required tier."""
        if skill is None:
            return False

        current_tier = (current_tier or "basic").lower()
        required_tier = str(getattr(skill, "MIN_TIER", "basic")).lower()
        return self.TIER_PRIORITY.get(current_tier, 0) >= self.TIER_PRIORITY.get(required_tier, 0)
