"""
JARVIS Maps Skill

Day 6 — Google Maps URL builder (no API key needed, no navigation SDK).
"""

from __future__ import annotations

import urllib.parse
import webbrowser

SKILL_NAME = "maps"

TRIGGER_PHRASES = [
    "maps par dikhao",
    "maps par kholo",
    "nearest",
    "paas mein",
    "kitni door hai",
    "route dikhao",
    "directions do",
    "raasta batao",
]

MIN_TIER = "basic"

def _extract_place(text: str) -> str:
    text = (text or "").lower()
    for phrase in TRIGGER_PHRASES:
        text = text.replace(phrase, "")
    return text.strip()

def execute(command: str, context: dict) -> dict:
    place = _extract_place(command or "")

    if not place:
        return {
            "status": "error",
            "type": "skill",
            "message": "Sir, please specify a place to search on Maps.",
        }

    text = (command or "").lower()
    is_directions = any(
        w in text for w in ["route", "directions", "raasta"]
    )

    if is_directions:
        url = (
            "https://www.google.com/maps/dir/?api=1&destination="
            + urllib.parse.quote(place)
        )
        message = f"Showing directions to {place}."
    else:
        url = (
            "https://www.google.com/maps/search/?api=1&query="
            + urllib.parse.quote(place)
        )
        message = f"Showing {place} on Maps."

    try:
        webbrowser.open(url)
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
