"""
JARVIS Production Dispatcher
"""

from __future__ import annotations

from tools.browser import BrowserTool
from tools.filesystem import FileSystemTool
from tools.universal_launcher import UniversalLauncher


class Dispatcher:

    def dispatch(self, tool: str, command: str):

        tool = tool.lower()

        # -------------------------
        # Universal Open Commands
        # -------------------------

        if tool == "launcher":

            text = command.lower()

            target = (
                text.replace("open", "")
                    .replace("launch", "")
                    .replace("start", "")
                    .strip()
            )

            return UniversalLauncher.launch(target)

        # -------------------------
        # Browser
        # -------------------------

        elif tool == "browser":

            text = command.lower()

            if "http://" in text or "https://" in text:

                return BrowserTool.open(command.strip())

            return BrowserTool.open("https://google.com")

        # -------------------------
        # Filesystem
        # -------------------------

        elif tool == "filesystem":

            return FileSystemTool.current_directory()

        # -------------------------

        return {

            "status": "error",

            "tool": tool,

            "message": "Unknown Tool"

        }