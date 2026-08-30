"""
Redis-backed JARVIS memory store.

Applies Redis plugin best practices:
- Consistent key naming (jarvis:{entity})
- Hash for owner profile fields
- Stream for append-only conversation log (MAXLEN cap)
- INCR for atomic task IDs
- Connection pooling with timeouts
- TTL on ephemeral conversation entries
- JSON file fallback when Redis is unavailable
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "jarvis_memory.json")
TASKS_FILE = os.path.join(BASE_DIR, "jarvis_tasks.json")

# Key naming: jarvis:{entity}:{detail}
KEY_OWNER = "jarvis:owner:profile"
KEY_FACTS = "jarvis:facts"
KEY_TASKS = "jarvis:tasks"
KEY_TASK_SEQ = "jarvis:tasks:seq"
STREAM_CONVERSATIONS = "jarvis:conversations"
USAGE_DAILY_PREFIX = "jarvis:usage:daily"

CONVERSATION_MAXLEN = 50
CONVERSATION_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")


class MemoryBackend:
    def read_owner(self) -> dict[str, str]:
        raise NotImplementedError

    def write_owner_field(self, key: str, value: str) -> None:
        raise NotImplementedError

    def append_conversation(self, text: str, speaker: str = "USER") -> None:
        raise NotImplementedError

    def get_recent_conversations(self, limit: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError

    def append_fact(self, fact: str) -> None:
        raise NotImplementedError

    def get_facts(self) -> list[dict[str, str]]:
        raise NotImplementedError

    def add_task(self, task: str, priority: str = "medium") -> dict[str, Any]:
        raise NotImplementedError

    def get_tasks(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def complete_task(self, task_id: int) -> dict[str, Any] | None:
        raise NotImplementedError


class JsonMemoryBackend(MemoryBackend):
    def _read_memory(self) -> dict:
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"owner": {}, "preferences": {}, "conversations": [], "facts": []}

    def _write_memory(self, data: dict) -> None:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def read_owner(self) -> dict[str, str]:
        return self._read_memory().get("owner", {})

    def write_owner_field(self, key: str, value: str) -> None:
        mem = self._read_memory()
        mem.setdefault("owner", {})[key] = value
        self._write_memory(mem)

    def append_conversation(self, text: str, speaker: str = "USER") -> None:
        mem = self._read_memory()
        mem.setdefault("conversations", []).append(
            {
                "speaker": speaker,
                "text": text,
                "time": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
        )
        mem["conversations"] = mem["conversations"][-CONVERSATION_MAXLEN:]
        self._write_memory(mem)

    def get_recent_conversations(self, limit: int = 5) -> list[dict[str, Any]]:
        convos = self._read_memory().get("conversations", [])
        return convos[-limit:]

    def append_fact(self, fact: str) -> None:
        mem = self._read_memory()
        mem.setdefault("facts", []).append(
            {"fact": fact, "time": datetime.now().strftime("%d/%m/%Y %H:%M")}
        )
        self._write_memory(mem)

    def get_facts(self) -> list[dict[str, str]]:
        return self._read_memory().get("facts", [])

    def increment_daily_usage(self, email: str) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        email_key = email.strip().lower()
        mem = self._read_memory()
        usage = mem.setdefault("daily_usage", {})
        daily_key = f"{today}:{email_key}"
        current = int(usage.get(daily_key, 0)) + 1
        usage[daily_key] = current
        self._write_memory(mem)
        return current

    def _read_tasks(self) -> list[dict[str, Any]]:
        try:
            if os.path.exists(TASKS_FILE):
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _write_tasks(self, tasks: list[dict[str, Any]]) -> None:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)

    def add_task(self, task: str, priority: str = "medium") -> dict[str, Any]:
        tasks = self._read_tasks()
        entry = {
            "id": len(tasks) + 1,
            "task": task,
            "priority": priority,
            "status": "pending",
            "created": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        tasks.append(entry)
        self._write_tasks(tasks)
        return entry

    def get_tasks(self) -> list[dict[str, Any]]:
        return self._read_tasks()

    def complete_task(self, task_id: int) -> dict[str, Any] | None:
        tasks = self._read_tasks()
        for task in tasks:
            if task.get("id") == task_id:
                task["status"] = "done"
                task["completed"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                self._write_tasks(tasks)
                return task
        return None


class RedisMemoryBackend(MemoryBackend):
    def __init__(self, url: str = REDIS_URL):
        import redis

        self._pool = redis.ConnectionPool.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            max_connections=10,
        )
        self._client = redis.Redis(connection_pool=self._pool)

    def _now(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M")

    def read_owner(self) -> dict[str, str]:
        return self._client.hgetall(KEY_OWNER)

    def write_owner_field(self, key: str, value: str) -> None:
        self._client.hset(KEY_OWNER, key, value)

    def append_conversation(self, text: str, speaker: str = "USER") -> None:
        entry_id = self._client.xadd(
            STREAM_CONVERSATIONS,
            {
                "speaker": speaker,
                "text": text,
                "time": self._now(),
            },
            maxlen=CONVERSATION_MAXLEN,
            approximate=True,
        )
        self._client.expire(STREAM_CONVERSATIONS, CONVERSATION_TTL_SECONDS)
        return entry_id

    def get_recent_conversations(self, limit: int = 5) -> list[dict[str, Any]]:
        entries = self._client.xrevrange(STREAM_CONVERSATIONS, count=limit)
        results = []
        for _entry_id, fields in reversed(entries):
            results.append(
                {
                    "speaker": fields.get("speaker", "USER"),
                    "text": fields.get("text", ""),
                    "time": fields.get("time", ""),
                }
            )
        return results

    def append_fact(self, fact: str) -> None:
        payload = json.dumps({"fact": fact, "time": self._now()}, ensure_ascii=False)
        self._client.rpush(KEY_FACTS, payload)

    def get_facts(self) -> list[dict[str, str]]:
        raw = self._client.lrange(KEY_FACTS, 0, -1)
        return [json.loads(item) for item in raw]

    def add_task(self, task: str, priority: str = "medium") -> dict[str, Any]:
        task_id = self._client.incr(KEY_TASK_SEQ)
        entry = {
            "id": task_id,
            "task": task,
            "priority": priority,
            "status": "pending",
            "created": self._now(),
        }
        self._client.hset(KEY_TASKS, str(task_id), json.dumps(entry, ensure_ascii=False))
        return entry

    def get_tasks(self) -> list[dict[str, Any]]:
        raw = self._client.hgetall(KEY_TASKS)
        tasks = [json.loads(value) for value in raw.values()]
        return sorted(tasks, key=lambda item: item.get("id", 0))

    def complete_task(self, task_id: int) -> dict[str, Any] | None:
        key = str(task_id)
        raw = self._client.hget(KEY_TASKS, key)
        if not raw:
            return None
        entry = json.loads(raw)
        entry["status"] = "done"
        entry["completed"] = self._now()
        self._client.hset(KEY_TASKS, key, json.dumps(entry, ensure_ascii=False))
        return entry

    def increment_daily_usage(self, email: str) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{USAGE_DAILY_PREFIX}:{today}:{email.strip().lower()}"
        value = self._client.incr(key)
        self._client.expire(key, 90000)
        return value


@lru_cache(maxsize=1)
def get_memory_backend() -> MemoryBackend:
    try:
        backend = RedisMemoryBackend()
        backend._client.ping()
        return backend
    except Exception:
        return JsonMemoryBackend()


def migrate_json_to_redis(url: str = REDIS_URL) -> dict[str, int]:
    """One-time import from jarvis_memory.json into Redis."""
    json_backend = JsonMemoryBackend()
    redis_backend = RedisMemoryBackend(url)
    redis_backend._client.ping()

    owner = json_backend.read_owner()
    for key, value in owner.items():
        redis_backend.write_owner_field(key, value)

    for fact in json_backend.get_facts():
        redis_backend.append_fact(fact.get("fact", ""))

    for convo in json_backend.get_recent_conversations(CONVERSATION_MAXLEN):
        redis_backend.append_conversation(
            convo.get("text", ""),
            speaker=convo.get("speaker", "USER"),
        )

    for task in json_backend.get_tasks():
        redis_backend._client.hset(
            KEY_TASKS,
            str(task.get("id")),
            json.dumps(task, ensure_ascii=False),
        )
        if task.get("id", 0) > int(redis_backend._client.get(KEY_TASK_SEQ) or 0):
            redis_backend._client.set(KEY_TASK_SEQ, task.get("id"))

    return {
        "owner_fields": len(owner),
        "facts": len(json_backend.get_facts()),
        "conversations": len(json_backend.get_recent_conversations(CONVERSATION_MAXLEN)),
        "tasks": len(json_backend.get_tasks()),
    }
