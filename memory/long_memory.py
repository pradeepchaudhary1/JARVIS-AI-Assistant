"""
long_memory.py
Permanent, disk-saved memory. This WRAPS your existing jarvis_memory.py
(facts/preferences/people/instructions) and ADDS two new files:
  - user_profile.json    -> who Pradeep sir is, his preferences, brands
  - project_memory.json  -> what projects exist, their status, history

Nothing in your old jarvis_memory.py is removed or broken.
This file just adds two more "drawers" to the same filing cabinet.
"""
import os, json
from datetime import datetime

BASE_DIR = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

USER_PROFILE_FILE    = os.path.join(MEMORY_DIR, "user_profile.json")
PROJECT_MEMORY_FILE  = os.path.join(MEMORY_DIR, "project_memory.json")

# Re-use your existing fact/preference/people/instruction system
try:
    from jarvis_memory import (
        load_memory, save_memory, remember_fact, remember_preference,
        remember_person, add_instruction, get_active_instructions,
        build_memory_context, handle_memory_command
    )
    OLD_MEMORY_OK = True
except Exception:
    OLD_MEMORY_OK = False


# ---------------- USER PROFILE ----------------

DEFAULT_PROFILE = {
    "name": "Pradeep",
    "location": "Kota, Rajasthan",
    "company": "Pradeep Content Empire",
    "brands": ["@lumixbranding", "@_darkfarts_hindi"],
    "communication_style": "Hinglish, direct, short answers",
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
}

def load_user_profile():
    if not os.path.exists(USER_PROFILE_FILE):
        save_user_profile(DEFAULT_PROFILE)
        return dict(DEFAULT_PROFILE)
    try:
        with open(USER_PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_PROFILE)

def save_user_profile(data):
    data["updated_at"] = datetime.now().isoformat()
    with open(USER_PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_user_profile(key, value):
    profile = load_user_profile()
    profile[key] = value
    save_user_profile(profile)
    return f"Sir, profile mein {key} update kar diya: {value}"


# ---------------- PROJECT MEMORY ----------------

DEFAULT_PROJECTS = {
    "projects": [
        {
            "name": "JARVIS AI Assistant",
            "status": "active_development",
            "description": "Personal AI assistant with voice, PC control, web UI",
            "started": datetime.now().isoformat(),
        },
        {
            "name": "Lumix Branding",
            "status": "active",
            "description": "Luxury business card brand on Instagram",
            "started": datetime.now().isoformat(),
        },
        {
            "name": "DarkFacts Hindi",
            "status": "active",
            "description": "Dark facts Instagram content brand",
            "started": datetime.now().isoformat(),
        },
    ]
}

def load_project_memory():
    if not os.path.exists(PROJECT_MEMORY_FILE):
        save_project_memory(DEFAULT_PROJECTS)
        return dict(DEFAULT_PROJECTS)
    try:
        with open(PROJECT_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_PROJECTS)

def save_project_memory(data):
    with open(PROJECT_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_project(name, description="", status="active"):
    data = load_project_memory()
    data["projects"].append({
        "name": name,
        "status": status,
        "description": description,
        "started": datetime.now().isoformat(),
    })
    save_project_memory(data)
    return f"Sir, naya project add kiya: {name}"

def update_project_status(name, new_status):
    data = load_project_memory()
    for p in data["projects"]:
        if p["name"].lower() == name.lower():
            p["status"] = new_status
            p["updated"] = datetime.now().isoformat()
            save_project_memory(data)
            return f"Sir, {name} ka status ab '{new_status}' hai."
    return f"Sir, '{name}' naam ka project nahi mila."

def get_project_summary():
    data = load_project_memory()
    if not data["projects"]:
        return "Sir, abhi koi project track nahi ho raha."
    lines = []
    for p in data["projects"]:
        lines.append(f"{p['name']} ({p['status']})")
    return "Sir, current projects: " + ", ".join(lines)


# ---------------- UNIFIED CONTEXT BUILDER ----------------

def build_full_memory_context():
    """Combines old fact/preference memory + new user profile + project memory
    into one text block to inject into the AI system prompt."""
    parts = []

    profile = load_user_profile()
    parts.append(
        f"USER PROFILE: Name={profile.get('name')}, Location={profile.get('location')}, "
        f"Company={profile.get('company')}, Brands={', '.join(profile.get('brands', []))}, "
        f"Style={profile.get('communication_style')}"
    )

    projects = load_project_memory()
    if projects.get("projects"):
        proj_lines = "; ".join(f"{p['name']} [{p['status']}]" for p in projects["projects"])
        parts.append("ACTIVE PROJECTS: " + proj_lines)

    if OLD_MEMORY_OK:
        old_context = build_memory_context()
        if old_context:
            parts.append(old_context)

    if not parts:
        return ""
    return "\n\nLONG-TERM MEMORY:\n" + "\n".join(parts)


def handle_long_memory_command(text):
    """Routes 'remember/yaad rakho' style commands AND new project commands."""
    t = text.lower()

    # Project tracking commands
    if "naya project" in t or "new project" in t:
        name = text.split("naya project")[-1].split("new project")[-1].strip(" :,-")
        if name:
            return add_project(name)

    if "project status batao" in t or "projects batao" in t or "kya kya project" in t:
        return get_project_summary()

    # Fall back to old fact/instruction memory handler
    if OLD_MEMORY_OK:
        return handle_memory_command(text)

    return None


if __name__ == "__main__":
    print("User Profile:", json.dumps(load_user_profile(), indent=2, ensure_ascii=False))
    print("\nProject Memory:", json.dumps(load_project_memory(), indent=2, ensure_ascii=False))
    print("\nFull context block:")
    print(build_full_memory_context())
