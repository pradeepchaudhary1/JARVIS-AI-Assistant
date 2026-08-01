"""
JARVIS Browser Tool
"""

from __future__ import annotations

import webbrowser


class BrowserTool:

    @staticmethod
    def open(url: str):

        webbrowser.open(url)

        return {
            "status": "success",
            "tool": "browser",
            "url": url,
        }