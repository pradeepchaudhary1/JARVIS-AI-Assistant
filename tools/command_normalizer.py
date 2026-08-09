"""
JARVIS Command Normalizer
Phase 2.3.1
"""

from __future__ import annotations

import re


class CommandNormalizer:

    WAKE_WORDS = (
        "hey jarvis",
        "hello jarvis",
        "hi jarvis",
        "jarvis",
    )

    FILLER_WORDS = {
        "please",
        "kindly",
        "can",
        "you",
    }

    @classmethod
    def normalize(cls, text: str) -> str:

        if not text:
            return ""

        text = text.lower().strip()

        # Remove punctuation
        text = re.sub(r"[^\w\s]", " ", text)

        # Normalize multiple spaces
        text = re.sub(r"\s+", " ", text).strip()

        # Remove wake word from beginning
        for wake in cls.WAKE_WORDS:
            if text == wake:
                return ""

            prefix = wake + " "

            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break

        # Remove common conversational fillers
        words = text.split()

        words = [
            word
            for word in words
            if word not in cls.FILLER_WORDS
        ]

        return " ".join(words).strip()