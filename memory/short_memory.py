"""
JARVIS Short-Term Memory
"""

from __future__ import annotations

from typing import Dict, List


class ShortMemory:
    """
    Stores the latest conversation messages.

    Automatically removes the oldest messages
    when the configured limit is exceeded.
    """

    def __init__(self, limit: int = 20):

        self.limit = limit
        self.messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str) -> None:

        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        if len(self.messages) > self.limit:
            self.messages.pop(0)

    def get(self) -> List[Dict[str, str]]:

        return list(self.messages)

    def clear(self) -> None:

        self.messages.clear()

    def size(self) -> int:

        return len(self.messages)