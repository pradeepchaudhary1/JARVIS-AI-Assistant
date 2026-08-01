"""
JARVIS YouTube Tool
"""

from __future__ import annotations

from tools.browser import BrowserTool


class YoutubeTool:

    @staticmethod
    def open():

        return BrowserTool.open(
            "https://www.youtube.com"
        )