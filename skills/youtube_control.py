"""
JARVIS YouTube Media Control Skill
Day 4 — adapted from Automation/Youtube_playback.py (audited, no personal data).
"""

from __future__ import annotations

import pyautogui

SKILL_NAME = "youtube_control"

TRIGGER_PHRASES = [
    "volume up", "volume badhao",
    "volume down", "volume ghatao",
    "seek forward", "aage badhao",
    "seek backward", "peeche karo",
    "seek to beginning", "shuruat par jao video",
    "seek to end", "ant par jao video",
    "decrease playback speed", "speed kam karo",
    "increase playback speed", "speed badhao",
    "move to next video", "next video par jao",
    "move to previous video", "previous video par jao",
]

MIN_TIER = "basic"

def _volume_up():
    pyautogui.press("up")

def _volume_down():
    pyautogui.press("down")

def _seek_forward():
    pyautogui.press("right")

def _seek_backward():
    pyautogui.press("left")

def _seek_to_beginning():
    pyautogui.press("home")

def _seek_to_end():
    pyautogui.press("end")

def _decrease_speed():
    pyautogui.hotkey("shift", ",")

def _increase_speed():
    pyautogui.hotkey("shift", ".")

def _next_video():
    pyautogui.hotkey("shift", "n")

def _previous_video():
    pyautogui.hotkey("shift", "p")

_ACTIONS = [
    (("volume up", "volume badhao"), _volume_up, "Volume increased."),
    (("volume down", "volume ghatao"), _volume_down, "Volume decreased."),
    (("seek forward", "aage badhao"), _seek_forward, "Seeked forward."),
    (("seek backward", "peeche karo"), _seek_backward, "Seeked backward."),
    (("seek to beginning", "shuruat par jao video"), _seek_to_beginning, "Went to beginning."),
    (("seek to end", "ant par jao video"), _seek_to_end, "Went to end."),
    (("decrease playback speed", "speed kam karo"), _decrease_speed, "Playback speed decreased."),
    (("increase playback speed", "speed badhao"), _increase_speed, "Playback speed increased."),
    (("move to next video", "next video par jao"), _next_video, "Moved to next video."),
    (("move to previous video", "previous video par jao"), _previous_video, "Moved to previous video."),
]

def execute(command: str, context: dict) -> dict:
    text = (command or "").lower()

    for phrases, action, message in _ACTIONS:
        if any(p in text for p in phrases):
            try:
                action()
                return {
                    "status": "success",
                    "type": "skill",
                    "message": message,
                }
            except Exception as e:
                return {
                    "status": "error",
                    "type": "skill",
                    "message": str(e),
                }

    return {
        "status": "error",
        "type": "skill",
        "message": "No matching YouTube action.",
    }
