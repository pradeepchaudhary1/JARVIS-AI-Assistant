"""
JARVIS WhatsApp Tool
"""

from __future__ import annotations

from tools.browser import BrowserTool


class WhatsAppTool:

    @staticmethod
    def open():

        return BrowserTool.open(
            "https://web.whatsapp.com"
        )