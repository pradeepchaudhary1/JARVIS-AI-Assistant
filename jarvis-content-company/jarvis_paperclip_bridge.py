"""
JARVIS ↔ Paperclip Bridge Server
Paperclip is ko call karta hai JARVIS ko tasks dene ke liye.

Install: pip install flask
Run: python jarvis_paperclip_bridge.py
Port: 8765
"""
import os, json, asyncio, threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from flask import Flask, request, jsonify
    FLASK_OK = True
except ImportError:
    FLASK_OK = False
    print("❌ Flask nahi mila. Run: pip install flask")

STATUS_FILE = os.path.join(os.path.dirname(__file__), "jarvis_status.json")
LOG_FILE    = os.path.join(os.path.dirname(__file__), "paperclip_tasks.json")


def _load_status() -> dict:
    try:
        with open(STATUS_FILE) as f:
            return json.load(f)
    except Exception:
        return {"status": "unknown"}


def _log_task(data: dict):
    tasks = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                tasks = json.load(f)
        except Exception:
            pass
    tasks.append({**data, "timestamp": datetime.now().isoformat()})
    with open(LOG_FILE, "w") as f:
        json.dump(tasks[-100:], f, indent=2)  # Last 100 tasks


def _run_crew_task(task_type: str, topic: str) -> dict:
    """Background mein crew task run karo"""
    try:
        if task_type == "youtube_pipeline":
            from phase1_research_seo_script import run_phase1
            result = run_phase1(topic)
            return {
                "status": "success",
                "type": task_type,
                "topic": topic,
                "script_file": result.get("script", {}).get("script_file", ""),
                "title": result.get("seo", {}).get("seo", {}).get("title", ""),
                "words": result.get("script", {}).get("word_count", 0)
            }
        elif task_type == "social_post":
            import requests
            zapier_url = os.getenv("ZAPIER_WEBHOOK_URL")
            if zapier_url:
                r = requests.post(zapier_url, json={"content": topic}, timeout=10)
                return {"status": "success", "type": task_type, "posted": True}
            return {"status": "error", "message": "ZAPIER_WEBHOOK_URL missing"}
        elif task_type == "upwork_proposal":
            from jarvis_crew_bridge import handle_client_task
            # Run in event loop
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(handle_client_task(topic))
            return {"status": "success", "type": task_type, "result": result}
        else:
            return {"status": "received", "type": task_type, "task": topic,
                    "message": "JARVIS ne task receive kar liya"}
    except Exception as e:
        return {"status": "error", "error": str(e), "type": task_type}


if FLASK_OK:
    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health():
        """Paperclip check karta hai JARVIS online hai ya nahi"""
        jarvis_status = _load_status()
        return jsonify({
            "status": "online",
            "agent": "JARVIS",
            "jarvis_status": jarvis_status.get("status", "unknown"),
            "timestamp": datetime.now().isoformat()
        })

    @app.route('/task', methods=['POST'])
    def handle_task():
        """
        Paperclip se task receive karo.
        Body: {"task": "topic", "type": "youtube_pipeline|social_post|upwork_proposal|general"}
        """
        data       = request.get_json(force=True) or {}
        task       = data.get("task", "")
        task_type  = data.get("type", "general")
        agent      = data.get("agent", "ceo")

        print(f"\n📋 Paperclip task received:")
        print(f"   Type: {task_type}")
        print(f"   Task: {task[:80]}")
        print(f"   Agent: {agent}")

        _log_task({"task": task, "type": task_type, "agent": agent,
                   "status": "received"})

        # Background mein run karo taaki Flask block na ho
        def bg():
            result = _run_crew_task(task_type, task)
            _log_task({**result, "task": task, "completed": True})
            print(f"✅ Task complete: {result.get('status')}")

        t = threading.Thread(target=bg, daemon=True)
        t.start()

        return jsonify({
            "accepted": True,
            "task":     task,
            "type":     task_type,
            "message":  f"JARVIS ne task accept kar liya — background mein process ho raha hai",
            "check_status": "GET /status"
        })

    @app.route('/status', methods=['GET'])
    def get_status():
        """Recent tasks ka status"""
        tasks = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE) as f:
                    tasks = json.load(f)
            except Exception:
                pass
        return jsonify({
            "jarvis": _load_status(),
            "recent_tasks": tasks[-5:],
            "total_tasks": len(tasks)
        })

    @app.route('/agents', methods=['GET'])
    def list_agents():
        """Available JARVIS agents"""
        return jsonify({
            "agents": [
                {"id": "ceo",        "name": "CEO",           "status": "active"},
                {"id": "researcher", "name": "Research Analyst","status": "active"},
                {"id": "writer",     "name": "Script Writer",  "status": "active"},
                {"id": "seo",        "name": "SEO Manager",    "status": "active"},
                {"id": "social",     "name": "Social Media",   "status": "active"},
                {"id": "client",     "name": "Client Handler", "status": "active"},
            ]
        })

    @app.route('/run', methods=['POST'])
    def run_pipeline():
        """
        Full pipeline run karo.
        Body: {"topic": "AI tools 2026", "schedule_hours": 0}
        """
        data          = request.get_json(force=True) or {}
        topic         = data.get("topic", "")
        schedule_hrs  = data.get("schedule_hours", 0)

        if not topic:
            return jsonify({"error": "topic required"}), 400

        def bg_pipeline():
            try:
                from phase1_research_seo_script import run_phase1
                from phase2_thumbnail_upload    import run_phase2
                p1 = run_phase1(topic)
                p2 = run_phase2(p1, None, schedule_hrs)
                _log_task({
                    "type":      "full_pipeline",
                    "topic":     topic,
                    "status":    "complete",
                    "title":     p1.get("seo",{}).get("seo",{}).get("title",""),
                    "thumbnail": p2.get("thumbnail",{}).get("image_path",""),
                    "completed": True
                })
                print(f"✅ Pipeline complete: {topic}")
            except Exception as e:
                print(f"❌ Pipeline error: {e}")

        threading.Thread(target=bg_pipeline, daemon=True).start()

        return jsonify({
            "accepted": True,
            "topic":    topic,
            "schedule": f"{schedule_hrs}h" if schedule_hrs else "immediate",
            "message":  "Pipeline shuru ho gayi — /status pe check karo"
        })


def main():
    if not FLASK_OK:
        print("pip install flask karke dobara run karo")
        return

    print("\n" + "="*50)
    print("  JARVIS ↔ Paperclip Bridge Server")
    print("="*50)
    print(f"  Port: 8765")
    print(f"  Endpoints:")
    print(f"    GET  /health    — JARVIS online check")
    print(f"    POST /task      — Task assign karo")
    print(f"    GET  /status    — Recent tasks status")
    print(f"    GET  /agents    — Available agents")
    print(f"    POST /run       — Full pipeline run")
    print("="*50)
    print(f"\n  Paperclip config mein add karo:")
    print(f"  bridgeUrl: http://localhost:8765")
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=8765, debug=False)


if __name__ == '__main__':
    main()
