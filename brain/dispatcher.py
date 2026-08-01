"""
JARVIS Production Dispatcher
"""

from __future__ import annotations

from tools.youtube import YoutubeTool
from tools.browser import BrowserTool
from tools.whatsapp import WhatsAppTool
from tools.filesystem import FileSystemTool


class Dispatcher:

    def dispatch(self, tool: str, command: str):

        tool = tool.lower()

        if tool == "youtube":
            return YoutubeTool.open()

        elif tool == "browser":

            url = "https://google.com"

            text = command.lower()

            if "http://" in text or "https://" in text:
                url = command.strip()

            return BrowserTool.open(url)

        elif tool == "whatsapp":
            return WhatsAppTool.open()

        elif tool == "filesystem":
            return FileSystemTool.current_directory()

        return {
            "status": "error",
            "tool": tool,
            "message": "Unknown tool."
        }