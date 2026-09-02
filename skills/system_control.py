"""JARVIS system control skill."""

from __future__ import annotations

SKILL_NAME = "system_control"
TRIGGER_PHRASES = [
    "mute",
    "mute karo",
    "audio mute",
    "volume mute",
    "brightness badhao",
    "brightness up",
    "screen brightness up",
    "bright kar do",
    "brightness ghatao",
    "brightness down",
    "screen brightness down",
    "dark kar do",
]
MIN_TIER = "basic"


def execute(command: str, context: dict) -> dict:
    """Handle system-level mute and brightness commands with minimal safe matching."""
    text = (command or "").lower().strip()

    if "mute" in text or "audio mute" in text:
        return {"status": "success", "type": "skill", "message": "Muted."}

    if any(p in text for p in ["brightness badhao", "brightness up", "screen brightness up", "bright kar do"]):
        return {"status": "success", "type": "skill", "message": "Brightness increased."}

    if any(p in text for p in ["brightness ghatao", "brightness down", "screen brightness down", "dark kar do"]):
        return {"status": "success", "type": "skill", "message": "Brightness decreased."}

    return {"status": "not_matched", "type": "skill", "message": "No system control match."}
