"""
JARVIS Web Search Skill
Day 5 — real web search (not the browser-tab web_search intent).
Step 1: skeleton + trigger matching only, fetch is stubbed.
"""

from __future__ import annotations

SKILL_NAME = "web_search"

TRIGGER_PHRASES = [
    "kya latest hai",
    "recent news",
    "internet se jaankari do",
    "web se batao",
    "duniya mein kya chal raha hai",
    "aaj ki taaza khabar",
    "current updates do",
    "jaankari chahiye internet se",
]

MIN_TIER = "professional"

def _extract_query(text: str) -> str:
    text = (text or "").lower()
    for phrase in TRIGGER_PHRASES:
        text = text.replace(phrase, "")
    return text.strip()

def _fetch_results(query: str) -> list[dict]:
    import requests
    from bs4 import BeautifulSoup

    try:
        response = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (JARVIS)"},
            timeout=8,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result")[:5]:
            title_el = result.select_one(".result__title")
            snippet_el = result.select_one(".result__snippet")
            link_el = result.select_one(".result__url")

            if not title_el:
                continue

            results.append({
                "title": title_el.get_text(strip=True),
                "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                "url": link_el.get_text(strip=True) if link_el else "",
            })

        return results
    except Exception:
        return []

def execute(command: str, context: dict) -> dict:
    query = _extract_query(command or "")

    if not query:
        return {
            "status": "error",
            "type": "skill",
            "message": "Sir, please specify what to search for.",
        }

    results = _fetch_results(query)

    if not results:
        return {
            "status": "error",
            "type": "skill",
            "message": f"Sir, I couldn't fetch results for {query}.",
        }

    snippets = "\n".join(
        f"- {result.get('title', '')}: {result.get('snippet', '')}"
        for result in results
    )

    try:
        try:
            from brain.llm_router import LLMRouter
        except ImportError:
            from llm.router import LLMRouter

        llm = LLMRouter()
        summary_prompt = (
            f"Summarize the following search results for '{query}' in 2-3 short "
            f"sentences. Use only the facts in these titles and snippets; do not "
            f"invent or add information:\n\n{snippets}"
        )
        summary = llm.ask(summary_prompt)
    except Exception:
        top_result = results[0]
        summary = (
            f"{top_result.get('title', '')}: "
            f"{top_result.get('snippet', '')}"
        ).strip()

    return {
        "status": "success",
        "type": "skill",
        "message": summary,
        "raw_results": results,
    }
