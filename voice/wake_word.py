"""
JARVIS Wake Word Detector
"""

from __future__ import annotations


class WakeWord:

    WAKE_WORDS = {

        "jarvis",
        "hey jarvis",
        "hi jarvis",
        "hello jarvis",

    }

    def detected(self, text: str) -> bool:

        text = text.lower().strip()

        for wake in self.WAKE_WORDS:

            if wake in text:
                return True

    def remove_wake_word(self, text: str) -> str:

        text = text.lower().strip()

        prefixes = (
            "hey jarvis",
            "hello jarvis",
            "hi jarvis",
            "jarvis",
        )

        for prefix in prefixes:

            if text.startswith(prefix):
                return text[len(prefix):].strip()

        return text            

        return False