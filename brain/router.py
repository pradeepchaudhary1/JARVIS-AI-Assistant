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

        text = text.strip()

        # Remove wake-word prefix before routing
        for wake in (
            "hey jarvis",
            "hello jarvis",
            "hi jarvis",
            "jarvis"
        ):
            if text.startswith(wake):
                text = text[len(wake):].strip()
                break

        # App/process control commands
        if text.startswith(("close ", "kill ")):
            return "launcher"

        # Window control commands
        if text.startswith((
            "minimize ",
            "minimise ",
            "maximize ",
            "maximise ",
            "restore "
        )):
            return "launcher"    

        if "weather" in text:
            return "weather"

        if "browser" in text:
            return "browser"

        # -------------------------
        # File / Folder Commands
        # -------------------------

        if any(
            word in text
            for word in [
                "desktop",
                "downloads",
                "documents",
                "pictures",
                "picture",
                "videos",
                "video",
                "music",
                "folder",
                "file"
            ]
        ):
            return "filesystem"


        # -------------------------
        # Universal launcher commands
        # -------------------------

        if any(
            x in text
            for x in [
                "open",
                "launch",
                "start",
                "run",
                "kholo",
                "khol do",
                "open up",
                "close",
                "kill",
                "band karo",
                "bapas jao",
                "hatao",
                "minimize",
                "maximize",
                "restore"
            ]
        ):
            return "launcher"

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