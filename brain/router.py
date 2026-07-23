"""
JARVIS Router
"""

from __future__ import annotations


class Router:

    def detect(self, text: str):

        text = text.lower()

        if "weather" in text:

            return "weather"

        if "browser" in text:

            return "browser"

        if "youtube" in text:

            return "youtube"

        return "llm"