"""
JARVIS ↔ Multi-Agent Bridge — Phase 3
Jarvis voice commands ko pipeline se connect karta hai
"""
import os, json, asyncio
from datetime import datetime
from dotenv import load_dotenv
from livekit.agents import function_tool

# ✅ FIX: Telemetry disable
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY"]  = "false"

load_dotenv()

STATUS_LOG    = os.path.join(os.path.dirname(__file__), "agent_status.json")
SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), "schedule.json")


def _update_status(agent: str, task: str, status: str, result: str = ""):
    try:
        data = {}
        if os.path.exists(STATUS_LOG):
            with open(STATUS_LOG) as f:
                data = json.load(f)
        data[agent] = {
            "task": task, "status": status,
            "result": result[:200],
            "time": datetime.now().strftime("%H:%M:%S")
        }
        with open(STATUS_LOG, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _get_status_report() -> str:
    try:
        if os.path.exists(STATUS_LOG):
            with open(STATUS_LOG) as f:
                data = json.load(f)
            lines = ["📊 AGENT STATUS:"]
            for agent, info in data.items():
                lines.append(
                    f"  🤖 {agent}: {info['status']} — {info['task']}"
                )
            return "\n".join(lines)
        return "Koi agent status nahi mila."
    except Exception:
        return "Status file read error."


# ══════════════════════════════════════════════
# TOOL 1: VIDEO PIPELINE
# ══════════════════════════════════════════════
@function_tool
async def create_youtube_video(topic: str) -> str:
    """
    Full YouTube video pipeline start karo.
    Research, SEO, Script, Thumbnail, Upload sab automatic.
    Example: 'AI tools 2026 pe video banao'
    """
    _update_status("Pipeline", f"Starting: {topic}", "running")
    print(f"\n🎬 Pipeline start: {topic}")

    async def _run_bg():
        try:
            # Phase 1 run karo
            from phase1_research_seo_script import run_phase1
            p1 = await asyncio.get_event_loop().run_in_executor(
                None, run_phase1, topic
            )
            _update_status("Phase1", f"Done: {topic}", "complete",
                           p1.get("seo",{}).get("seo",{}).get("title",""))

            # Phase 2 run karo
            from phase2_thumbnail_upload import run_phase2
            p2 = await asyncio.get_event_loop().run_in_executor(
                None, run_phase2, p1
            )
            _update_status("Phase2", f"Done: {topic}", "complete",
                           p2.get("upload",{}).get("scheduled_time",""))

            _update_status("Pipeline", f"Done: {topic}", "COMPLETE",
                           "Script + Thumbnail + Upload ready")
            print(f"✅ Pipeline complete: {topic}")

        except Exception as e:
            _update_status("Pipeline", f"Error: {topic}", "ERROR", str(e))
            print(f"❌ Pipeline error: {e}")

    asyncio.create_task(_run_bg())

    return (
        f"Sir, '{topic}' ke liye YouTube pipeline shuru kar diya! "
        f"Background mein kaam ho raha hai — Research, SEO, Script, "
        f"Thumbnail sab automatic hoga. "
        f"Status ke liye bolen: 'agent status batao'"
    )


# ══════════════════════════════════════════════
# TOOL 2: AGENT STATUS
# ══════════════════════════════════════════════
@function_tool
async def get_agent_status() -> str:
    """Sab agents ka current status batao"""
    report = _get_status_report()
    if "Koi" in report:
        return "Abhi koi agent kaam nahi kar raha. Koi topic do video ke liye."
    return f"Yeh raha status:\n{report}"


# ══════════════════════════════════════════════
# TOOL 3: CLIENT MANAGEMENT
# ══════════════════════════════════════════════
@function_tool
async def handle_client_task(task: str) -> str:
    """
    Upwork client ke liye proposal ya message likho.
    Example: 'Video editing project ke liye proposal likho'
    """
    _update_status("Client Agent", f"Task: {task}", "running")
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        if "proposal" in task.lower():
            prompt = f"Write professional Upwork proposal for: {task}. Under 200 words, highlight expertise, be compelling."
        elif "follow" in task.lower():
            prompt = f"Write follow-up message for Upwork client: {task}. Professional, concise."
        else:
            prompt = f"Write professional client communication for: {task}"

        resp = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        result = resp.text

        # Save
        path = os.path.join(os.path.dirname(__file__), "client_docs",
                            f"client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(result)

        _update_status("Client Agent", task, "done", f"Saved: {path}")
        return f"Client document ready hai:\n{result[:400]}"

    except Exception as e:
        return f"Client task error: {e}"


# ══════════════════════════════════════════════
# TOOL 4: SOCIAL MEDIA POST
# ══════════════════════════════════════════════
@function_tool
async def post_to_social_media(content: str) -> str:
    """
    Instagram, Facebook, Rumble pe post karo via Zapier.
    Example: 'Is video ka short post karo social media pe'
    """
    import requests
    zapier_url = os.getenv("ZAPIER_WEBHOOK_URL")

    if not zapier_url or "hooks.zapier.com" not in zapier_url:
        return (
            "Zapier webhook setup nahi hai. "
            ".env mein sahi ZAPIER_WEBHOOK_URL add karo. "
            "zapier.com pe webhook zap banao."
        )
    try:
        payload = {
            "content": content,
            "platforms": ["instagram", "facebook", "rumble"],
            "timestamp": datetime.now().isoformat()
        }
        r = requests.post(zapier_url, json=payload, timeout=10)
        if r.status_code in [200, 201]:
            _update_status("Social Media", content[:50], "posted")
            return "Content Instagram, Facebook aur Rumble pe post kar diya!"
        return f"Zapier error: {r.status_code} — {r.text[:100]}"
    except Exception as e:
        return f"Social media error: {e}"


# ══════════════════════════════════════════════
# TOOL 5: SCHEDULE CONTENT
# ══════════════════════════════════════════════
@function_tool
async def schedule_content(topic: str, schedule_time: str = "tomorrow 10am") -> str:
    """
    Content ko specific time pe schedule karo.
    Example: 'Kal subah 10 baje AI tools video upload karo'
    """
    entry = {
        "topic": topic,
        "scheduled_time": schedule_time,
        "status": "scheduled",
        "created": datetime.now().isoformat()
    }
    schedules = []
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE) as f:
                schedules = json.load(f)
        except Exception:
            pass

    schedules.append(entry)
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedules, f, indent=2)

    _update_status("Scheduler", f"Scheduled: {topic}", "done", schedule_time)
    return (
        f"'{topic}' ko {schedule_time} ke liye schedule kar diya! "
        f"Total {len(schedules)} content schedule mein hai."
    )


# ══════════════════════════════════════════════
# TOOL 6: AFFILIATE SUGGESTIONS
# ══════════════════════════════════════════════
@function_tool
async def get_affiliate_suggestions(topic: str) -> str:
    """
    Video topic ke liye affiliate products suggest karo.
    Example: 'AI tools video ke liye affiliate products batao'
    """
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
Affiliate marketing expert ho.
YouTube topic: {topic}

5 affiliate products suggest karo. Har ek ke liye:
1. Product name
2. Kyon fit hai (1 line)
3. Platform (Amazon/ClickBank/ShareASale)
4. Commission estimate
5. Video mein kaise mention karo (exact line)
"""
        )
        return f"'{topic}' ke liye affiliates:\n{resp.text}"
    except Exception as e:
        return f"Affiliate suggestions error: {e}"
