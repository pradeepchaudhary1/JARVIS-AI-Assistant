"""
JARVIS Intent Detector
Phase 2.3.2

Purpose:
Convert a normalized command into a structured intent.

This module is intentionally isolated.
It does NOT modify Router, Dispatcher, Orchestrator,
VoiceLoop, or any existing Phase 2.2 component.
"""

from __future__ import annotations

import re
from typing import Any


class IntentDetector:

    OPEN_WORDS = {
        "open",
        "launch",
        "start",
        "run",
    }

    CLOSE_WORDS = {
        "close",
        "exit",
        "quit",
        "shutdown",
        "terminate",
    }

    MINIMIZE_WORDS = {
        "minimize",
        "minimise",
    }

    MAXIMIZE_WORDS = {
        "maximize",
        "maximise",
    }

    RESTORE_WORDS = {
        "restore",
    }

    SEARCH_WORDS = {
        "search",
        "google",
        "find",
        "look",
    }

    TIME_WORDS = {
        "time",
        "clock",
    }

    FOLDER_WORDS = {
        "folder",
        "directory",
        "pictures",
        "picture",
        "photos",
        "photo",
        "videos",
        "video",
        "downloads",
        "download",
        "documents",
        "document",
        "desktop",
        "music",
    }

    @staticmethod
    def _clean(text: str) -> str:
        """
        Normalize basic punctuation and whitespace.

        The command normalizer remains a separate layer.
        """

        if not text:
            return ""

        text = text.lower().strip()

        text = re.sub(r"[^\w\s]", " ", text)

        text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def _result(
        intent: str,
        command: str,
        **extra: Any,
    ) -> dict[str, Any]:
        """
        Build a consistent detector response.
        """

        result = {
            "status": "success",
            "intent": intent,
            "command": command,
        }

        result.update(extra)

        return result

    @classmethod
    def detect(cls, text: str) -> dict[str, Any]:
        """
        Detect the primary intent of a normalized command.
        """

        command = cls._clean(text)

        if not command:
            return {
                "status": "empty",
                "intent": "unknown",
                "command": "",
            }

        words = command.split()

        first_word = words[0]

        # -----------------------------------------
        # OPEN
        # -----------------------------------------

        if first_word in cls.OPEN_WORDS:

            target = cls._extract_target(
                command,
                cls.OPEN_WORDS,
            )

            if target:

                if (
                    target.startswith("my ")
                    or target in cls.FOLDER_WORDS
                ):
                    return cls._result(
                        "open_folder",
                        command,
                        target=target.replace("my ", "", 1),
                    )

                return cls._result(
                    "open_app",
                    command,
                    target=target,
                )

            return cls._result(
                "open",
                command,
            )

        # -----------------------------------------
        # CLOSE
        # -----------------------------------------

        if first_word in cls.CLOSE_WORDS:

            target = cls._extract_target(
                command,
                cls.CLOSE_WORDS,
            )

            return cls._result(
                "close_app",
                command,
                target=target,
            )

        # -----------------------------------------
        # MINIMIZE
        # -----------------------------------------

        if first_word in cls.MINIMIZE_WORDS:

            target = cls._extract_target(
                command,
                cls.MINIMIZE_WORDS,
            )

            return cls._result(
                "minimize_window",
                command,
                target=target,
            )

        # -----------------------------------------
        # MAXIMIZE
        # -----------------------------------------

        if first_word in cls.MAXIMIZE_WORDS:

            target = cls._extract_target(
                command,
                cls.MAXIMIZE_WORDS,
            )

            return cls._result(
                "maximize_window",
                command,
                target=target,
            )

        # -----------------------------------------
        # RESTORE
        # -----------------------------------------

        if first_word in cls.RESTORE_WORDS:

            target = cls._extract_target(
                command,
                cls.RESTORE_WORDS,
            )

            return cls._result(
                "restore_window",
                command,
                target=target,
            )

        # -----------------------------------------
        # SEARCH
        # -----------------------------------------

        if (
            first_word in cls.SEARCH_WORDS
            or " search " in f" {command} "
        ):

            return cls._detect_search(command)

        # -----------------------------------------
        # TIME
        # -----------------------------------------

        if (
            "time" in words
            or "clock" in words
        ):

            return cls._result(
                "time",
                command,
            )

        # -----------------------------------------
        # FOLDER / FILESYSTEM
        # -----------------------------------------

        if (
            "my pictures" in command
            or "my photos" in command
            or "my videos" in command
            or "my downloads" in command
            or "my documents" in command
            or "my desktop" in command
            or "my music" in command
        ):

            target = cls._extract_folder(command)

            return cls._result(
                "open_folder",
                command,
                target=target,
            )

        # -----------------------------------------
        # UNKNOWN
        # -----------------------------------------

        return cls._result(
            "unknown",
            command,
        )

    @classmethod
    def _extract_target(
        cls,
        command: str,
        words_to_remove: set[str],
    ) -> str:

        words = command.split()

        result = [
            word
            for word in words
            if word not in words_to_remove
            and word not in {"my"}
        ]

        return " ".join(result).strip()

    @staticmethod
    def _extract_folder(command: str) -> str:

        folder_aliases = (
            "pictures",
            "photos",
            "videos",
            "downloads",
            "documents",
            "desktop",
            "music",
        )

        for folder in folder_aliases:

            if folder in command:
                return folder

        return ""

    @classmethod
    def _detect_search(cls, command: str) -> dict[str, Any]:

        words = command.split()

        # search youtube lofi music
        if len(words) >= 3 and words[1] == "youtube":

            return cls._result(
                "web_search",
                command,
                site="youtube",
                query=" ".join(words[2:]),
            )

        # search google python decorators
        if len(words) >= 3 and words[1] == "google":

            return cls._result(
                "web_search",
                command,
                site="google",
                query=" ".join(words[2:]),
            )

        # generic search
        if words[0] == "search":

            return cls._result(
                "web_search",
                command,
                site="default",
                query=" ".join(words[1:]),
            )

        return cls._result(
            "web_search",
            command,
            site="default",
            query=command,
        )