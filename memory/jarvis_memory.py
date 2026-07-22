"""
JARVIS memory API used by memory_interceptor and tests.

Uses Redis when available (Hashes, Streams, INCR) with JSON fallback.
"""
from __future__ import annotations

from livekit.agents import function_tool

from memory.redis_store import get_memory_backend


def _get_recent_entries_sync(limit: int = 5) -> list[dict]:
    return get_memory_backend().get_recent_conversations(limit)


def get_recent_conversations_text(limit: int = 10) -> str:
    """Sync helper for memory_interceptor and non-async callers."""
    return _format_conversations(_get_recent_entries_sync(limit))


def _format_conversations(entries: list[dict]) -> str:
    if not entries:
        return "अभी तक कोई बातचीत याद नहीं है"
    lines = []
    for entry in entries:
        speaker = entry.get("speaker", "USER")
        text = entry.get("text", "")
        time = entry.get("time", "")
        prefix = f"[{time}] " if time else ""
        lines.append(f"{prefix}{speaker}: {text}")
    return "\n".join(lines)


@function_tool
async def get_recent_conversations(limit: int = 10) -> str:
    """Recent conversations padhna — Redis Stream se, ya JSON fallback."""
    entries = _get_recent_entries_sync(limit)
    return _format_conversations(entries)


@function_tool
async def save_conversation(text: str, speaker: str = "USER") -> str:
    """Conversation entry save karo."""
    get_memory_backend().append_conversation(text, speaker=speaker)
    return "Memory saved successfully"


@function_tool
async def remember_owner_info(key: str, value: str) -> str:
    """Owner ki personal info save karo (Redis Hash)."""
    get_memory_backend().write_owner_field(key, value)
    return f"✅ Yaad kar liya: {key} = {value}"


@function_tool
async def get_owner_info() -> str:
    """Owner ki saved info padhna."""
    owner = get_memory_backend().read_owner()
    if not owner:
        return "Abhi tak koi personal info save nahi hui."
    result = "👤 Owner Info:\n"
    for k, v in owner.items():
        result += f"  {k}: {v}\n"
    return result


@function_tool
async def save_fact(fact: str) -> str:
    """Important fact save karo."""
    get_memory_backend().append_fact(fact)
    return f"✅ Fact save: {fact}"


@function_tool
async def get_all_facts() -> str:
    """Sab saved facts padhna."""
    facts = get_memory_backend().get_facts()
    if not facts:
        return "Koi facts save nahi hain."
    result = "📌 Saved Facts:\n"
    for item in facts:
        result += f"  • {item.get('fact', '')} ({item.get('time', '')})\n"
    return result
