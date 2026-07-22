import os, requests
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
load_dotenv(os.path.join(BASE_DIR, ".env"))

SERPER_KEY = os.getenv("SERPER_API_KEY", "")

CATEGORIES = {
    "ai":      "latest AI technology news today",
    "tech":    "latest technology news today",
    "world":   "top world news headlines today",
    "india":   "top India news headlines today",
    "kota":    "Kota Rajasthan news today",
    "market":  "stock market news today India",
    "youtube": "YouTube creator economy news",
}

def fetch_news(category="world", count=5):
    """Fetch headlines via Serper.dev news search. Falls back gracefully if no key."""
    if not SERPER_KEY:
        return {
            "ok": False,
            "message": "Sir, SERPER_API_KEY .env mein nahi hai. serper.dev se free key le lo.",
            "headlines": []
        }

    query = CATEGORIES.get(category.lower(), category)
    try:
        resp = requests.post(
            "https://google.serper.dev/news",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": count},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("news", [])[:count]
        headlines = [
            {
                "title": it.get("title", ""),
                "source": it.get("source", ""),
                "date": it.get("date", ""),
                "link": it.get("link", "")
            }
            for it in items
        ]
        return {"ok": True, "category": category, "headlines": headlines}
    except Exception as e:
        return {"ok": False, "message": "Sir, news fetch nahi ho payi: " + str(e), "headlines": []}

def format_for_voice(result):
    """Turns a fetch_news() result into a short Hinglish spoken summary."""
    if not result.get("ok") or not result.get("headlines"):
        return result.get("message", "Sir, abhi news available nahi hai.")
    lines = ["Sir, aaj ki top headlines:"]
    for i, h in enumerate(result["headlines"][:4], 1):
        lines.append(f"{i}. {h['title']} ({h['source']})")
    return " ".join(lines)

def handle_worldmonitor_command(text):
    t = text.lower()

    # Strict trigger phrases - avoid generic substrings like "world" matching everything
    triggers = [
        "news batao", "khabar batao", "headlines batao", "samachar batao",
        "duniya mein kya", "aaj ki khabar", "aaj ki news", "world news",
        "khabren batao", "saari khabren", "top headlines", "news sunao",
        "khabar sunao",
    ]
    if not any(trig in t for trig in triggers):
        return None

    category = "world"
    if "ai" in t or "technology" in t or "tech" in t:
        category = "ai"
    elif "market" in t or "share" in t or "stock" in t:
        category = "market"
    elif "kota" in t or "rajasthan" in t:
        category = "kota"
    elif "india" in t:
        category = "india"
    elif "youtube" in t:
        category = "youtube"

    result = fetch_news(category)
    return format_for_voice(result)

if __name__ == "__main__":
    r = fetch_news("ai", 5)
    print(format_for_voice(r))
