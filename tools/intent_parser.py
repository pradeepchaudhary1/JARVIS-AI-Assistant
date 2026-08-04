"""
JARVIS Intent Parser
"""

from __future__ import annotations

from tools.command_parser import CommandParser


class IntentParser:

    SEARCH_WORDS = {

        "search",
        "find",
        "look",
        "google",

        "searching",

        "khojo",
        "dhundo",
        "dhoondo",

        "par"
    }

    def __init__(self):

        self.parser = CommandParser()

    def parse(self, command: str):

        cleaned = self.parser.parse(command)

        words = cleaned.split()

        if not words:

            return {

                "intent": "none",

                "target": "",

                "query": ""
            }

        target = words[0]

        query = ""

        for i, word in enumerate(words):

            if word in self.SEARCH_WORDS:

                remaining = words[i + 1:]

                while remaining and remaining[0] in self.SEARCH_WORDS:
                    remaining.pop(0)

                query = " ".join(remaining)

                break

        return {

            "intent": "open",

            "target": target,

            "query": query
        }