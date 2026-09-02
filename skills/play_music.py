"""JARVIS play music skill."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote

SKILL_NAME = "play_music"
TRIGGER_PHRASES = [
    "play music",
    "music chalao",
    "gaana chalao",
    "song chalao",
]
MIN_TIER = "basic"


def execute(command: str, context: dict) -> dict:
    """Open a music source for the requested tune without hardcoded personal paths."""
    text = (command or "").strip()
    lowered = text.lower()

    if not any(phrase in lowered for phrase in [p.lower() for p in TRIGGER_PHRASES]):
        return {
            "status": "not_matched",
            "type": "skill",
            "message": "No music command matched.",
        }

    query = text
    for phrase in TRIGGER_PHRASES:
        query = query.replace(phrase, "", 1).strip()

    if not query:
        query = "popular songs"

    url = "https://music.youtube.com/search?q=" + quote(query)
    try:
        webbrowser.open(url, new=2)
        return {
            "status": "success",
            "type": "skill",
            "message": f"Playing music for: {query}",
        }
    except Exception as exc:
        return {
            "status": "error",
            "type": "skill",
            "message": str(exc),
        }
