"""
JARVIS Wake Word Detector

Handles:
- Wake-word detection
- Command extraction
- Wake-only detection
"""

from __future__ import annotations


class WakeWordDetector:

    WAKE_WORDS = (
        "hey jarvis",
        "hello jarvis",
        "hi jarvis",
        "jarvis",
    )

    @classmethod
    def detect(cls, text: str) -> dict:

        if not isinstance(text, str):

            return {
                "status": "error",
                "wake_word": False,
                "command": "",
                "text": "",
                "message": "Invalid text input.",
            }

        original = text.strip()

        if not original:

            return {
                "status": "empty",
                "wake_word": False,
                "command": "",
                "text": "",
            }

        lower = original.lower()

        for wake in cls.WAKE_WORDS:

            # Wake word only
            if lower == wake:

                return {
                    "status": "wake_only",
                    "wake_word": True,
                    "command": "",
                    "text": original,
                }

            # Wake word + command
            prefix = wake + " "

            if lower.startswith(prefix):

                command = original[len(wake):].strip()

                return {
                    "status": "command",
                    "wake_word": True,
                    "command": command,
                    "text": original,
                }

        # No wake word
        return {
            "status": "ignored",
            "wake_word": False,
            "command": "",
            "text": original,
        }

    @classmethod
    def remove_wake_word(cls, text: str) -> str:

        if not isinstance(text, str):
            return ""

        original = text.strip()
        lower = original.lower()

        for wake in cls.WAKE_WORDS:

            if lower == wake:
                return ""

            prefix = wake + " "

            if lower.startswith(prefix):
                return original[len(wake):].strip()

        return original

    @classmethod
    def parse(cls, text: str) -> dict:
        return cls.detect(text)