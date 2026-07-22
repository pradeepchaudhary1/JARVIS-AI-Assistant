"""
PHASE 1 — Fixed: SEO JSON + Script 900+ words + Pollinations thumbnail
"""
import os, json, requests
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
SERPER_KEY = os.getenv("SERPER_API_KEY")
client     = genai.Client(api_key=GEMINI_KEY)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "phase1_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def gemini(prompt: str, retries=3) -> str:
    for i in range(retries):
        try:
            r = client.models.generate_content(
                model="gemini-2.0-flash", contents=prompt)
            return r.text or ""
        except Exception as e:
            if i == retries - 1:
                return f"Error: {e}"
            import time; time.sleep(2)
    return ""


def clean_json(text: str) -> dict | None:
    """JSON extract karo response se"""
    import re
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    # Find JSON object
    start = text.find('{')
    end   = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except Exception:
            pass
    return None


# ══════════════════════════════════════════════
# AGENT 1: RESEARCH
# ══════════════════════════════════════════════
class ResearchAnalyst:
    def run(self, topic: str) -> dict:
        print(f"\n🔬 [Research] Topic: {topic}")
        trending = self._serper(topic)
        ideas    = gemini(f"""
YouTube Research Analyst ho.
Topic: {topic}
Trending: {json.dumps(trending[:3], ensure_ascii=False)}

TOP 3 video ideas do. Har ek ke liye:
1. TITLE (60 chars, high CTR)
2. HOOK (first 15 seconds)
3. WHY VIRAL
4. TARGET AUDIENCE (India)
5. VIEWS POTENTIAL

Clearly numbered format mein likho.
""")
        result = {"topic": topic, "trending": trending, "ideas": ideas,
                  "timestamp": datetime.now().isoformat()}
        with open(os.path.join(OUTPUT_DIR,
                  f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
                  "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Research done")
        return result

    def _serper(self, topic: str) -> list:
        if not SERPER_KEY:
            return []
        try:
            r = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY,
                         "Content-Type": "application/json"},
                json={"q": f"{topic} YouTube viral 2026",
                      "gl": "in", "hl": "en", "num": 5},
                timeout=10)
            if r.status_code == 200:
                return [{"title": i.get("title",""),
                         "snippet": i.get("snippet","")}
                        for i in r.json().get("organic", [])[:5]]
        except Exception as e:
            print(f"  ⚠ Serper: {e}")
        return []


# ══════════════════════════════════════════════
# AGENT 2: SEO — Fixed JSON parsing
# ══════════════════════════════════════════════
class SEOManager:
    def run(self, research: dict) -> dict:
        print(f"\n📊 [SEO] Optimizing...")
        topic = research.get("topic", "")
        ideas = research.get("ideas", "")[:400]

        # ✅ FIX: Explicit JSON instruction
        raw = gemini(f"""
YouTube SEO Expert ho. Topic: {topic}

Sirf yeh JSON return karo, koi aur text nahi:
{{
  "title": "60 chars max YouTube title with main keyword",
  "description": "300 word YouTube description with keywords timestamps and CTA",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10"],
  "thumbnail_text": "5 words bold hook text",
  "category": "27",
  "best_upload_time": "Friday 5pm IST",
  "target_keywords": ["keyword1","keyword2","keyword3"]
}}

Research context: {ideas}
""")
        seo = clean_json(raw)
        if not seo:
            print(f"  ⚠ JSON parse fail — retry kar rahi hun...")
            # Retry with even simpler prompt
            raw2 = gemini(f"""
Return ONLY valid JSON for YouTube video about "{topic}":
{{"title":"...","description":"...","tags":["tag1","tag2","tag3"],"thumbnail_text":"...","category":"27","best_upload_time":"Friday 5pm IST","target_keywords":["kw1","kw2"]}}
""")
            seo = clean_json(raw2)

        if not seo:
            seo = {
                "title": f"{topic[:50]} — Complete Guide 2026",
                "description": f"In this video we cover everything about {topic}. Subscribe for more!",
                "tags": [topic, "tutorial", "guide", "2026", "hindi", "india",
                         "how to", "ai", "technology", "earn money"],
                "thumbnail_text": f"{topic[:20].upper()} SECRETS",
                "category": "27",
                "best_upload_time": "Friday 5pm IST",
                "target_keywords": [topic, f"{topic} hindi", f"{topic} 2026"]
            }
            print(f"  ⚠ Using default SEO")
        else:
            print(f"  ✅ SEO JSON parsed successfully")

        result = {"topic": topic, "seo": seo,
                  "timestamp": datetime.now().isoformat()}
        with open(os.path.join(OUTPUT_DIR,
                  f"seo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
                  "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  ✅ SEO done — Title: {seo.get('title','')[:50]}")
        return result


# ══════════════════════════════════════════════
# AGENT 3: SCRIPT — Fixed 900+ words
# ══════════════════════════════════════════════
class ScriptWriter:
    def run(self, research: dict, seo: dict) -> dict:
        print(f"\n✍️  [Script] Writing 900+ word script...")
        topic    = research.get("topic", "")
        seo_data = seo.get("seo", {})
        title    = seo_data.get("title", topic)
        keywords = seo_data.get("target_keywords", [topic])
        ideas    = research.get("ideas", "")[:400]

        # ✅ FIX: Longer, detailed prompt for 900+ words
        script = gemini(f"""
Professional YouTube scriptwriter ho tum.

VIDEO TITLE: {title}
TOPIC: {topic}
KEYWORDS: {', '.join(keywords[:3])}
RESEARCH: {ideas}

Ek COMPLETE, DETAILED YouTube script likho jo 900-1200 words ka ho.
Har section clearly likho:

[HOOK - 0:00-0:15]
Shocking question ya statement jo turant attention pakde.
(2-3 sentences)

[INTRO - 0:15-0:45]
Apna intro do, viewers ko batao kya seekhenge.
(3-4 sentences)

[SECTION 1: Main Topic Introduction - 0:45-2:00]
Pehla major point detail mein explain karo.
Examples aur real scenarios use karo.
[SHOW SCREEN] marker lagao jahan zaruri ho.
(100-150 words)

[SECTION 2: Deep Dive - 2:00-3:30]
Dusra major point — advanced tips.
Real examples aur case studies.
(100-150 words)

[SECTION 3: Step by Step Guide - 3:30-5:00]
Practical implementation steps.
Numbered steps clearly.
(100-150 words)

[SECTION 4: Advanced Tips - 5:00-6:30]
Pro-level tips jo log nahi jaante.
India-specific context.
(100-150 words)

[COMMON MISTAKES - 6:30-7:30]
5 common mistakes aur unke solutions.
(80-100 words)

[RESULTS/PROOF - 7:30-8:00]
Social proof ya expected results.
(50-60 words)

[CTA - 8:00-8:15]
Subscribe, like, comment call-to-action.
(30-40 words)

[OUTRO - 8:15-8:30]
End screen mention.
(20-25 words)

Conversational Hinglish tone use karo.
[PAUSE], [SHOW SCREEN], [B-ROLL] markers lagao.
MINIMUM 900 WORDS likhna zaroori hai.
""")

        wc = len(script.split())
        print(f"  📝 Word count: {wc}")

        # If still too short, expand
        if wc < 500:
            print(f"  ⚠ Script short ({wc} words) — expanding...")
            script = gemini(f"""
Yeh script bahut short hai. Ise expand karo to minimum 900 words:

Topic: {topic}
Title: {title}

Ek full detailed YouTube script likho with:
- Hook (shocking opening)
- Detailed intro
- 4 detailed sections with examples
- Common mistakes
- Strong CTA
- Total 900+ words
Conversational Hinglish tone.
""")
            wc = len(script.split())

        fname = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        fpath = os.path.join(OUTPUT_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"TITLE: {title}\nTOPIC: {topic}\n"
                    f"WORDS: {wc}\n"
                    f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    + "="*60 + "\n\n" + script)

        result = {"title": title, "topic": topic, "script": script,
                  "script_file": fpath, "word_count": wc,
                  "timestamp": datetime.now().isoformat()}
        print(f"  ✅ Script done ({wc} words) → {fpath}")
        return result


# ══════════════════════════════════════════════
# AGENT 4: THUMBNAIL — Pollinations AI (FREE)
# ══════════════════════════════════════════════
class ThumbnailAgent:
    def run(self, seo: dict) -> dict:
        print(f"\n🎨 [Thumbnail] Generating FREE thumbnail...")
        seo_data       = seo.get("seo", {})
        thumbnail_text = seo_data.get("thumbnail_text", "VIRAL VIDEO")
        topic          = seo.get("topic", "")
        title          = seo_data.get("title", topic)

        # ✅ FIX: Pollinations.ai — completely FREE
        result = self._pollinations(thumbnail_text, topic, title)

        fpath = os.path.join(OUTPUT_DIR,
                f"thumbnail_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Thumbnail info saved")
        return result

    def _pollinations(self, text: str, topic: str, title: str) -> dict:
        """Pollinations.ai — FREE image generation"""
        try:
            import urllib.parse
            prompt = (
                f"YouTube thumbnail, professional design, "
                f"bold text '{text}', vibrant colors, "
                f"high contrast, cinematic lighting, "
                f"topic: {topic[:50]}, clean layout, "
                f"no watermark, 4K quality, eye-catching"
            )
            encoded = urllib.parse.quote(prompt)
            # Pollinations free API
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true"

            print(f"  📥 Downloading from Pollinations.ai...")
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                safe  = "".join(c for c in text if c.isalnum() or c in " _-")
                fname = f"thumbnail_{safe[:20]}_{datetime.now().strftime('%H%M%S')}.jpg"
                fpath = os.path.join(OUTPUT_DIR, fname)
                with open(fpath, "wb") as f:
                    f.write(r.content)
                print(f"  ✅ Thumbnail saved → {fpath}")
                return {"thumbnail_text": text, "image_path": fpath,
                        "status": "success", "source": "pollinations.ai (free)"}
            else:
                return {"thumbnail_text": text, "image_path": None,
                        "error": f"Status {r.status_code}"}
        except Exception as e:
            return {"thumbnail_text": text, "image_path": None,
                    "error": str(e)}


# ══════════════════════════════════════════════
# AGENT 5: AFFILIATES
# ══════════════════════════════════════════════
class AffiliateFinder:
    def run(self, topic: str, script: dict) -> dict:
        print(f"\n💰 [Affiliates] Finding products...")
        result = gemini(f"""
Affiliate marketing expert ho.
YouTube topic: {topic}
Script preview: {script.get('script','')[:300]}

5 affiliate products suggest karo. Har ek ke liye:
1. Product name
2. Kyon fit hai (1 line)
3. Platform (Amazon.in/ClickBank)
4. Commission estimate
5. Video mein kaise mention karo (exact line)

Indian audience ke liye relevant products suggest karo.
""")
        fpath = os.path.join(OUTPUT_DIR,
                f"affiliates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"  ✅ Affiliates done")
        return {"topic": topic, "affiliates": result, "file": fpath}


# ══════════════════════════════════════════════
# MASTER RUNNER
# ══════════════════════════════════════════════
def run_phase1(topic: str) -> dict:
    print("\n" + "="*60)
    print(f"🚀 PHASE 1 — {topic}")
    print("="*60)

    research  = ResearchAnalyst().run(topic)
    seo       = SEOManager().run(research)
    script    = ScriptWriter().run(research, seo)
    thumbnail = ThumbnailAgent().run(seo)
    affiliate = AffiliateFinder().run(topic, script)

    results = {
        "research": research, "seo": seo,
        "script": script, "thumbnail": thumbnail,
        "affiliates": affiliate
    }

    sp = os.path.join(OUTPUT_DIR,
         f"PHASE1_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump({
            "topic":      topic,
            "title":      seo.get("seo",{}).get("title",""),
            "script":     script.get("script_file",""),
            "words":      script.get("word_count", 0),
            "thumbnail":  thumbnail.get("image_path",""),
            "upload_time":seo.get("seo",{}).get("best_upload_time",""),
            "tags":       seo.get("seo",{}).get("tags",[]),
            "status":     "phase1_complete"
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "="*60)
    print("✅ PHASE 1 COMPLETE!")
    print(f"📝 Script: {script.get('word_count',0)} words")
    print(f"🎯 Title:  {seo.get('seo',{}).get('title','')}")
    print(f"🎨 Thumbnail: {thumbnail.get('image_path','❌')}")
    print(f"⏰ Upload: {seo.get('seo',{}).get('best_upload_time','')}")
    print("="*60)
    return results


if __name__ == "__main__":
    topic = input("\n🎯 Topic: ").strip()
    if topic:
        run_phase1(topic)
