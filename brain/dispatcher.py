"""
JARVIS Dispatcher
"""

from __future__ import annotations

from tools.browser import BrowserTool
from tools.youtube import YoutubeTool
from tools.whatsapp import WhatsAppTool
from tools.filesystem import FileSystemTool


class Dispatcher:

    def dispatch(self, tool: str, command: str):

        tool = tool.lower()

        if tool == "youtube":
            return YoutubeTool.open()

        if tool == "browser":

            text = command.lower()

            if text.startswith("open "):

                url = text.replace("open ", "").strip()

                if "." not in url:
                    url += ".com"

                if not url.startswith("http"):
                    url = "https://" + url

                return BrowserTool.open(url)

            return {
                "status": "error",
                "message": "Browser command not understood."
            }

        if tool == "whatsapp":
            return WhatsAppTool.open()

        if tool == "filesystem":
            return FileSystemTool.current_directory()

        return {
            "status": "unknown",
            "tool": tool,
            "command": command,
            "message": "No matching tool."
        }