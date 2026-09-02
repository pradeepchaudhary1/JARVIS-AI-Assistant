"""JARVIS scheduler skill parser for relative timers and reminders."""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from memory.scheduler_store import SchedulerStore

SKILL_NAME = "scheduler"
TRIGGER_PHRASES = [
    "timer",
    "reminder",
    "set timer",
    "set reminder",
    "timer lagao",
    "remind me",
    "yaad dilana",
    "reminder lagao",
    "mere reminders kya hain",
    "mere pending reminders batao",
    "mere reminders batao",
    "kaunse reminders pending hain",
    "what reminders do i have",
    "show my reminders",
    "show pending reminders",
    "what are my pending reminders",
]
MIN_TIER = "basic"


def parse_relative_time(text: str) -> timedelta | None:
    """Parse a relative duration from a command like '20 second' or '5 minute'."""
    if not text:
        return None

    lowered = text.lower().strip()
    if not lowered:
        return None

    patterns = [
        (r"(?P<value>\d+)\s*(?:second|seconds|sec|secs)\b", "seconds"),
        (r"(?P<value>\d+)\s*(?:minute|minutes|min|mins)\b", "minutes"),
        (r"(?P<value>\d+)\s*(?:hour|hours|hr|hrs)\b", "hours"),
    ]

    for pattern, unit in patterns:
        match = re.search(pattern, lowered)
        if not match:
            continue

        try:
            value = int(match.group("value"))
        except ValueError:
            return None

        if unit == "seconds":
            return timedelta(seconds=value)
        if unit == "minutes":
            return timedelta(minutes=value)
        if unit == "hours":
            return timedelta(hours=value)

    return None


def parse_relative_timer(text: str) -> dict | None:
    """Return a reminder payload with an extracted message and fire_at datetime."""
    if not text:
        return None

    duration = parse_relative_time(text)
    if duration is None:
        return None

    now = datetime.now()
    fire_at = now + duration

    pattern = re.compile(
        r"(?P<value>\d+)\s*(?:second|seconds|sec|secs|minute|minutes|min|mins|hour|hours|hr|hrs)\b"
        r"(?:\s*(?:ka|ke|ki|baad|after|in|later))?",
        re.IGNORECASE,
    )

    message = pattern.sub("", text, count=1).strip()
    message = re.sub(r"^(?:ka|ke|ki|baad|after|in|later)\b\s*", "", message, flags=re.IGNORECASE)
    message = re.sub(r"\s{2,}", " ", message)
    message = message.strip(" ,.;:-/\\")

    if not message:
        message = "timer"

    return {
        "message": message,
        "fire_at": fire_at,
    }


def parse_absolute_timer(text: str) -> dict | None:
    """Parse absolute-day reminders like 'kal 7 baje' or 'tomorrow at 8 am'."""
    if not text:
        return None

    raw = text.strip()
    lower = raw.lower()
    if not lower:
        return None

    day_token = None
    if re.search(r"\b(?:kal|tomorrow)\b", lower):
        day_token = "tomorrow"
    elif re.search(r"\b(?:aaj|today)\b", lower):
        day_token = "today"
    else:
        return None

    now = datetime.now()
    time_match = None
    hour = None
    minute = 0
    ampm = None

    hindi_match = re.search(
        r"(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*baje\b",
        lower,
        flags=re.IGNORECASE,
    )
    if hindi_match:
        time_match = hindi_match
        hour = int(hindi_match.group("hour"))
        minute = int(hindi_match.group("minute") or 0)
        ampm = None
    else:
        english_match = re.search(
            r"(?:at\s+)?(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)?\b",
            lower,
            flags=re.IGNORECASE,
        )
        if english_match:
            time_match = english_match
            hour = int(english_match.group("hour"))
            minute = int(english_match.group("minute") or 0)
            ampm = (english_match.group("ampm") or "").lower()

    if time_match is None:
        return None

    if ampm == "am":
        hour = hour % 12
    elif ampm == "pm":
        hour = (hour % 12) + 12
    elif time_match.re.pattern.lower().find("baje") != -1 and ampm is None:
        hour = hour % 24
    elif ampm is None:
        hour = hour % 24

    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None

    if day_token == "today":
        target = datetime.combine(now.date(), datetime.min.time()).replace(hour=hour, minute=minute)
        if target <= now:
            return None
    else:
        next_day = now.date() + timedelta(days=1)
        target = datetime.combine(next_day, datetime.min.time()).replace(hour=hour, minute=minute)

    message = raw
    message = re.sub(r"\b(?:kal|tomorrow|aaj|today)\b", " ", message, flags=re.IGNORECASE)
    message = re.sub(
        r"\b(?:reminder\s+lagao|reminder|lagao|yaad\s+dilana|yaad\s+dila\s+dena|remind\s+me|at|baje|am|pm|mujhe)\b",
        " ",
        message,
        flags=re.IGNORECASE,
    )
    message = re.sub(r"\b\d{1,2}(?::\d{2})?\s*(?:baje|am|pm)?\b", " ", message, flags=re.IGNORECASE)
    message = re.sub(r"\s{2,}", " ", message)
    message = message.strip(" ,.;:-/\\")
    if not message:
        message = "reminder"

    return {
        "message": message,
        "fire_at": target,
    }


def schedule_timer(text: str) -> dict | None:
    """Parse a timer/reminder and persist it using the project SchedulerStore."""
    result = parse_relative_timer(text)
    if result is None:
        result = parse_absolute_timer(text)
    if result is None:
        return None

    store = SchedulerStore()
    reminder_id = store.add_reminder(
        message=result["message"],
        fire_at=result["fire_at"],
    )

    return {
        "id": reminder_id,
        "message": result["message"],
        "fire_at": result["fire_at"],
    }


def get_pending_reminders() -> list[dict]:
    """Return all pending reminders from the project's SchedulerStore."""
    store = SchedulerStore()
    return store.get_all_pending()


def query_reminders(text: str) -> list[dict] | None:
    """Return pending reminders for recognized reminder-query prompts."""
    if not text:
        return None

    normalized = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return None

    patterns = [
        r"\b(?:mere|my)\s+(?:pending\s+)?reminders?\s*(?:kya\s+hain|batao|do\s+i\s+have|show|are)?\b",
        r"\bkaunse\s+reminders?\s+pending\s+hain\b",
        r"\bwhat\s+reminders?\s+do\s+i\s+have\b",
        r"\bshow\s+(?:my\s+)?(?:pending\s+)?reminders?\b",
        r"\bwhat\s+are\s+my\s+pending\s+reminders\b",
    ]

    if any(re.search(pattern, normalized) for pattern in patterns):
        return get_pending_reminders()

    return None


def execute(command: str, context: dict) -> dict:
    """Skill entry point for scheduling timers and answering reminder queries."""
    query_result = query_reminders(command or "")
    if query_result is not None:
        return {
            "status": "success",
            "type": "skill",
            "message": query_result,
        }

    parsed = parse_relative_timer(command or "")
    if parsed is None:
        parsed = parse_absolute_timer(command or "")

    if parsed is None:
        return {
            "status": "not_matched",
            "type": "skill",
            "message": "I could not parse a relative timer or reminder.",
        }

    scheduled = schedule_timer(command or "")
    if scheduled is None:
        return {
            "status": "not_matched",
            "type": "skill",
            "message": "I could not parse a relative timer or reminder.",
        }

    return {
        "status": "success",
        "type": "skill",
        "message": scheduled["message"],
        "fire_at": scheduled["fire_at"].isoformat(),
        "id": scheduled["id"],
    }
