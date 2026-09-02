"""
JARVIS Browser Control Skill
Day 4 — adapted from Automation/tab_automation.py (audited, no personal data).
"""

from __future__ import annotations

import pyautogui


SKILL_NAME = "browser_control"
TRIGGER_PHRASES = [
    "open new tab", "new tab kholo",
    "close tab", "tab band karo",
    "zoom in", "zoom in karo",
    "zoom out", "zoom out karo",
    "refresh page", "page refresh karo",
    "switch to next tab", "next tab par jao",
    "switch to previous tab", "previous tab par jao",
    "open history", "history kholo",
    "open bookmarks", "bookmarks kholo",
    "go back", "peeche jao",
    "go forward", "aage jao",
    "open dev tools", "dev tools kholo",
    "toggle full screen", "full screen karo",
    "open private window", "private window kholo",
]
MIN_TIER = "basic"


def _open_new_tab():
    pyautogui.hotkey("ctrl", "t")


def _close_tab():
    pyautogui.hotkey("ctrl", "w")


def _zoom_in():
    pyautogui.hotkey("ctrl", "+")


def _zoom_out():
    pyautogui.hotkey("ctrl", "-")


def _refresh_page():
    pyautogui.hotkey("ctrl", "r")


def _switch_next_tab():
    pyautogui.hotkey("ctrl", "tab")


def _switch_previous_tab():
    pyautogui.hotkey("ctrl", "shift", "tab")


def _open_history():
    pyautogui.hotkey("ctrl", "h")


def _open_bookmarks():
    pyautogui.hotkey("ctrl", "b")


def _go_back():
    pyautogui.hotkey("alt", "left")


def _go_forward():
    pyautogui.hotkey("alt", "right")


def _open_dev_tools():
    pyautogui.hotkey("ctrl", "shift", "i")


def _toggle_full_screen():
    pyautogui.press("f11")


def _open_private_window():
    pyautogui.hotkey("ctrl", "shift", "n")


_ACTIONS = [
    (("open new tab", "new tab kholo"), _open_new_tab, "New tab opened."),
    (("close tab", "tab band karo"), _close_tab, "Tab closed."),
    (("zoom in", "zoom in karo"), _zoom_in, "Zoomed in."),
    (("zoom out", "zoom out karo"), _zoom_out, "Zoomed out."),
    (("refresh page", "page refresh karo"), _refresh_page, "Page refreshed."),
    (("switch to next tab", "next tab par jao"), _switch_next_tab, "Switched to next tab."),
    (("switch to previous tab", "previous tab par jao"), _switch_previous_tab, "Switched to previous tab."),
    (("open history", "history kholo"), _open_history, "History opened."),
    (("open bookmarks", "bookmarks kholo"), _open_bookmarks, "Bookmarks opened."),
    (("go back", "peeche jao"), _go_back, "Went back."),
    (("go forward", "aage jao"), _go_forward, "Went forward."),
    (("open dev tools", "dev tools kholo"), _open_dev_tools, "Dev tools opened."),
    (("toggle full screen", "full screen karo"), _toggle_full_screen, "Toggled full screen."),
    (("open private window", "private window kholo"), _open_private_window, "Private window opened."),
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

    return {"status": "error", "type": "skill", "message": "No matching browser action."}
