import os
import sys
import time
import threading
import speech_recognition as sr
import pyttsx3
import random
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import requests as _requests
engine=pyttsx3.init()

BASE_DIR = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
sys.path.insert(0, BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Optional imports
try:
    from Jarvis_prompts import JARVIS_MAIN_SYSTEM
except ImportError:
    JARVIS_MAIN_SYSTEM = """
        "You are JARVIS AI Assistant for Pradeep sir."
    VOICE MODE RULES:

        If selected voice is Hindi / Indian voice:
        - Reply in natural Hindi or Hinglish.
        - Use Indian speaking style.
        - Hindi words must be written normally.
        - Do not spell words letter by letter.
        - Example:
          Correct: "Ho gaya Boss"
          Wrong: "H O G A Y A Boss"
        - STOP/Ruko/Chup suno to turant chup ho jao.
        - Use normal Hindi pronunciation.

        If selected voice is Indian English voice:
        - Reply only in natural English.
        - Do not use Hindi words.
        - Speak like a professional assistant.

        If selected voice is US/UK/Australian:
        - Use that country's natural English style.

        General rules:
        - Keep answers short.
        - Never say "As an AI".
        - You are Pradeep sir's personal assistant.
        - Understand Hindi, English and Hinglish commands.

        IMPORTANT:

        Never claim that you have clicked anything.
        Never say
        Message sent
        Screenshot taken
        Face registered
        Voice registered
        Whatsapp checked
        unless a Python tool actually executed it.
        If you cannot access something say
        "I cannot verify that."

        Never guess screen contents
        Never pretend to see monitor.
        Never pretend to read WhatsApp.
        Never pretend camera is active.
        If screen analysis is unavailable simply say
        "I cannot see your screen."
"""

try:
    from jarvis_social_lumix import handle_jarvis_command as lumix_cmd
    LUMIX_OK = True
except Exception:
    LUMIX_OK = False

try:
    from jarvis_get_whether import get_weather
    WEATHER_OK = True
except Exception:
    WEATHER_OK = False

try:
    from jarvis_pc_control import control_pc
    PC_OK = True
except Exception:
    PC_OK = False

try:
    from jarvis_memory import handle_memory_command, build_memory_context
    MEMORY_OK = True
except Exception:
    MEMORY_OK = False

try:
    sys.path.insert(0, BASE_DIR)
    from memory.long_memory import (
        handle_long_memory_command, build_full_memory_context, load_user_profile
    )
    from memory.short_memory import short_mem
    LONG_MEMORY_OK = True
except Exception:
    LONG_MEMORY_OK = False

try:
    sys.path.insert(0, BASE_DIR)
    from soul.personality_engine import (
        build_personality_prompt, handle_personality_command, load_personality
    )
    PERSONALITY_OK = True
except Exception:
    PERSONALITY_OK = False

try:
    from jarvis_worldmonitor import handle_worldmonitor_command
    WORLDMONITOR_OK = True
except Exception:
    WORLDMONITOR_OK = False

try:
    from jarvis_pc_stats import handle_pc_stats_command
    PC_STATS_OK = True
except Exception:
    PC_STATS_OK = False

try:
    from jarvis_voice_manager import (
        get_current_voice_id, handle_voice_command, list_installed_voices
    )
    VOICE_MANAGER_OK = True
except Exception:
    VOICE_MANAGER_OK = False

try:
    import requests as _req
    _r = _req.get("http://localhost:8765/health", timeout=2)
    PAPERCLIP_OK = _r.status_code == 200
except Exception:
    PAPERCLIP_OK = False

# Models
PRIMARY_MODEL = "llama-3.1-8b-instant"
BACKUP_MODEL  = "llama-3.3-70b-versatile"
OLLAMA_MODEL    = "hermes3:latest"
OLLAMA_URL      = "http://127.0.0.1:11434/api/tags"

# Groq client
GROQ_KEY=os.getenv("GROQ_API_KEY","").strip()

client=None

if GROQ_KEY:
    client=Groq(api_key=GROQ_KEY)

# Ollama availability check
def _check_ollama():
    try:
        r = _requests.get("http://127.0.0.1:11434", timeout=2)
        return r.status_code == 200
    except:
        return False
if _check_ollama():
OLLAMA_AVAILABLE =_check_ollama()
print(f"[JARVIS] Ollama available: {OLLAMA_AVAILABLE}")

def query_llm(messages, model=PRIMARY_MODEL):
    global OLLAMA_AVAILABLE
    
    # Groq try karo pehle
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[JARVIS] Groq failed: {e}")
            print("[JARVIS] Ollama pe switch kar raha/rahi hun...")
    
    # Ollama fallback
    if _check_ollama():
        try:
            r = _requests.post(OLLAMA_URL, json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False
            }, timeout=60)
            return r.json()["message"]["content"]
        except Exception as e:
            print(f"[JARVIS] Ollama bhi fail: {e}")
            return "Dono AI offline hain Boss, check karo."
    
    return "Groq API key nahi hai aur Ollama bhi nahi mila Boss."

# ================================
# JARVIS UNIVERSAL VOICE SYSTEM
# ================================

_temp_engine = pyttsx3.init()

voices = _temp_engine.getProperty('voices')

VOICE_FILE = os.path.join(BASE_DIR,"voice_config.json")


def get_all_voices():

    result={}

    for v in voices:
        result[v.name]=v.id

    return result



def load_voice():

    if os.path.exists(VOICE_FILE):

        try:
            with open(
                VOICE_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data=json.load(f)

                saved=data.get("selected_voice_id")

                for v in voices:
                    if v.id==saved:
                        return saved

        except:
            pass


    # Default priority
    priority=[
        "Kalpana",
        "Heera",
        "Ravi",
        "Hemant"
    ]


    for p in priority:

        for v in voices:

            if p.lower() in v.name.lower():
                return v.id


    return voices[0].id



selected = load_voice()



def save_voice():

    name="Unknown"

    for v in voices:
        if v.id==selected:
            name=v.name


    with open(
        VOICE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
        {
        "selected_voice_id":selected,
        "selected_voice_name":name
        },
        f,
        indent=4
        )



save_voice()


_current=[
v.name for v in voices if v.id==selected
]


print(
"JARVIS Voice ->",
_current[0] if _current else "default"
)


_temp_engine.stop()
del _temp_engine

# Speech recognition
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1.0

# State
class State:
    paused          = False
    speaking        = False
    last_user_time  = time.time()
    wait_start_time = None
    silence_asked   = False
    conversation    = []

ST = State()

STOP_WORDS = [
    "stop", "ruko", "chup", "wait", "bas", "ek second",
    "ruk jao", "chup raho", "stop jarvis", "wait jarvis",
    "ruko jarvis", "hold on", "ek minute", "abhi nahi",
    "thoda ruko", "ruk", "silence"
]
RESUME_WORDS = [
    "ab baat karo", "ha ab bolo", "theek hai", "ok jarvis",
    "continue", "ab baat kar skte", "resume", "baat karo",
    "haan", "ha", "yes", "chalo", "ab bolo", "bol"
]

def speak(text):
    if ST.paused:
        return

    ST.speaking = True

    print("[JARVIS]", text)

    try:
        engine = pyttsx3.init()

        engine.setProperty(
            "voice",
            selected
        )

        # Normal human speed
        engine.setProperty(
            "rate",
            155
        )

        engine.setProperty(
            "volume",
            1.0
        )

        # Hindi voice ke liye
        voice_text = str(selected)

        if "hiIN" in voice_text or "Kalpana" in voice_text or "Hemant" in voice_text:


            # Hinglish ko Hindi script me convert karne ki zarurat nahi
            # lekin speed slow rakho
            engine.setProperty("rate", 130)


        # English voices
        else:
            engine.setProperty("rate", 165)


        engine.say(text)

        engine.runAndWait()

        engine.stop()


    except Exception as e:
        print("[TTS ERROR]",e)


    finally:
        ST.speaking=False

def query_ai(user_input, use_backup=False):
    model = BACKUP_MODEL if use_backup else PRIMARY_MODEL

    if PERSONALITY_OK:
        system_prompt = build_personality_prompt()   # personality.json drives the core identity
    else:
        system_prompt = JARVIS_MAIN_SYSTEM             # fallback to hardcoded prompt

    if LONG_MEMORY_OK:
        system_prompt += build_full_memory_context()   # includes old memory + profile + projects
    elif MEMORY_OK:
        system_prompt += build_memory_context()          # fallback to old-only if new module missing
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(ST.conversation[-10:])
    messages.append({"role": "user", "content": user_input})
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=120,
            temperature=0.85,
            stream=True
        )
        full = ""
        for chunk in stream:
            if ST.paused:
                break
            delta = chunk.choices[0].delta.content or ""
            full += delta
        return full.strip()
    except Exception as e:
        print("[Groq Error]", repr(e))
        if not use_backup:
            return get_ai_response(user_input, use_backup=True)
        return "Sir, thoda issue aa gaya. Ek baar phir bolein?"

def handle_command(text):
    global selected

    t = text.lower()

    # PC control - apps, lock, notepad (check FIRST)
    if PC_OK:
        pc_result = control_pc(t)
        if pc_result:
            return pc_result

    # Personality commands - "apna naam ... rakho", "formal baat karo", etc.
    if PERSONALITY_OK:
        personality_result = handle_personality_command(text)
        if personality_result:
            return personality_result

    # Voice switching
    if VOICE_MANAGER_OK:
        voice_result = handle_voice_command(text)

        if voice_result:
            global selected

            new_id = get_current_voice_id()

            if new_id:
                selected = new_id

            return voice_result + " Ab se naya voice use hoga."

    # Memory / learning commands - "yaad rakho", "hamesha...", "bhool jao", "naya project"
    if LONG_MEMORY_OK:
        mem_result = handle_long_memory_command(text)
        if mem_result:
            return mem_result
    elif MEMORY_OK:
        mem_result = handle_memory_command(text)
        if mem_result:
            return mem_result

    # WorldMonitor - news/headlines
    if WORLDMONITOR_OK:
        wm_result = handle_worldmonitor_command(text)
        if wm_result:
            return wm_result

    if any(w in t for w in ["lumix", "business card", "card post karo", "card dalo"]):
        if LUMIX_OK:
            return lumix_cmd(text)
        return "Sir, Lumix ke liye ZAPIER_WEBHOOK_URL .env mein set karo."

    if any(w in t for w in ["video banao", "youtube pipeline", "video bana"]):
        if PAPERCLIP_OK:
            try:
                topic = t.replace("video banao", "").replace("video bana", "").strip() or "AI tools 2026"
                import requests
                requests.post("http://localhost:8765/run", json={"topic": topic}, timeout=5)
                return "Sir! Pipeline shuru ho gayi " + topic + " ke liye!"
            except Exception:
                return "Sir, Paperclip bridge chalu nahi hai. START_JARVIS.bat run karo."
        return "Sir, bridge band hai. START_JARVIS.bat chalao pehle."

    if any(w in t for w in ["weather", "mausam", "barish"]):
        if WEATHER_OK:
            try:
                return get_weather("Karauli")
            except Exception:
                pass
        return "Weather module set nahi abhi sir."

    if any(w in t for w in [
         "time kya hai", "kitne baje", "samay", "what is the time", "what's the time",
         "time kya ho", "time batao", "abhi kitne baje", "time bata", "kya time hai",
         "baj rahe hain", "baje hain", "kya baj raha"
    ]):
        return "Sir, abhi " + datetime.now().strftime("%I:%M %p") + " baj rahe hain."

    if any(w in t for w in ["what is the date", "date kya hai", "aaj ki date"]):
        return "Sir, aaj " + datetime.now().strftime("%d %B %Y") + " hai."

    if any(w in t for w in ["status", "system check", "kya chal raha"]):
        parts = ["Sir sab theek hai!"]
        if PAPERCLIP_OK:
            parts.append("Paperclip ON")
        if LUMIX_OK:
            parts.append("Lumix ON")
        if PC_OK:
            parts.append("PC Control ON")
        if MEMORY_OK:
            parts.append("Memory ON")
        if LONG_MEMORY_OK:
            parts.append("LongMemory ON")
        if PERSONALITY_OK:
            parts.append("Personality ON")
        if WORLDMONITOR_OK:
            parts.append("WorldMonitor ON")
        if VOICE_MANAGER_OK:
            parts.append("VoiceManager ON")
        return " | ".join(parts)

    return None

def silence_monitor():
    while True:
        time.sleep(5)
        if ST.paused and not ST.speaking:
            elapsed = time.time() - (ST.wait_start_time or ST.last_user_time)
            if elapsed > 30 and not ST.silence_asked:
                ST.silence_asked = True
                replies = [
                    "Sir... kya ab baat kar sakte hain?",
                    "Sir, main aapka intezaar kar raha/rahi hoon.",
                    "Ji sir, jab ready ho batao.",
                ]
                speak(random.choice(replies))
            elif elapsed > 300 and ST.silence_asked:
                speak("Ok sir, main background mein hoon. Zaroorat ho to bulao.")
                ST.silence_asked = False
                ST.wait_start_time = time.time()

def listen_once(timeout=8):
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=0.3)
        try:
            audio = recognizer.listen(mic, timeout=timeout, phrase_time_limit=10)
            return recognizer.recognize_google(audio, language="en-IN").strip()
        except Exception:
            return None

def is_stop(text):
    t = text.lower()
    return any(w in t for w in STOP_WORDS)

def is_resume(text):
    t = text.lower()
    return any(w in t for w in RESUME_WORDS)

def process(text):
    ST.last_user_time = time.time()
    ST.silence_asked  = False

    if LONG_MEMORY_OK:
        short_mem.add("user", text)

    # Stop command
    if is_stop(text):
        ST.paused = True
        ST.wait_start_time = time.time()
        try:
            pass
        except Exception:
            pass
        ack = random.choice([
            "Ok sir.", "Theek hai sir, chup hoon.",
            "Ji, ruk gaya/gayi.", "Ok, wait kar raha/rahi hoon."
        ])
        print("[JARVIS - PAUSED]", ack)
        try:
            local_engine = pyttsx3.init()
            local_engine.setProperty('voice', selected)
            local_engine.setProperty('rate', 170)
            local_engine.say(ack)
            local_engine.runAndWait()
            local_engine.stop()
            del local_engine
        except Exception:
            pass
        return

    # Resume command
    if ST.paused and is_resume(text):
        ST.paused = False
        ST.silence_asked = False
        greet = random.choice([
            "Haan sir! Bataiye.",
            "Ji sir, bol dijiye!",
            "Theek hai sir, ab bolo!",
        ])
        speak(greet)
        return

    # Ignore if paused
    if ST.paused:
        return

    # Built-in commands
    result = handle_command(text)
    if result:
        speak(result)
        ST.conversation.append({"role": "user", "content": text})
        ST.conversation.append({"role": "assistant", "content": result})
        if LONG_MEMORY_OK:
            short_mem.add("assistant", result)
        return

    # AI response
    print("[You]", text)
    response = query_ai(text)
    if response and not ST.paused:
        speak(response)
        ST.conversation.append({"role": "user", "content": text})
        ST.conversation.append({"role": "assistant", "content": response})
        if LONG_MEMORY_OK:
            short_mem.add("assistant", response)
        if len(ST.conversation) > 20:
            ST.conversation = ST.conversation[-20:]

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning sir! JARVIS ready hai. Kya karna hai aaj?"
    elif 12 <= hour < 17:
        return "Good afternoon sir! JARVIS ready hai. Kya karna hai?"
    elif 17 <= hour < 21:
        return "Good evening sir! JARVIS ready hai. Kya karna hai?"
    else:
        return "JARVIS ready hai sir, itni raat ko bhi kaam kar rahe ho? Kya karna hai?"

def main():
    print("=" * 45)
    print("  JARVIS AI Assistant - Online")
    print("  Pradeep Content Empire")
    print("=" * 45)
    print("  Say 'Jarvis' + command")
    print("  Say 'Stop/Ruko' to pause")
    print("  Ctrl+C to quit")
    print("=" * 45 + "\n")

    threading.Thread(target=silence_monitor, daemon=True).start()
    time.sleep(0.5)
    speak(get_greeting())

    while True:
        try:
            text = listen_once(timeout=10)
            if not text:
                continue
            print("[Heard]", text)
            t = text.lower()

            if t in ["quit", "exit", "band karo", "bye jarvis", "bye"]:
                speak("Ok sir, band kar raha/rahi hoon. Alvida!")
                break

            # STOP — highest priority
            if is_stop(t):
                process(t)
                continue

            # VOICE CHANGE — second priority, no wake word needed
            if VOICE_MANAGER_OK and any(w in t for w in [
                "voice lagao", "voice change", "male voice", "female voice",
                "awaaz lagao", "awaaz change", "voices batao", "available voices"
            ]):
                voice_result = handle_voice_command(text)
                selected = get_current_voice_id(selected)
                if voice_result:
                    # Apply new voice to currently running instance immediately
                    new_id = get_current_voice_id()
                    if new_id:
                        selected = new_id
                    speak(voice_result)
                    continue

            if "jarvis" in t or "jarviz" in t or "jarbis" in t:
                cmd = t
                for w in ["hey jarvis", "ok jarvis", "jarvis", "jarviz", "jarbis"]:
                    cmd = cmd.replace(w, "")
                cmd = cmd.strip()
                if cmd:
                    process(cmd)
                else:
                    speak(random.choice(["Haan sir?", "Ji sir?", "Bataiye!", "Haan, bol dijiye!"]))
            else:
                process(t)

        except KeyboardInterrupt:
            speak("Ok sir, bye!")
            break
        except Exception as e:
            print("[Error]", e)
            time.sleep(1)

if __name__ == "__main__":
    main()
