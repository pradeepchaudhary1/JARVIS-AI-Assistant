"""
JARVIS Multi-Agent Automation System
100% Free Tools:
- Gemini (Google AI Studio) - Script Writing
- Canva MCP - Thumbnails
- Zapier MCP - Social Media (FB, IG, Rumble)
- Google Calendar - Scheduling
- HubSpot - Client Management (Upwork)
- Notion - Content Storage
- YouTube Data API - Upload
- Leonardo.ai - AI Images (Free tier)
"""

import os
import json
import asyncio
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Optional
import google.generativeai as genai

load_dotenv()

# ─── API KEYS (.env me add karo) ──────────────────────────
GEMINI_KEY       = os.getenv("GOOGLE_API_KEY")
SERPER_KEY       = os.getenv("SERPER_API_KEY")        # serper.dev - free
LEONARDO_KEY     = os.getenv("LEONARDO_API_KEY")      # leonardo.ai - free
YOUTUBE_KEY      = os.getenv("YOUTUBE_API_KEY")
CANVA_TOKEN      = os.getenv("CANVA_ACCESS_TOKEN")
ZAPIER_WEBHOOK   = os.getenv("ZAPIER_WEBHOOK_URL")    # Zapier webhook URL
NOTION_KEY       = os.getenv("NOTION_API_KEY")
HUBSPOT_KEY      = os.getenv("HUBSPOT_API_KEY")

# Configure Gemini
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# ─── STATUS FILE (Jarvis ko report karne ke liye) ─────────
STATUS_LOG = os.path.join(os.path.dirname(__file__), "agent_status.json")

def update_agent_status(agent_name: str, task: str, status: str, result: str = ""):
    """Jarvis ko agent ka status batao"""
    try:
        data = {}
        if os.path.exists(STATUS_LOG):
            with open(STATUS_LOG, "r") as f:
                data = json.load(f)
        data[agent_name] = {
            "task": task,
            "status": status,
            "result": result[:200],
            "time": datetime.now().strftime("%H:%M:%S")
        }
        with open(STATUS_LOG, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Status update error: {e}")

def get_all_agent_status() -> str:
    """Sabhi agents ka status padhna"""
    try:
        if os.path.exists(STATUS_LOG):
            with open(STATUS_LOG, "r") as f:
                data = json.load(f)
            result = "📊 AGENT STATUS REPORT:\n"
            for agent, info in data.items():
                result += f"\n🤖 {agent}: {info['status']} — {info['task']}"
                if info.get('result'):
                    result += f"\n   → {info['result']}"
            return result
        return "No agent status available yet."
    except Exception:
        return "Status file not found."


# ══════════════════════════════════════════════
# TOOL 1: RESEARCH TOOL (Free - Google Search)
# ══════════════════════════════════════════════
class ResearchTool(BaseTool):
    name: str = "research_tool"
    description: str = "Search trending YouTube topics and keywords for given niche"

    def _run(self, query: str) -> str:
        update_agent_status("Research Agent", f"Searching: {query}", "running")
        try:
            if SERPER_KEY:
                headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
                payload = {"q": f"{query} trending YouTube 2025", "num": 5}
                r = requests.post("https://google.serper.dev/search",
                                  headers=headers, json=payload, timeout=10)
                if r.status_code == 200:
                    items = r.json().get("organic", [])
                    results = "\n".join([f"- {i.get('title')}: {i.get('snippet','')}"
                                         for i in items[:5]])
                    update_agent_status("Research Agent", f"Searching: {query}", "done", results[:100])
                    return f"Trending Topics:\n{results}"

            # Fallback: Gemini se research
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                f"Give me 5 trending YouTube video ideas for: {query}. "
                f"Include title, hook, and why it will get views. Format as numbered list."
            )
            result = response.text
            update_agent_status("Research Agent", f"Searching: {query}", "done", result[:100])
            return result
        except Exception as e:
            return f"Research error: {e}"


# ══════════════════════════════════════════════
# TOOL 2: SEO TOOL
# ══════════════════════════════════════════════
class SEOTool(BaseTool):
    name: str = "seo_tool"
    description: str = "Generate SEO-optimized title, description, tags for YouTube video"

    def _run(self, topic: str) -> str:
        update_agent_status("SEO Agent", f"Optimizing: {topic}", "running")
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
You are a YouTube SEO expert. For topic: "{topic}"
Generate:
1. TITLE: (60 chars, high CTR, include keyword)
2. DESCRIPTION: (500 words, include keywords naturally, call to action)
3. TAGS: (20 relevant tags comma separated)
4. THUMBNAIL TEXT: (5 words max, bold hook text)

Return as JSON format:
{{"title": "", "description": "", "tags": "", "thumbnail_text": ""}}
"""
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Clean JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            update_agent_status("SEO Agent", f"Optimizing: {topic}", "done", "SEO data ready")
            return text
        except Exception as e:
            return f"SEO error: {e}"


# ══════════════════════════════════════════════
# TOOL 3: SCRIPT WRITING TOOL (Free - Gemini)
# ══════════════════════════════════════════════
class ScriptTool(BaseTool):
    name: str = "script_tool"
    description: str = "Write full YouTube video script using Gemini AI (Free)"

    def _run(self, topic_and_seo: str) -> str:
        update_agent_status("Script Agent", f"Writing script: {topic_and_seo[:50]}", "running")
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
Write a complete YouTube video script for: {topic_and_seo}

Structure:
- HOOK (0-15 sec): Attention grabbing opener
- INTRO (15-30 sec): What viewer will learn
- MAIN CONTENT (5-8 min): 5-7 sections with detailed content
- CTA (last 30 sec): Subscribe, like, comment prompt
- END SCREEN (10 sec): Outro

Make it engaging, conversational, and educational.
Include [PAUSE], [SHOW SCREEN], [B-ROLL] markers.
Total length: 800-1200 words.
"""
            response = model.generate_content(prompt)
            script = response.text

            # Save to file
            filename = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            script_path = os.path.join(os.path.dirname(__file__), "scripts", filename)
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)

            update_agent_status("Script Agent", f"Writing: {topic_and_seo[:50]}", "done",
                                f"Saved: {filename}")
            return f"Script saved: {script_path}\n\nPREVIEW:\n{script[:300]}..."
        except Exception as e:
            return f"Script error: {e}"


# ══════════════════════════════════════════════
# TOOL 4: THUMBNAIL TOOL (Free - Leonardo.ai)
# ══════════════════════════════════════════════
class ThumbnailTool(BaseTool):
    name: str = "thumbnail_tool"
    description: str = "Generate YouTube thumbnail using Leonardo.ai (Free tier)"

    def _run(self, thumbnail_prompt: str) -> str:
        update_agent_status("Thumbnail Agent", f"Creating thumbnail", "running")
        try:
            if not LEONARDO_KEY:
                update_agent_status("Thumbnail Agent", "Creating thumbnail", "skipped",
                                    "No Leonardo key")
                return ("⚠ LEONARDO_API_KEY missing. "
                        "Get free key at: https://app.leonardo.ai/api-access\n"
                        f"Thumbnail prompt ready: {thumbnail_prompt}")

            # Leonardo.ai API call
            headers = {
                "Authorization": f"Bearer {LEONARDO_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": f"YouTube thumbnail, {thumbnail_prompt}, "
                          f"bold text overlay, high contrast, eye-catching, "
                          f"professional, 1280x720",
                "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Diffusion
                "width": 1280,
                "height": 720,
                "num_images": 1,
            }
            r = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers, json=payload, timeout=30
            )
            if r.status_code == 200:
                gen_id = r.json().get("sdGenerationJob", {}).get("generationId")
                # Wait for generation
                import time; time.sleep(15)
                r2 = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}",
                    headers=headers, timeout=15
                )
                if r2.status_code == 200:
                    imgs = r2.json().get("generations_by_pk", {}).get("generated_images", [])
                    if imgs:
                        img_url = imgs[0].get("url")
                        update_agent_status("Thumbnail Agent", "Creating thumbnail",
                                            "done", img_url)
                        return f"✅ Thumbnail generated: {img_url}"
            return f"Leonardo API error: {r.status_code}"
        except Exception as e:
            return f"Thumbnail error: {e}"


# ══════════════════════════════════════════════
# TOOL 5: SOCIAL MEDIA TOOL (Free - Zapier)
# ══════════════════════════════════════════════
class SocialMediaTool(BaseTool):
    name: str = "social_media_tool"
    description: str = "Post to Instagram, Facebook, Rumble via Zapier webhook"

    def _run(self, post_data: str) -> str:
        update_agent_status("Social Media Agent", "Posting to social media", "running")
        try:
            if not ZAPIER_WEBHOOK:
                return ("⚠ ZAPIER_WEBHOOK_URL missing in .env\n"
                        "Setup: zapier.com → New Zap → Webhook trigger → "
                        "Post to Instagram/Facebook/Rumble\n"
                        f"Post content ready:\n{post_data}")

            payload = {
                "platform": "all",
                "content": post_data,
                "timestamp": datetime.now().isoformat()
            }
            r = requests.post(ZAPIER_WEBHOOK, json=payload, timeout=10)
            if r.status_code in [200, 201]:
                update_agent_status("Social Media Agent", "Posting", "done",
                                    "Posted to all platforms")
                return "✅ Posted to Instagram, Facebook, Rumble via Zapier"
            return f"Zapier error: {r.status_code}"
        except Exception as e:
            return f"Social media error: {e}"


# ══════════════════════════════════════════════
# TOOL 6: YOUTUBE UPLOAD TOOL
# ══════════════════════════════════════════════
class YouTubeUploadTool(BaseTool):
    name: str = "youtube_upload_tool"
    description: str = "Schedule and upload video to YouTube"

    def _run(self, video_info: str) -> str:
        update_agent_status("Upload Agent", "Scheduling YouTube upload", "running")
        try:
            # Parse video info
            schedule_time = (datetime.now() + timedelta(hours=24)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            # Save upload job
            upload_queue = os.path.join(os.path.dirname(__file__), "upload_queue.json")
            queue = []
            if os.path.exists(upload_queue):
                with open(upload_queue, "r") as f:
                    queue = json.load(f)

            queue.append({
                "video_info": video_info,
                "scheduled_time": schedule_time,
                "status": "pending",
                "created": datetime.now().isoformat()
            })
            with open(upload_queue, "w") as f:
                json.dump(queue, f, indent=2)

            update_agent_status("Upload Agent", "Scheduling upload", "done",
                                f"Scheduled for {schedule_time}")
            return (f"✅ Video scheduled for upload at {schedule_time}\n"
                    f"Queue saved to upload_queue.json\n"
                    f"Run python youtube_uploader.py to process queue")
        except Exception as e:
            return f"Upload scheduling error: {e}"


# ══════════════════════════════════════════════
# TOOL 7: CLIENT MANAGEMENT (HubSpot/Upwork)
# ══════════════════════════════════════════════
class ClientManagementTool(BaseTool):
    name: str = "client_management_tool"
    description: str = "Manage Upwork clients, proposals, and follow-ups via HubSpot"

    def _run(self, task: str) -> str:
        update_agent_status("Client Agent", f"Managing: {task}", "running")
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")

            if "proposal" in task.lower():
                prompt = f"Write a professional Upwork proposal for: {task}. Make it compelling, under 200 words, highlight expertise."
            elif "follow" in task.lower():
                prompt = f"Write a follow-up message for Upwork client: {task}. Professional and concise."
            else:
                prompt = f"Draft a professional client communication for: {task}"

            response = model.generate_content(prompt)
            result = response.text

            # Save to file
            filename = f"client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = os.path.join(os.path.dirname(__file__), "client_docs", filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)

            update_agent_status("Client Agent", f"Managing: {task}", "done",
                                f"Saved: {filename}")
            return f"✅ Client document ready:\n{result[:300]}..."
        except Exception as e:
            return f"Client management error: {e}"


# ══════════════════════════════════════════════
# AFFILIATE TOOL
# ══════════════════════════════════════════════
class AffiliateTool(BaseTool):
    name: str = "affiliate_tool"
    description: str = "Generate affiliate links and product recommendations"

    def _run(self, topic: str) -> str:
        update_agent_status("Affiliate Agent", f"Finding affiliates for: {topic}", "running")
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
For YouTube video about: {topic}
Suggest 5 affiliate products to promote.
For each include:
- Product name
- Why it fits the video
- Where to get affiliate link (Amazon, ClickBank, etc)
- Estimated commission %
- How to mention in video naturally
Format as numbered list.
"""
            response = model.generate_content(prompt)
            result = response.text
            update_agent_status("Affiliate Agent", f"Finding: {topic}", "done",
                                "Affiliates found")
            return result
        except Exception as e:
            return f"Affiliate error: {e}"


# ══════════════════════════════════════════════════════════
# CREWAI AGENTS DEFINITION
# ══════════════════════════════════════════════════════════

def create_crew(topic: str):
    """Create full agent crew for given topic"""

    from crewai import LLM
    gemini_llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=GEMINI_KEY
    )

    # ── Agents ────────────────────────────────────────────
    ceo = Agent(
        role="CEO - Chief Executive Officer",
        goal="Define content strategy, approve final content plan",
        backstory="Experienced digital media CEO who knows what content goes viral",
        llm=gemini_llm, verbose=True,
        tools=[ResearchTool()]
    )

    research_analyst = Agent(
        role="Research Analyst",
        goal="Find trending topics and competitor analysis for maximum views",
        backstory="Data-driven researcher who finds viral content opportunities",
        llm=gemini_llm, verbose=True,
        tools=[ResearchTool()]
    )

    seo_manager = Agent(
        role="SEO Manager",
        goal="Optimize all content for maximum YouTube search visibility",
        backstory="YouTube SEO expert with track record of ranking videos #1",
        llm=gemini_llm, verbose=True,
        tools=[SEOTool()]
    )

    script_writer = Agent(
        role="Script Writer",
        goal="Write engaging, viral video scripts that keep viewers watching",
        backstory="Professional scriptwriter who has written for top YouTubers",
        llm=gemini_llm, verbose=True,
        tools=[ScriptTool()]
    )

    thumbnail_designer = Agent(
        role="Thumbnail Designer",
        goal="Create eye-catching thumbnails that maximize click-through rate",
        backstory="Visual designer specializing in YouTube thumbnails with 40%+ CTR",
        llm=gemini_llm, verbose=True,
        tools=[ThumbnailTool()]
    )

    social_media_manager = Agent(
        role="Social Media Manager",
        goal="Post content across Instagram, Facebook, Rumble for maximum reach",
        backstory="Social media expert who grows audiences across all platforms",
        llm=gemini_llm, verbose=True,
        tools=[SocialMediaTool()]
    )

    upload_scheduler = Agent(
        role="Upload & Scheduler",
        goal="Schedule and manage YouTube uploads at optimal times",
        backstory="Operations expert who knows the best times to upload for maximum views",
        llm=gemini_llm, verbose=True,
        tools=[YouTubeUploadTool()]
    )

    sales_manager = Agent(
        role="Sales Manager",
        goal="Find affiliate opportunities and maximize revenue from content",
        backstory="Digital marketing expert specializing in affiliate monetization",
        llm=gemini_llm, verbose=True,
        tools=[AffiliateTool()]
    )

    client_handler = Agent(
        role="Client Handler",
        goal="Manage Upwork clients, write proposals, handle communications",
        backstory="Professional freelancer manager with 500+ successful Upwork projects",
        llm=gemini_llm, verbose=True,
        tools=[ClientManagementTool()]
    )

    coo = Agent(
        role="COO - Chief Operating Officer",
        goal="Coordinate all agents, ensure smooth workflow, report to Jarvis",
        backstory="Operations expert who keeps all teams synchronized",
        llm=gemini_llm, verbose=True,
        tools=[ResearchTool()]
    )

    # ── Tasks ─────────────────────────────────────────────
    research_task = Task(
        description=f"Research trending YouTube topics for: {topic}. Find top 3 video ideas with search volume potential.",
        expected_output="3 video ideas with title, hook, why it will get views",
        agent=research_analyst
    )

    seo_task = Task(
        description="Take the best video idea from research and create full SEO package: title, description, tags, thumbnail text",
        expected_output="JSON with title, description, tags, thumbnail_text",
        agent=seo_manager,
        context=[research_task]
    )

    script_task = Task(
        description="Write complete video script using the SEO-optimized title and research findings",
        expected_output="Full video script with hook, intro, main content, CTA",
        agent=script_writer,
        context=[research_task, seo_task]
    )

    thumbnail_task = Task(
        description="Generate thumbnail image using the thumbnail text from SEO package",
        expected_output="Thumbnail image URL or file path",
        agent=thumbnail_designer,
        context=[seo_task]
    )

    affiliate_task = Task(
        description=f"Find 3-5 affiliate products to promote in this {topic} video",
        expected_output="Affiliate product list with commission info",
        agent=sales_manager,
        context=[research_task]
    )

    upload_task = Task(
        description="Schedule the video for upload with all metadata",
        expected_output="Upload confirmation with scheduled time",
        agent=upload_scheduler,
        context=[seo_task, script_task, thumbnail_task]
    )

    social_task = Task(
        description="Create social media posts for Instagram, Facebook, Rumble to promote this video",
        expected_output="Social media posts ready for all platforms",
        agent=social_media_manager,
        context=[seo_task, upload_task]
    )

    final_report_task = Task(
        description="Compile final report of everything done: script, thumbnail, schedule, affiliates, social posts",
        expected_output="Complete summary report for Jarvis to read to user",
        agent=coo,
        context=[research_task, seo_task, script_task,
                 thumbnail_task, affiliate_task, upload_task, social_task]
    )

    # ── Crew ──────────────────────────────────────────────
    crew = Crew(
        agents=[ceo, research_analyst, seo_manager, script_writer,
                thumbnail_designer, sales_manager, upload_scheduler,
                social_media_manager, client_handler, coo],
        tasks=[research_task, seo_task, script_task, thumbnail_task,
               affiliate_task, upload_task, social_task, final_report_task],
        process=Process.sequential,
        verbose=True
    )

    return crew


# ══════════════════════════════════════════════════════════
# MAIN FUNCTION — Jarvis yahan se call karega
# ══════════════════════════════════════════════════════════
async def run_full_pipeline(topic: str) -> str:
    """
    Jarvis is call karega jab user bolta hai:
    'Jarvis, {topic} pe video banao'
    """
    print(f"\n🚀 LAUNCHING MULTI-AGENT SYSTEM for: {topic}")
    print("=" * 60)
    update_agent_status("SYSTEM", f"Pipeline started for: {topic}", "running")

    try:
        crew = create_crew(topic)
        # Run in thread to not block Jarvis
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)

        update_agent_status("SYSTEM", f"Pipeline: {topic}", "COMPLETED",
                            str(result)[:200])

        # Final status
        status_report = get_all_agent_status()

        final_msg = (
            f"✅ Sir, '{topic}' ke liye poora kaam ho gaya!\n\n"
            f"{status_report}\n\n"
            f"📁 Files saved in:\n"
            f"  - scripts/ folder (video script)\n"
            f"  - upload_queue.json (scheduled upload)\n"
            f"  - client_docs/ folder (client documents)\n\n"
            f"CREW RESULT:\n{str(result)[:500]}"
        )
        return final_msg

    except Exception as e:
        error_msg = f"❌ Pipeline error: {e}"
        update_agent_status("SYSTEM", f"Pipeline: {topic}", "ERROR", str(e))
        return error_msg


def run_client_pipeline(task: str) -> str:
    """Upwork client management task"""
    tool = ClientManagementTool()
    return tool._run(task)


if __name__ == "__main__":
    # Test run
    topic = input("Enter video topic: ")
    result = asyncio.run(run_full_pipeline(topic))
    print(result)
