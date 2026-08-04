"""
JARVIS Intelligent Command Parser
"""

from __future__ import annotations

import re


class CommandParser:

    OPEN_WORDS = {

        "open",
        "launch",
        "start",
        "run",

        "khol",
        "kholo",
        "kholna",

        "please",
        "jarvis",
        "can",
        "you",

        "my"
    }

    FILLER_WORDS = {

        "mujhe",
        "mera",
        "meri",
        "mere",

        "liye",
        "liya",

        "jara",
        "zara",

        "krke",
        "kar",
        "karo",
        "karu",

        "do",
        "dijiye",
        "de",
        "diya",
        "dun",

        "please",
        "kindly",

        "ab",
        "ek",
        "baar"
    }

    def parse(self, text: str) -> str:

        text = text.lower().strip()

        text = re.sub(r"[^\w\s]", " ", text)

        words = text.split()

        result = []

        for word in words:

            if (
                word not in self.OPEN_WORDS
                and
                word not in self.FILLER_WORDS
            ):
            
                result.append(word)

        return " ".join(result).strip()