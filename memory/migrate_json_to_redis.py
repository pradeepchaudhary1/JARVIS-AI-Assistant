#!/usr/bin/env python
"""Import existing jarvis_memory.json into Redis."""
from memory.redis_store import migrate_json_to_redis


def main() -> None:
    counts = migrate_json_to_redis()
    print("✅ Migrated JARVIS memory to Redis:")
    for key, value in counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
