"""
personality_engine.py
Loads soul/personality.json and builds the system prompt JARVIS uses.
Also lets Pradeep sir CHANGE the personality by voice/chat command
("apna naam Stark rakho", "thoda zyada formal baat karo", etc.)
without touching any code.
"""
import os, json
from datetime import datetime

BASE_DIR = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
SOUL_DIR = os.path.join(BASE_DIR, "soul")
os.makedirs(SOUL_DIR, exist_ok=True)
PERSONALITY_FILE = os.path.join(SOUL_DIR, "personality.json")

DEFAULT_PERSONALITY = {
    "name": "JARVIS",
    "owner_calls_me": "JARVIS",
    "addresses_owner_as": "Boss",
    "tone": "warm, direct, energetic, slightly witty",
    "language_mix": "Hinglish",
    "response_length": "short",
    "traits": ["loyal", "proactive", "efficient", "respectful", "occasionally witty"],
    "catchphrases": ["Ho gaya sir!", "Wah sir!", "Samajh gaya sir.", "Ek second sir..."],
    "forbidden_phrases": ["As an AI", "I am an AI language model", "I cannot help with that"],
    "humor_level": "medium",
    "formality_level": "low",
    "voice": "Microsoft David Desktop",
    "version": "1.0",
    "last_updated": datetime.now().isoformat(),
}

def load_personality():
    if not os.path.exists(PERSONALITY_FILE):
        save_personality(DEFAULT_PERSONALITY)
        return dict(DEFAULT_PERSONALITY)
    try:
        with open(PERSONALITY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in DEFAULT_PERSONALITY.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return dict(DEFAULT_PERSONALITY)

def save_personality(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(PERSONALITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_trait(key, value):
    data = load_personality()
    data[key] = value
    save_personality(data)
    return f"Sir, {key} ab '{value}' set ho gaya hai."

def build_personality_prompt():
    """Turns personality.json into a system-prompt text block."""
    p = load_personality()
    lines = [
        f"Your name is {p['name']}. Pradeep sir calls you '{p['owner_calls_me']}'.",
        f"You address him as '{p['addresses_owner_as']}'.",
        f"Your tone is: {p['tone']}.",
        f"You respond primarily in {p['language_mix']}, keeping replies {p['response_length']}.",
        f"Your personality traits: {', '.join(p['traits'])}.",
        f"Humor level: {p['humor_level']}. Formality level: {p['formality_level']}.",
    ]
    if p.get("catchphrases"):
        lines.append("You occasionally use phrases like: " + ", ".join(p["catchphrases"]))
    if p.get("forbidden_phrases"):
        lines.append("NEVER say: " + ", ".join(p["forbidden_phrases"]))
    return "\n".join(lines)


# ---------------- Voice/chat command handling ----------------

def handle_personality_command(text):
    """Detects commands that change JARVIS's personality on the fly."""
    t = text.lower()

    # Rename JARVIS: "apna naam Stark rakho" / "tumhara naam ab Friday hai"
    if ("apna naam" in t or "tumhara naam" in t or "naam rakho" in t) and "rakho" in t or "naam ab" in t:
        words = text.split()
        # naive extraction: last capitalized-looking word, fallback to last word
        candidate = words[-1].strip(" .,!?")
        if candidate.lower() not in ["rakho", "hai", "kar", "do"]:
            return update_trait("name", candidate)

    # Change tone: "thoda formal baat karo" / "casual ho jao" / "zyada serious raho"
    if "formal baat karo" in t or "formal ho jao" in t:
        return update_trait("formality_level", "high")
    if "casual baat karo" in t or "casual ho jao" in t or "relax raho" in t:
        return update_trait("formality_level", "low")
    if "serious raho" in t or "mazak mat karo" in t:
        return update_trait("humor_level", "low")
    if "mazak karo" in t or "funny ho jao" in t or "majedaar baat karo" in t:
        return update_trait("humor_level", "high")

    # Change how owner is addressed: "mujhe sir mat bulao" / "mujhe boss bulao"
    if "mat bulao" in t and ("sir" in t or "boss" in t):
        return update_trait("addresses_owner_as", "Pradeep")
    if "mujhe boss bulao" in t or "boss bulao" in t:
        return update_trait("addresses_owner_as", "Boss")
    if "mujhe sir bulao" in t:
        return update_trait("addresses_owner_as", "Sir")

    # Reset to default
    if "personality reset karo" in t or "default personality" in t:
        save_personality(dict(DEFAULT_PERSONALITY))
        return "Sir, personality default settings pe reset ho gayi."

    # Show current personality
    if "apni personality batao" in t or "tumhari personality" in t or "tum kaise ho describe" in t:
        p = load_personality()
        return (f"Sir, mera naam {p['name']} hai, main aapko '{p['addresses_owner_as']}' bolta hoon, "
                f"tone {p['tone']}, humor level {p['humor_level']}.")

    return None


if __name__ == "__main__":
    print(json.dumps(load_personality(), indent=2, ensure_ascii=False))
    print("\n--- System prompt block ---")
    print(build_personality_prompt())
