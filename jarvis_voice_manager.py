"""
jarvis_voice_manager.py
Voice switching system for JARVIS - calibrated to actual installed voices.
Pradeep sir's PC has these confirmed voices (from check_voices.py output):
  Indian Male:    Ravi (en-IN), Hemant (hi-IN)
  Indian Female:  Heera (en-IN), Kalpana (hi-IN)
  US Female:      Zira Desktop, Zira
  AU Male:        James
  AU Female:      Catherine
"""
import os, json, pyttsx3

BASE_DIR         = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
VOICE_CONFIG_FILE = os.path.join(BASE_DIR, "voice_config.json")

DEFAULT_CONFIG = {"selected_voice_id": None, "selected_voice_name": None}

# Exact keyword matches based on confirmed check_voices.py output
VOICE_PROFILES = {
    "indian_male":   {"keywords": ["ravi"],    "label": "Indian English Male (Ravi)"},
    "hindi_male":    {"keywords": ["hemant"],  "label": "Hindi Male (Hemant)"},
    "indian_female": {"keywords": ["heera"],   "label": "Indian English Female (Heera)"},
    "hindi_female":  {"keywords": ["kalpana"], "label": "Hindi Female (Kalpana)"},
    "us_male":       {"keywords": ["david desktop", "david"], "label": "US Male (David)"},
    "us_female":     {"keywords": ["zira desktop", "zira"],   "label": "US Female (Zira)"},
    "us_male_mark":  {"keywords": ["mark"],    "label": "US Male (Mark)"},
    "au_male":       {"keywords": ["james"],   "label": "Australian Male (James)"},
    "au_female":     {"keywords": ["catherine"], "label": "Australian Female (Catherine)"},
}

# Voice command trigger phrases -> profile key
VOICE_COMMAND_MAP = {
    # Indian English
    "indian male voice":        "indian_male",
    "ravi voice":               "indian_male",
    "india male":               "indian_male",
    "indian female voice":      "indian_female",
    "heera voice":              "indian_female",
    # Hindi
    "hindi male voice":         "indian_hindi_male",
    "hemant voice":             "indian_hindi_male",
    "hindi female voice":       "indian_hindi_female",
    "kalpana voice":            "indian_hindi_female",
    # US
    "us male voice":            "us_male",
    "david voice":              "us_male",
    "english male voice":       "us_male",
    "us female voice":          "us_female",
    "zira voice":               "us_female",
    "english female voice":     "us_female",
    "mark voice":               "us_male_mark",
    # Australian
    "australian male voice":    "au_male",
    "james voice":              "au_male",
    "australia male":           "au_male",
    "australian female voice":  "au_female",
    "catherine voice":          "au_female",
    "australia female":         "au_female",
    # Hindi shortcuts
    "mard awaaz":               "indian_male",
    "aurat awaaz":              "indian_female",
    "hindi mard awaaz":         "indian_male",
    "hindi aurat awaaz":        "indian_female",
    "male voice lagao":         "indian_male",
    "female voice lagao":       "indian_female",
    "default voice":            "indian_english_male",
}

def _get_all_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    result = [{"id": v.id, "name": v.name} for v in voices]
    engine.stop()
    del engine
    return result

def load_voice_config():
    if not os.path.exists(VOICE_CONFIG_FILE):
        save_voice_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        with open(VOICE_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_voice_config(data):
    with open(VOICE_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_voice_by_profile(profile_key):

    profile = VOICE_PROFILES.get(profile_key)

    if not profile:
        return None


def get_all_voice_names():

    voices=_get_all_voices()

    return [
        v["name"]
        for v in voices
    ]

    for v in voices:

        name=v["name"].lower()
        vid=v["id"].lower()


        for kw in profile["keywords"]:

            if kw in name or kw in vid:

                return v


    return None

def set_voice(profile_key):
    voice = find_voice_by_profile(profile_key)
    label = VOICE_PROFILES.get(profile_key, {}).get("label", profile_key)
    if not voice:
        return False, f"Sir, '{label}' voice nahi mili (unexpected)."
    save_voice_config({
        "selected_voice_id":   voice["id"],
        "selected_voice_name": voice["name"],
    })
    return True, f"Sir, voice ab '{voice['name']}' set ho gayi hai! JARVIS restart hote hi naya voice load hoga."

def get_all_voice_id(fallback_id=None):
    config = load_voice_config()
    return config.get("selected_voice_id") or fallback_id

def describe_available_voices():
    voices = _get_all_voices()
    key_voices = [v for v in voices if any(
        kw in v["name"].lower()
        for kw in ["mark", "zira", "ravi", "heera", "hemant", "kalpana", "james", "catherine", "david"]
    )]
    if not key_voices:
        return "Sir, koi familiar voice nahi mila."
    names = [v["name"] for v in key_voices]
    return "Sir, ye voices available hain: " + ", ".join(names)

def list_installed_voices():

    engine=pyttsx3.init()

    voices=engine.getProperty("voices")

    data=[]

    for v in voices:

        data.append(
        {
        "name":v.name,
        "id":v.id
        })

    engine.stop()

    return data

def handle_voice_command(text):
    t = text.lower()

    if any(w in t for w in ["available voices", "kaunsi awaaz", "voice list batao",
                              "awaaz list", "voices batao"]):
        return describe_available_voices()

    # Try all command map entries (longest first to avoid partial matches)
    for phrase in sorted(VOICE_COMMAND_MAP.keys(), key=len, reverse=True):
        if phrase in t:
            profile_key = VOICE_COMMAND_MAP[phrase]
            ok, msg = set_voice(profile_key)
            return msg

    return None

if __name__ == "__main__":
    print(describe_available_voices())
    print("\nTesting: set Indian male voice (Ravi)...")
    ok, msg = set_voice("indian_male")
    print(msg)
