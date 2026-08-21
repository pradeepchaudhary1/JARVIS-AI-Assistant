"""
JARVIS Command Safety Layer

Detects dangerous/destructive commands and requires
explicit user confirmation before execution.
"""

from __future__ import annotations


class CommandSafety:

    DANGEROUS_KEYWORDS = (
        "shutdown",
        "shut down",
        "restart",
        "reboot",
        "delete",
        "remove",
        "erase",
        "format",
        "kill all",
        "close all",
    )

    CONFIRMATION_WORDS = (
        "yes",
        "yes jarvis",
        "confirm",
        "confirmed",
        "do it",
        "proceed",
        "haan",
        "ha",
        "kar do",
        "kardo",
    )

    CANCEL_WORDS = (
        "no",
        "no jarvis",
        "cancel",
        "cancel it",
        "stop",
        "don't",
        "dont",
        "nahi",
        "mat karo",
    )

    @classmethod
    def requires_confirmation(cls, command: str) -> bool:

        if not isinstance(command, str):
            return False

        text = command.strip().lower()

        if not text:
            return False

        return any(
            keyword in text
            for keyword in cls.DANGEROUS_KEYWORDS
        )

    @classmethod
    def is_confirmation(cls, text: str) -> bool:

        if not isinstance(text, str):
            return False

        value = text.strip().lower()

        return value in cls.CONFIRMATION_WORDS

    @classmethod
    def is_cancellation(cls, text: str) -> bool:

        if not isinstance(text, str):
            return False

        value = text.strip().lower()

        return value in cls.CANCEL_WORDS

    @classmethod
    def confirmation_required_response(cls, command: str) -> dict:

        return {
            "status": "confirmation_required",
            "command": command,
            "message": (
                f"Sir, '{command}' is a potentially dangerous command. "
                "Please confirm before I execute it."
            )
        }