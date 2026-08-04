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

    def detect(self, text: str):
        """
        Detect the best route for the given command.
        """

        text = text.lower()

        # Universal launcher commands
        if any(
            text.startswith(x)
            for x in [
                "open",
                "launch",
                "start"
            ]
        ):
            return "launcher"

        if "weather" in text:
            return "weather"

        if "browser" in text:
            return "browser"

        if "filesystem" in text:
            return "filesystem"

        return "llm"

    def route(self, text: str):
        """
        Public routing method.

        Currently forwards to detect().
        Future versions may contain advanced routing logic.
        """
        return self.detect(text)