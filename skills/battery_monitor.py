"""JARVIS battery monitor skill."""

from __future__ import annotations

import psutil

SKILL_NAME = "battery_monitor"
TRIGGER_PHRASES = [
    "battery status",
    "battery kitni hai",
    "battery percentage",
    "battery check karo",
    "battery batao",
]
MIN_TIER = "basic"


def _read_battery() -> dict:
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return {"status": "error", "type": "skill", "message": "Battery information unavailable."}

        percent = int(battery.percent)
        plugged = bool(battery.power_plugged)
        status = "Charging" if plugged else "Discharging"
        return {
            "status": "success",
            "type": "skill",
            "message": f"Battery is at {percent}% and currently {status}.",
            "percent": percent,
            "plugged": plugged,
            "status": status,
        }
    except Exception as exc:  # pragma: no cover - graceful fallback for unsupported environments
        return {"status": "error", "type": "skill", "message": str(exc)}


def execute(command: str, context: dict) -> dict:
    text = (command or "").lower().strip()
    if not any(phrase in text for phrase in [p.lower() for p in TRIGGER_PHRASES]):
        return {
            "status": "not_matched",
            "type": "skill",
            "message": "No battery status request matched.",
        }

    return _read_battery()
