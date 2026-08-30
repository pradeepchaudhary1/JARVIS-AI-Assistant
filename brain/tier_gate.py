"""
JARVIS Tier Gate — Phase 2.6a
Feature-gating only. Does not touch dangerous-command confirmation
or usage limits (that's Phase 2.6b, pending license_manager review).
"""

from __future__ import annotations
import json
import os


class TierGate:

    TIERS_FILE = os.path.join("config", "tiers.json")

    def __init__(self):
        with open(self.TIERS_FILE, "r", encoding="utf-8") as f:
            self.tiers = json.load(f)

        self.current_tier = self._load_active_tier()

    def _load_active_tier(self) -> str:
        try:
            from license_manager import read_license_data

            _, tier = read_license_data()
            if tier in self.tiers:
                return tier
        except Exception:
            pass

        return "basic"

    def is_allowed(self, intent: str) -> bool:
        """
        Only gates KNOWN/INTEGRATED tool intents (open_app, close_app,
        minimize_window, maximize_window, restore_window, open_folder,
        web_search). Any other intent (unknown, time, general LLM
        conversation) is NEVER gated here — always returns True for those.
        """
        integrated_intents = {
            "open_app", "close_app", "minimize_window",
            "maximize_window", "restore_window", "open_folder", "web_search",
        }

        if intent not in integrated_intents:
            return True

        tier_config = self.tiers.get(self.current_tier, self.tiers["basic"])
        return intent in tier_config.get("allowed_intents", [])

    def upgrade_message(self, intent: str) -> str:
        return (
            f"Sir, '{intent}' is not available on your current "
            f"({self.current_tier.title()}) plan. Please upgrade to "
            f"unlock this feature."
        )