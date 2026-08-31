import importlib.util
import logging
import re
from pathlib import Path
from typing import Optional

try:
    from fuzzywuzzy import fuzz
except Exception:  # pragma: no cover - dependency may be absent in some envs
    fuzz = None


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

    @staticmethod
    def _normalize_text(value: str) -> str:
        """Normalize text for safe trigger comparison."""
        if not value:
            return ""

        text = value.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _score_trigger(self, command: str, trigger: str) -> int:
        """Return a conservative similarity score for trigger matching."""
        normalized_command = self._normalize_text(command)
        normalized_trigger = self._normalize_text(trigger)

        if not normalized_command or not normalized_trigger:
            return 0

        if normalized_trigger in normalized_command or normalized_command in normalized_trigger:
            return 100

        if fuzz is None:
            return 0

        return max(
            fuzz.ratio(normalized_command, normalized_trigger),
            fuzz.partial_ratio(normalized_command, normalized_trigger),
        )

    def match(self, command: str):
        """Match the best skill trigger using exact + conservative fuzzy matching."""
        if not command:
            return None

        normalized_command = self._normalize_text(command)
        if not normalized_command:
            return None

        best_skill = None
        best_score = 0

        for trigger_phrase, skill_module in self._trigger_lookup.items():
            score = self._score_trigger(normalized_command, trigger_phrase)
            if score > best_score:
                best_score = score
                best_skill = skill_module

        if best_skill is not None and best_score >= 82:
            return best_skill

        return None

    def is_tier_sufficient(self, skill, current_tier: str, tiers_config: dict) -> bool:
        """Compare the current tier with the skill's minimum required tier."""
        if skill is None:
            return False

        current_tier = (current_tier or "basic").lower()
        required_tier = str(getattr(skill, "MIN_TIER", "basic")).lower()
        return self.TIER_PRIORITY.get(current_tier, 0) >= self.TIER_PRIORITY.get(required_tier, 0)
