import os, json, time
from datetime import datetime

BASE_DIR    = os.path.join(os.environ.get("USERPROFILE", "D:/JARVIS-AI-Assistant"))
MEMORY_FILE = os.path.join(BASE_DIR, "jarvis_memory.json")

DEFAULT_MEMORY = {
    "facts": [],          # things JARVIS was told to remember: [{text, learned_at}]
    "preferences": {},     # key-value: {"favorite_song": "Tum Hi Ho"}
    "people": {},          # {"daddy": {"phone": "...", "relation": "father"}}
    "instructions": [],    # standing orders: [{text, learned_at, active}]
    "history_summary": [], # short rolling summary of past sessions
}

def _ensure_file():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_MEMORY, f, indent=2, ensure_ascii=False)

def load_memory():
    _ensure_file()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in DEFAULT_MEMORY.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return dict(DEFAULT_MEMORY)

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def remember_fact(text):
    data = load_memory()
    data["facts"].append({"text": text, "learned_at": datetime.now().isoformat()})
    data["facts"] = data["facts"][-200:]  # cap to last 200 facts
    save_memory(data)
    return "Sir, yaad rakh liya: " + text

def remember_preference(key, value):
    data = load_memory()
    data["preferences"][key] = value
    save_memory(data)
    return "Sir, " + key + " = " + value + " save ho gaya."

def remember_person(name, info):
    data = load_memory()
    data["people"][name.lower()] = info
    save_memory(data)
    return "Sir, " + name + " ki details yaad rakh li."

def add_instruction(text):
    data = load_memory()
    data["instructions"].append({"text": text, "learned_at": datetime.now().isoformat(), "active": True})
    save_memory(data)
    return "Sir, ye instruction follow karunga: " + text

def get_active_instructions():
    data = load_memory()
    return [i["text"] for i in data.get("instructions", []) if i.get("active", True)]

def forget_last_fact():
    data = load_memory()
    if data["facts"]:
        removed = data["facts"].pop()
        save_memory(data)
        return "Sir, ye bhula diya: " + removed["text"]
    return "Sir, yaad rakhne ko kuch nahi tha."

def build_memory_context(max_facts=15):
    """Builds a short text block to inject into the Groq system prompt
    so JARVIS 'remembers' things across sessions, like Stonic/Iron Man's JARVIS."""
    data = load_memory()
    lines = []

    if data["preferences"]:
        prefs = "; ".join(f"{k}: {v}" for k, v in data["preferences"].items())
        lines.append("Known preferences -> " + prefs)

    if data["people"]:
        for name, info in data["people"].items():
            detail = ", ".join(f"{k}={v}" for k, v in info.items())
            lines.append(f"Person '{name}' -> {detail}")

    if data["facts"]:
        recent = data["facts"][-max_facts:]
        lines.append("Remembered facts:")
        for f in recent:
            lines.append("- " + f["text"])

    instructions = get_active_instructions()
    if instructions:
        lines.append("Standing instructions to always follow:")
        for ins in instructions:
            lines.append("- " + ins)

    if not lines:
        return ""
    return "\n\nMEMORY (things Pradeep sir has taught JARVIS before):\n" + "\n".join(lines)

def handle_memory_command(text):
    """Detects 'remember/yaad rakho' style commands from voice/chat and stores them.
    Returns a reply string if handled, else None."""
    t = text.lower().strip()

    triggers = ["yaad rakho", "yaad rakhna", "remember this", "remember that",
                "is baat ko yaad rakho", "note kar lo", "mujhe yaad dilana"]
    instruction_triggers = ["hamesha", "jab bhi", "every time", "always",
                             "is se aage se", "ab se"]
    forget_triggers = ["bhool jao", "forget that", "ye bhula do", "delete memory"]

    if any(w in t for w in forget_triggers):
        return forget_last_fact()

    if any(w in t for w in instruction_triggers) and len(t) > 12:
        return add_instruction(text)

    if any(w in t for w in triggers):
        # strip the trigger phrase, keep the actual fact
        fact = text
        for w in triggers:
            fact = fact.lower().replace(w, "")
        fact = fact.strip(" :,-")
        if fact:
            return remember_fact(fact)
        return "Sir, kya yaad rakhna hai bataiye."

    return None

if __name__ == "__main__":
    print("JARVIS Memory file:", MEMORY_FILE)
    print(json.dumps(load_memory(), indent=2, ensure_ascii=False))
