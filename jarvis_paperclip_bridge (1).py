import os, sys, json, threading
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR    = os.path.join(os.environ.get("USERPROFILE", "C:/Users/hp"), "Desktop", "JARVIS-AI-Assistant")
STATUS_FILE = os.path.join(BASE_DIR, "jarvis_status.json")
LOG_FILE    = os.path.join(BASE_DIR, "paperclip_tasks.json")
sys.path.insert(0, BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_OK = True
except ImportError:
    FLASK_OK = False
    print("Run: pip install flask flask-cors")

# ---------- Groq brain (shared with agent.py) ----------
try:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    GROQ_OK = True
except Exception:
    GROQ_OK = False

try:
    from Jarvis_prompts import JARVIS_MAIN_SYSTEM
except ImportError:
    JARVIS_MAIN_SYSTEM = (
        "You are JARVIS, Pradeep sir ka AI assistant. Kota, Rajasthan mein hoon. "
        "Hinglish mein baat karo. Chhote jawab do. Kabhi mat bolo 'As an AI'."
    )

try:
    from jarvis_pc_control import control_pc
    PC_OK = True
except Exception:
    PC_OK = False

try:
    from jarvis_social_lumix import handle_jarvis_command as lumix_cmd
    LUMIX_OK = True
except Exception:
    LUMIX_OK = False

try:
    from jarvis_memory import (
        handle_memory_command, build_memory_context, load_memory
    )
    MEMORY_OK = True
except Exception:
    MEMORY_OK = False

try:
    from jarvis_worldmonitor import handle_worldmonitor_command
    WORLDMONITOR_OK = True
except Exception:
    WORLDMONITOR_OK = False

PRIMARY_MODEL = "llama-3.1-8b-instant"
BACKUP_MODEL  = "llama-3.3-70b-versatile"

# simple in-memory chat history for the web UI session
WEB_CONVERSATION = []

def get_ai_reply(user_text, use_backup=False):
    if not GROQ_OK:
        return "Sir, GROQ_API_KEY missing hai .env mein."
    model = BACKUP_MODEL if use_backup else PRIMARY_MODEL

    system_prompt = JARVIS_MAIN_SYSTEM
    if MEMORY_OK:
        system_prompt += build_memory_context()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(WEB_CONVERSATION[-10:])
    messages.append({"role": "user", "content": user_text})
    try:
        resp = client.chat.completions.create(
            model=model, messages=messages, max_tokens=150, temperature=0.85
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        if not use_backup:
            return get_ai_reply(user_text, use_backup=True)
        return "Sir, thoda issue aa gaya. Phir se try karo."

def handle_web_command(text):
    """Same routing logic as agent.py's handle_command(), reused for the web UI."""
    t = text.lower()

    if PC_OK:
        pc_result = control_pc(t)
        if pc_result:
            return pc_result, "pc_control"

    # Memory / learning commands - "yaad rakho", "hamesha...", "bhool jao"
    if MEMORY_OK:
        mem_result = handle_memory_command(text)
        if mem_result:
            return mem_result, "memory"

    # WorldMonitor - news/headlines
    if WORLDMONITOR_OK:
        wm_result = handle_worldmonitor_command(text)
        if wm_result:
            return wm_result, "worldmonitor"

    if any(w in t for w in ["lumix", "business card", "card post karo", "card dalo"]):
        if LUMIX_OK:
            return lumix_cmd(text), "lumix_post"
        return "Sir, Lumix ke liye ZAPIER_WEBHOOK_URL .env mein set karo.", "lumix_post"

    if any(w in t for w in ["time kya hai", "kitne baje", "samay", "what is the time"]):
        return "Sir, abhi " + datetime.now().strftime("%I:%M %p") + " baj rahe hain.", "get_time"

    if any(w in t for w in ["what is the date", "date kya hai", "aaj ki date"]):
        return "Sir, aaj " + datetime.now().strftime("%d %B %Y") + " hai.", "get_date"

    if any(w in t for w in ["status", "system check", "kya chal raha"]):
        parts = ["Sir sab theek hai!"]
        if LUMIX_OK: parts.append("Lumix ON")
        if PC_OK: parts.append("PC Control ON")
        if MEMORY_OK: parts.append("Memory ON")
        if WORLDMONITOR_OK: parts.append("WorldMonitor ON")
        parts.append("Bridge ON")
        return " | ".join(parts), "system_status"

    return None, None

def _load_status():
    try:
        with open(STATUS_FILE) as f:
            return json.load(f)
    except Exception:
        return {"status": "unknown"}

def _log_task(data):
    tasks = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                tasks = json.load(f)
        except Exception:
            pass
    tasks.append({**data, "timestamp": datetime.now().isoformat()})
    with open(LOG_FILE, "w") as f:
        json.dump(tasks[-100:], f, indent=2)

if FLASK_OK:
    app = Flask(__name__)
    CORS(app)  # allow jarvis_app.html (opened as file://) to call this API

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "online", "agent": "JARVIS",
            "timestamp": datetime.now().isoformat(),
            "groq": GROQ_OK, "pc_control": PC_OK, "lumix": LUMIX_OK,
            "memory": MEMORY_OK, "worldmonitor": WORLDMONITOR_OK,
        })

    @app.route("/memory", methods=["GET"])
    def get_memory():
        if not MEMORY_OK:
            return jsonify({"error": "memory module not loaded"}), 500
        return jsonify(load_memory())

    # ---------- NEW: Web UI chat endpoint ----------
    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json(force=True) or {}
        text = (data.get("message") or "").strip()
        if not text:
            return jsonify({"error": "message required"}), 400

        print("[WebUI] User:", text)

        # 1. Try built-in commands first (PC control, Lumix, time, status)
        result, tool_used = handle_web_command(text)
        if result:
            WEB_CONVERSATION.append({"role": "user", "content": text})
            WEB_CONVERSATION.append({"role": "assistant", "content": result})
            _log_task({"source": "web_ui", "input": text, "reply": result, "tool": tool_used})
            return jsonify({"reply": result, "tool": tool_used})

        # 2. Otherwise fall back to Groq AI chat
        reply = get_ai_reply(text)
        WEB_CONVERSATION.append({"role": "user", "content": text})
        WEB_CONVERSATION.append({"role": "assistant", "content": reply})
        if len(WEB_CONVERSATION) > 20:
            del WEB_CONVERSATION[:-20]
        _log_task({"source": "web_ui", "input": text, "reply": reply, "tool": "ai_chat"})
        return jsonify({"reply": reply, "tool": "ai_chat"})

    @app.route("/task", methods=["POST"])
    def handle_task():
        data      = request.get_json(force=True) or {}
        task      = data.get("task", "")
        task_type = data.get("type", "general")
        print("[Paperclip] Task:", task_type, "-", task[:60])
        _log_task({"task": task, "type": task_type, "status": "received"})
        return jsonify({"accepted": True, "task": task, "type": task_type})

    @app.route("/status", methods=["GET"])
    def get_status():
        tasks = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE) as f:
                    tasks = json.load(f)
            except Exception:
                pass
        return jsonify({"jarvis": _load_status(), "recent_tasks": tasks[-5:]})

    @app.route("/run", methods=["POST"])
    def run_pipeline():
        data  = request.get_json(force=True) or {}
        topic = data.get("topic", "")
        if not topic:
            return jsonify({"error": "topic required"}), 400
        def bg():
            try:
                from phase1_research_seo_script import run_phase1
                from phase2_thumbnail_upload    import run_phase2
                p1 = run_phase1(topic)
                p2 = run_phase2(p1, None, 0)
                _log_task({"type": "full_pipeline", "topic": topic, "status": "complete"})
                print("[Pipeline] Complete:", topic)
            except Exception as e:
                print("[Pipeline] Error:", e)
        threading.Thread(target=bg, daemon=True).start()
        return jsonify({"accepted": True, "topic": topic, "message": "Pipeline shuru ho gayi"})

def main():
    if not FLASK_OK:
        print("Run: pip install flask flask-cors")
        return
    print("=" * 45)
    print("  JARVIS <-> Web UI Bridge")
    print("  Port: 8765")
    print("  Groq:", GROQ_OK, "| PC Control:", PC_OK, "| Lumix:", LUMIX_OK)
    print("  Memory:", MEMORY_OK, "| WorldMonitor:", WORLDMONITOR_OK)
    print("  LAN access -> http://<your-PC-IP>:8765  (phone same WiFi)")
    print("=" * 45)
    app.run(host="0.0.0.0", port=8765, debug=False)

if __name__ == "__main__":
    main()
