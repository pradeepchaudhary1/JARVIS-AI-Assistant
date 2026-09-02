"""
JARVIS Scroll Control Skill
Day 4 — adapted from Automation/scroll_system.py (audited, no personal data).
"""

from __future__ import annotations

import pyautogui

SKILL_NAME = "scroll_control"
TRIGGER_PHRASES = [
    "scroll up", "upar scroll karo",
    "scroll down", "neeche scroll karo",
    "scroll to top", "shuruat par jao",
    "scroll to bottom", "ant par jao",
]

MIN_TIER = "basic"

def _scroll_up():
    pyautogui.press("up", presses=5)

def _scroll_down():
    pyautogui.press("down", presses=5)

def _scroll_to_top():
    pyautogui.hotkey("home")

def _scroll_to_bottom():
    pyautogui.hotkey("end")

_ACTIONS = [
    (("scroll up", "upar scroll karo"), _scroll_up, "Scrolled up."),
    (("scroll down", "neeche scroll karo"), _scroll_down, "Scrolled down."),
    (("scroll to top", "shuruat par jao"), _scroll_to_top, "Scrolled to top."),
    (("scroll to bottom", "ant par jao"), _scroll_to_bottom, "Scrolled to bottom."),
]

def execute(command: str, context: dict) -> dict:
    text = (command or "").lower()

    for phrases, action, message in _ACTIONS:
        if any(p in text for p in phrases):
            try:
                action()
                return {"status": "success", "type": "skill", "message": message}
            except Exception as e:
                return {"status": "error", "type": "skill", "message": str(e)}

    return {"status": "error", "type": "skill", "message": "No matching scroll action."}
