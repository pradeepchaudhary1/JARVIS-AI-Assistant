"""
PHASE 2 — YouTube Upload + Auto Schedule + Description+Tags fill
"""
import os, json, pickle, requests, time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "phase2_output")
PHASE1_DIR = os.path.join(os.path.dirname(__file__), "phase1_output")
QUEUE_FILE = os.path.join(os.path.dirname(__file__), "upload_queue.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "youtube_token.pickle")
CREDS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

STABILITY_KEY = os.getenv("STABILITY_API_KEY")
GEMINI_KEY    = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

from google import genai
gclient = genai.Client(api_key=GEMINI_KEY)


# ══════════════════════════════════════════════
# THUMBNAIL — Pollinations (FREE) + Stability fallback
# ══════════════════════════════════════════════
class ThumbnailDesigner:
    def run(self, seo_data: dict) -> dict:
        print(f"\n🎨 [Thumbnail] Generating...")
        seo  = seo_data.get("seo", {})
        text = seo.get("thumbnail_text", "VIRAL VIDEO")
        topic = seo_data.get("topic", "")

        # Try Pollinations first (FREE)
        result = self._pollinations(text, topic)
        if result.get("status") == "success":
            return result

        # Stability fallback if credits available
        if STABILITY_KEY:
            result2 = self._stability(text, topic)
            if result2.get("status") == "success":
                return result2

        return result

    def _pollinations(self, text: str, topic: str) -> dict:
        try:
            import urllib.parse
            prompt  = f"YouTube thumbnail professional, bold '{text}', vibrant high-contrast, {topic[:40]}, 4K"
            encoded = urllib.parse.quote(prompt)
            url     = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true"
            print(f"  📥 Pollinations.ai (FREE)...")
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and len(r.content) > 1000:
                safe  = "".join(c for c in text if c.isalnum() or c in " _")
                fname = f"thumb_{safe[:15]}_{datetime.now().strftime('%H%M%S')}.jpg"
                fpath = os.path.join(OUTPUT_DIR, fname)
                with open(fpath, "wb") as f:
                    f.write(r.content)
                print(f"  ✅ Thumbnail → {fpath}")
                return {"status": "success", "image_path": fpath,
                        "source": "pollinations.ai", "text": text}
            return {"status": "fail", "error": f"Status {r.status_code}"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}

    def _stability(self, text: str, topic: str) -> dict:
        try:
            prompt = f"YouTube thumbnail, bold text '{text}', {topic[:40]}, professional, 16:9"
            r = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/core",
                headers={"Authorization": f"Bearer {STABILITY_KEY}", "Accept": "image/*"},
                files={"none": ""},
                data={"prompt": prompt, "output_format": "jpeg", "aspect_ratio": "16:9"},
                timeout=60
            )
            if r.status_code == 200:
                safe  = "".join(c for c in text if c.isalnum() or c in " _")
                fname = f"thumb_stability_{safe[:15]}_{datetime.now().strftime('%H%M%S')}.jpg"
                fpath = os.path.join(OUTPUT_DIR, fname)
                with open(fpath, "wb") as f:
                    f.write(r.content)
                return {"status": "success", "image_path": fpath,
                        "source": "stability.ai", "text": text}
            return {"status": "fail", "error": f"{r.status_code}: {r.text[:100]}"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}


# ══════════════════════════════════════════════
# YOUTUBE UPLOADER — Auto fill description+tags
# ══════════════════════════════════════════════
class YouTubeUploader:

    def _get_youtube_service(self):
        """YouTube API service banao"""
        if not os.path.exists(TOKEN_FILE):
            return None
        try:
            from googleapiclient.discovery import build
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)
            # Refresh if expired
            if hasattr(creds, 'expired') and creds.expired:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                with open(TOKEN_FILE, "wb") as f:
                    pickle.dump(creds, f)
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"  ❌ YouTube service error: {e}")
            return None

    def upload_video(self, video_path: str, phase1_summary: dict,
                     thumbnail_path: str = None,
                     schedule_hours: int = 0) -> dict:
        """
        Video upload karo YouTube pe.
        schedule_hours=0 means abhi upload
        schedule_hours=24 means kal same time
        """
        print(f"\n📤 [YouTube Upload] Starting...")

        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file nahi mila: {video_path}"}

        yt = self._get_youtube_service()
        if not yt:
            return {"success": False,
                    "error": "YouTube OAuth token nahi mila. Option 3 (Setup OAuth) run karo."}

        seo   = phase1_summary.get("seo", {}).get("seo",
                phase1_summary.get("seo", {}))
        title = seo.get("title") or phase1_summary.get("title", "My Video")
        desc  = seo.get("description", "")
        tags  = seo.get("tags", [])
        cat   = seo.get("category", "27")

        # Auto-generate description if empty
        if not desc or len(desc) < 50:
            desc = self._auto_description(
                phase1_summary.get("topic", title),
                phase1_summary.get("script", {}).get("script", ""),
                tags
            )

        print(f"  📝 Title: {title[:60]}")
        print(f"  🏷 Tags: {len(tags)} tags")
        print(f"  📄 Description: {len(desc)} chars")

        # Schedule time
        if schedule_hours > 0:
            pub_time = (datetime.utcnow() + timedelta(hours=schedule_hours)
                        ).strftime("%Y-%m-%dT%H:%M:%S.0Z")
            privacy  = "private"
            status   = {"privacyStatus": "private",
                        "publishAt": pub_time}
        else:
            privacy  = "public"
            status   = {"privacyStatus": "public"}

        body = {
            "snippet": {
                "title":       title[:100],
                "description": desc[:5000],
                "tags":        tags[:30],
                "categoryId":  str(cat)
            },
            "status": status
        }

        try:
            from googleapiclient.http import MediaFileUpload
            media   = MediaFileUpload(video_path,
                                      mimetype="video/*",
                                      chunksize=-1,
                                      resumable=True)
            req     = yt.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            print(f"  📤 Uploading {os.path.getsize(video_path)/1e6:.1f} MB...")
            response = None
            while response is None:
                status_resp, response = req.next_chunk()
                if status_resp:
                    pct = int(status_resp.progress() * 100)
                    print(f"  ⬆ {pct}%", end="\r")

            vid_id = response.get("id")
            vid_url = f"https://youtube.com/watch?v={vid_id}"
            print(f"\n  ✅ Uploaded: {vid_url}")

            # Set thumbnail
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    yt.thumbnails().set(
                        videoId=vid_id,
                        media_body=MediaFileUpload(thumbnail_path)
                    ).execute()
                    print(f"  🎨 Thumbnail set!")
                except Exception as te:
                    print(f"  ⚠ Thumbnail error: {te}")

            # Save to queue as done
            self._update_queue(title, vid_id, "uploaded", schedule_hours)

            return {"success": True, "video_id": vid_id, "url": vid_url,
                    "title": title, "scheduled": schedule_hours > 0}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _auto_description(self, topic: str, script: str, tags: list) -> str:
        """Auto-generate YouTube description"""
        try:
            r = gclient.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"""
YouTube description likho {topic} ke liye.
Include:
- Engaging first 2 lines (show in search)
- Key points covered (timestamps: 0:00, 1:30, 3:00, etc.)
- Keywords: {', '.join(tags[:5])}
- Subscribe CTA
- Social media links placeholder
- 3-5 relevant hashtags at end

Script preview: {script[:200]}

300-400 words likhna.
"""
            )
            return r.text
        except Exception:
            kws = ' '.join(f'#{t}' for t in tags[:5])
            return (
                f"In this video, we cover everything about {topic}.\n\n"
                f"📌 Timestamps:\n0:00 Introduction\n1:30 Main Topic\n5:00 Tips\n7:00 Conclusion\n\n"
                f"👍 Like, Subscribe, Share!\n\n"
                f"🔔 Bell icon dabao notifications ke liye!\n\n"
                f"{kws}"
            )

    def _update_queue(self, title: str, vid_id: str,
                      status: str, schedule_h: int):
        queue = []
        if os.path.exists(QUEUE_FILE):
            try:
                with open(QUEUE_FILE) as f:
                    queue = json.load(f)
            except Exception:
                pass
        queue.append({
            "title":      title,
            "video_id":   vid_id,
            "url":        f"https://youtube.com/watch?v={vid_id}",
            "status":     status,
            "scheduled_h": schedule_h,
            "done_at":    datetime.now().isoformat()
        })
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

    def add_to_queue(self, title: str, sched_hours: int = 24) -> dict:
        """Video queue mein add karo (bina actual upload)"""
        queue = []
        if os.path.exists(QUEUE_FILE):
            try:
                with open(QUEUE_FILE) as f:
                    queue = json.load(f)
            except Exception:
                pass
        entry = {
            "title":          title,
            "status":         "queued",
            "scheduled_time": (datetime.now() +
                               timedelta(hours=sched_hours)).isoformat(),
            "added_at":       datetime.now().isoformat()
        }
        queue.append(entry)
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
        print(f"  📋 Queue: {len(queue)} items")
        return entry

    def show_queue(self) -> str:
        if not os.path.exists(QUEUE_FILE):
            return "Queue khali hai."
        try:
            with open(QUEUE_FILE) as f:
                q = json.load(f)
            out = f"📋 Upload Queue ({len(q)} items):\n"
            for i, item in enumerate(q[-10:], 1):
                out += (f"  {i}. {item.get('title','')[:50]}\n"
                        f"     Status: {item.get('status','?')} | "
                        f"Time: {item.get('scheduled_time','?')[:16]}\n")
            return out
        except Exception as e:
            return f"Queue error: {e}"


# ══════════════════════════════════════════════
# OAUTH SETUP
# ══════════════════════════════════════════════
def setup_oauth():
    print("\n📺 YouTube OAuth Setup")
    print("="*40)

    # Check multiple credential file names
    creds_names = ["client_secret.json", "youtube_credentials.json",
                   "credentials.json", "oauth_credentials.json"]
    creds_file  = None
    for cn in creds_names:
        fp = os.path.join(os.path.dirname(__file__), cn)
        if os.path.exists(fp):
            creds_file = fp
            print(f"✅ Credentials file mila: {cn}")
            break

    if not creds_file:
        print("❌ Credentials file nahi mila!")
        print("\nYeh files check ki gayi:")
        for cn in creds_names:
            print(f"  - {cn}")
        print("\nSteps:")
        print("1. console.cloud.google.com → New Project 'Jarvis'")
        print("2. APIs → Enable 'YouTube Data API v3'")
        print("3. Credentials → OAuth 2.0 → Desktop App")
        print("4. JSON download karo → 'client_secret.json' naam se save")
        print(f"5. JARVIS-AI-Assistant folder mein daalo")
        return False

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        SCOPES = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.readonly"
        ]
        flow  = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print(f"\n✅ OAuth complete! Token: {TOKEN_FILE}")
        return True
    except ImportError:
        print("❌ pip install google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        print(f"❌ OAuth error: {e}")
        return False


# ══════════════════════════════════════════════
# PHASE 2 RUNNER
# ══════════════════════════════════════════════
def run_phase2(phase1_results: dict, video_file: str = None,
               schedule_hours: int = 0) -> dict:
    print("\n" + "="*60)
    print("🚀 PHASE 2 — Thumbnail + YouTube Upload")
    print("="*60)

    # Thumbnail
    td = ThumbnailDesigner().run(phase1_results.get("seo", {}))

    # Upload
    uploader = YouTubeUploader()
    if video_file and os.path.exists(video_file):
        ud = uploader.upload_video(
            video_file, phase1_results,
            td.get("image_path"), schedule_hours
        )
    else:
        seo = phase1_results.get("seo", {}).get("seo", {})
        title = seo.get("title", "My Video")
        ud = uploader.add_to_queue(title, 24)
        print(f"  ℹ No video file — queued for later upload")

    result = {"thumbnail": td, "upload": ud}

    print("\n" + "="*60)
    print("✅ PHASE 2 COMPLETE!")
    print(f"🎨 Thumbnail: {td.get('image_path','❌')}")
    if ud.get("url"):
        print(f"📺 YouTube: {ud['url']}")
    else:
        print(f"📋 Status: {ud.get('status','queued')}")
    print("="*60)
    return result


def run_full_pipeline(topic: str, video_file: str = None,
                      schedule_hours: int = 0) -> dict:
    from phase1_research_seo_script import run_phase1
    p1 = run_phase1(topic)
    p2 = run_phase2(p1, video_file, schedule_hours)
    sp = os.path.join(OUTPUT_DIR,
         f"FULL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump({
            "topic":     topic,
            "title":     p1.get("seo",{}).get("seo",{}).get("title",""),
            "script":    p1.get("script",{}).get("script_file",""),
            "words":     p1.get("script",{}).get("word_count",0),
            "thumbnail": p2.get("thumbnail",{}).get("image_path",""),
            "upload":    p2.get("upload",{}),
            "tags":      p1.get("seo",{}).get("seo",{}).get("tags",[]),
            "status":    "complete"
        }, f, indent=2, ensure_ascii=False)
    print(f"\n🏁 Full pipeline done → {sp}")
    return {**p1, **p2}


# ══════════════════════════════════════════════
# MENU
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  JARVIS — Phase 2: Thumbnail + YouTube Upload")
    print("="*60)
    print("\n1. Full pipeline (Phase 1 + 2)")
    print("2. Phase 2 only (thumbnail + upload)")
    print("3. Setup YouTube OAuth (one-time)")
    print("4. Upload video from file")
    print("5. Show upload queue")

    ch = input("\nChoice (1-5): ").strip()

    if ch == "1":
        topic = input("Topic: ").strip()
        video = input("Video file (Enter = skip): ").strip() or None
        hrs   = int(input("Schedule hours (0 = now): ").strip() or "0")
        run_full_pipeline(topic, video, hrs)

    elif ch == "2":
        pf = input("Phase 1 summary JSON path: ").strip()
        try:
            with open(pf) as f: p1 = json.load(f)
            video = input("Video file (Enter = skip): ").strip() or None
            run_phase2(p1, video)
        except Exception as e:
            print(f"❌ {e}")

    elif ch == "3":
        setup_oauth()

    elif ch == "4":
        video = input("Video file path: ").strip()
        pf    = input("Phase 1 summary JSON (Enter = auto-find): ").strip()
        hrs   = int(input("Schedule hours (0 = now): ").strip() or "0")
        if not pf:
            # Auto find latest summary
            files = sorted([f for f in os.listdir(PHASE1_DIR)
                           if f.startswith("PHASE1_SUMMARY")],
                          reverse=True)
            if files:
                pf = os.path.join(PHASE1_DIR, files[0])
                print(f"✅ Using: {pf}")
        try:
            with open(pf) as f: p1 = json.load(f)
            run_phase2(p1, video, hrs)
        except Exception as e:
            print(f"❌ {e}")

    elif ch == "5":
        print(YouTubeUploader().show_queue())
