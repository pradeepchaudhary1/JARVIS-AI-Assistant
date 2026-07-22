"""
JARVIS Memory System — Issue #2 Fix
Persistent memory: Name, preferences, tasks, conversations
"""
import os, json
from livekit.agents import function_tool

from memory.redis_store import get_memory_backend

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "jarvis_memory.json")
TASKS_FILE  = os.path.join(os.path.dirname(__file__), "jarvis_tasks.json")
_backend = get_memory_backend()


# ══════════════════════════════════════════════
# MEMORY TOOLS
# ══════════════════════════════════════════════

@function_tool
async def remember_owner_info(key: str, value: str) -> str:
    """
    Owner ki personal info save karo.
    Examples: name=Pradeep, profession=YouTuber, city=Kota
    """
    _backend.write_owner_field(key, value)
    return f"✅ Yaad kar liya: {key} = {value}"


@function_tool
async def get_owner_info() -> str:
    """Owner ki saved info padhna"""
    owner = _backend.read_owner()
    if not owner:
        return "Abhi tak koi personal info save nahi hui. Apna naam batao: 'Mera naam Pradeep hai'"
    result = "👤 Owner Info:\n"
    for k, v in owner.items():
        result += f"  {k}: {v}\n"
    return result


@function_tool
async def save_memory(data: str) -> str:
    """Koi bhi baat memory mein save karo"""
    _backend.append_conversation(data, speaker="USER")
    return f"✅ Memory save ho gayi."


@function_tool
async def load_memory() -> str:
    """Sab saved memory padhna"""
    owner = _backend.read_owner()
    result = ""
    if owner:
        result += f"👤 Owner: {json.dumps(owner, ensure_ascii=False)}\n\n"
    convos = _backend.get_recent_conversations(50)
    if convos:
        result += f"💬 Recent ({len(convos)} entries):\n"
        for c in convos[-5:]:
            result += f"  [{c.get('time','')}] {c.get('text','')}\n"
    return result if result else "Memory khali hai."


@function_tool
async def get_recent_conversations(limit: int = 5) -> str:
    """Recent conversations padhna"""
    convos = _backend.get_recent_conversations(limit)
    if not convos:
        return "Abhi tak koi baat yaad nahi hai."
    recent = convos[-limit:]
    result = f"💬 Last {len(recent)} entries:\n"
    for c in recent:
        result += f"  [{c.get('time','')}] {c.get('text','')}\n"
    return result


@function_tool
async def add_memory_entry(entry: str) -> str:
    """New memory entry add karo"""
    return await save_memory(entry)


@function_tool
async def save_fact(fact: str) -> str:
    """Important fact save karo jo hamesha yaad rahe"""
    _backend.append_fact(fact)
    return f"✅ Fact save: {fact}"


@function_tool
async def get_all_facts() -> str:
    """Sab saved facts padhna"""
    facts = _backend.get_facts()
    if not facts:
        return "Koi facts save nahi hain."
    result = "📌 Saved Facts:\n"
    for f in facts:
        result += f"  • {f['fact']} ({f.get('time','')})\n"
    return result


# ══════════════════════════════════════════════
# TASK MANAGEMENT TOOLS
# ══════════════════════════════════════════════

@function_tool
async def add_task(task: str, priority: str = "medium") -> str:
    """New task add karo pending list mein"""
    entry = _backend.add_task(task, priority=priority)
    return f"✅ Task add hua: {task} (Priority: {priority})"


@function_tool
async def get_pending_tasks() -> str:
    """Sab pending tasks batao"""
    pending = [t for t in _backend.get_tasks() if t.get("status") == "pending"]
    if not pending:
        return "✅ Koi pending tasks nahi hain."
    result = f"📋 Pending Tasks ({len(pending)}):\n"
    for t in pending:
        result += f"  {t['id']}. [{t.get('priority','').upper()}] {t['task']} — {t.get('created','')}\n"
    return result


@function_tool
async def complete_task(task_id: int) -> str:
    """Task complete mark karo"""
    completed = _backend.complete_task(task_id)
    if completed:
        return f"✅ Task #{task_id} complete: {completed['task']}"
    return f"Task #{task_id} nahi mila."


@function_tool
async def get_system_errors() -> str:
    """Recent system errors batao"""
    try:
        error_log = os.path.join(os.path.dirname(__file__), "jarvis_log.txt")
        if not os.path.exists(error_log):
            return "Koi error log nahi mila."
        with open(error_log, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        errors = [l for l in lines if "ERROR" in l or "❌" in l]
        if not errors:
            return "✅ Koi errors nahi mile."
        result = f"⚠ Recent Errors ({len(errors[-5:])}):\n"
        for e in errors[-5:]:
            result += f"  {e.strip()}\n"
        return result
    except Exception as e:
        return f"Error log read error: {e}"
