"""
JARVIS Router

Responsible for deciding which module/tool
should handle the user's request.
"""

from __future__ import annotations


class Router:
    """
    Determines where a command should be routed.
    """

    def detect(self, text: str) -> str:
        """
        Detect the best route for the given text.
        """

        text = text.lower()

        if "weather" in text:
            return "weather"

        if "browser" in text:
            return "browser"

        if "youtube" in text:
            return "youtube"

        return "llm"

    def route(self, text: str) -> str:
        """
        Public routing method.

        Currently forwards to detect().
        Future versions may contain advanced routing logic.
        """
        return self.detect(text)