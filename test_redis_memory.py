#!/usr/bin/env python
"""Quick verification that Redis-backed memory works (JSON fallback OK)."""

from memory.jarvis_memory import get_recent_conversations_text
from memory.redis_store import JsonMemoryBackend, get_memory_backend


def main() -> None:
    backend = get_memory_backend()
    backend_name = type(backend).__name__
    print(f"Backend: {backend_name}")

    owner = backend.read_owner()
    print(f"Owner fields: {len(owner)}")
    if owner:
        print(f"  name: {owner.get('name', '(missing)')}")

    facts = backend.get_facts()
    print(f"Facts: {len(facts)}")
    if facts:
        print(f"  latest: {facts[-1].get('fact', '')}")

    text = get_recent_conversations_text(5)
    print(f"Recent conversations:\n{text or '(none)'}")

    if isinstance(backend, JsonMemoryBackend):
        backend.append_conversation("Redis plugin demo entry", speaker="AGENT")
        print("\nAppended demo conversation to JSON fallback store.")


if __name__ == "__main__":
    main()
