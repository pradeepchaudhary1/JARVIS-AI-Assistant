"""
JARVIS AI Assistant

Context Builder
"""

from __future__ import annotations

from datetime import datetime


class ContextBuilder:

    def build(self):

        return {

            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "platform": "Windows",

            "assistant": "JARVIS V3"

        }