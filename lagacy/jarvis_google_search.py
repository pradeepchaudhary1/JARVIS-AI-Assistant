"""
JARVIS Google Search — Issue #3 & #6 Fix
Real search with Serper, location-based, no hallucination
"""
import os, requests, logging
from datetime import datetime
from dotenv import load_dotenv
from livekit.agents import function_tool

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERPER_KEY = os.getenv("SERPER_API_KEY")
NEWS_KEY   = os.getenv("NEWS_API_KEY")


def _serper_search(query: str, location: str = "India") -> str:
    """Serper.dev se Google search"""
    if not SERPER_KEY:
        return None
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": query, "gl": "in", "hl": "hi", "num": 5},
            timeout=8
        )
        if r.status_code == 200:
            data  = r.json()
            items = data.get("organic", [])
            if not items:
                return "Koi results nahi mile."
            result = ""
            for i, item in enumerate(items[:4], 1):
                result += (
                    f"{i}. {item.get('title','')}\n"
                    f"   {item.get('snippet','')}\n"
                    f"   🔗 {item.get('link','')}\n\n"
                )
            # Answer box agar ho
            if data.get("answerBox"):
                ab = data["answerBox"]
                result = f"📌 Direct Answer: {ab.get('answer') or ab.get('snippet','')}\n\n" + result
            return result.strip()
    except Exception as e:
        logger.error(f"Serper error: {e}")
    return None


@function_tool
async def google_search(query: str) -> str:
    """
    Google pe search karo — real results sirf.
    Koi hallucination nahi — sirf verified results.
    """
    logger.info(f"Searching: {query}")

    result = _serper_search(query)
    if result:
        return result

    # Google Custom Search fallback
    gkey = os.getenv("GOOGLE_SEARCH_API_KEY")
    gcx  = os.getenv("SEARCH_ENGINE_ID")
    if gkey and gcx:
        try:
            r = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": gkey, "cx": gcx, "q": query, "num": 4},
                timeout=10
            )
            if r.status_code == 200:
                items = r.json().get("items", [])
                if items:
                    out = ""
                    for i, item in enumerate(items, 1):
                        out += f"{i}. {item.get('title','')}\n   {item.get('snippet','')}\n\n"
                    return out.strip()
        except Exception as e:
            logger.error(f"Google CSE error: {e}")

    return (
        "Search abhi available nahi hai. "
        "SERPER_API_KEY check karo .env mein. "
        f"Query thi: {query}"
    )


@function_tool
async def get_current_datetime() -> str:
    """Current date aur time batao — exact"""
    now = datetime.now()
    return (
        f"📅 Date: {now.strftime('%d %B %Y')}\n"
        f"🕐 Time: {now.strftime('%I:%M:%S %p')}\n"
        f"📆 Day:  {now.strftime('%A')}\n"
        f"🗓 Full: {now.strftime('%d/%m/%Y %H:%M:%S')}"
    )


@function_tool
async def search_youtube(query: str) -> str:
    """YouTube pe koi video search karo"""
    import webbrowser
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"✅ YouTube pe '{query}' search kar diya."


@function_tool
async def open_url(url: str) -> str:
    """Koi bhi URL browser mein kholo"""
    import webbrowser
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"✅ Khola: {url}"


@function_tool
async def get_news(topic: str = "") -> str:
    """Latest news fetch karo"""
    if not NEWS_KEY:
        # Serper news fallback
        query = f"{topic} latest news today" if topic else "India latest news today"
        result = _serper_search(query)
        return result or "News API key missing. SERPER_API_KEY ya NEWS_API_KEY add karo."
    try:
        url = "https://newsapi.org/v2/top-headlines" if not topic else "https://newsapi.org/v2/everything"
        params = {"apiKey": NEWS_KEY, "language": "en", "pageSize": 5}
        if topic:
            params["q"] = topic
        else:
            params["country"] = "in"
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            articles = r.json().get("articles", [])
            if not articles:
                return "Koi news nahi mili."
            result = f"📰 Latest News ({topic or 'India'}):\n\n"
            for i, a in enumerate(articles[:4], 1):
                result += f"{i}. {a.get('title','')}\n   {a.get('description','')[:100]}...\n\n"
            return result
    except Exception as e:
        return f"News error: {e}"
    return "News fetch nahi ho saka."
