"""
JARVIS AI Assistant

Module: Conversation Manager
Purpose: Maintain conversation history between user and assistant.
Author: JARVIS V3
Version: 3.0
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List


class ConversationManager:
    """
    Maintains rolling conversation history.
    """

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._history = deque(maxlen=max_messages)

    def add_user(self, message: str) -> None:
        self._history.append({
            "role": "user",
            "content": message
        })

    def add_assistant(self, message: str) -> None:
        self._history.append({
            "role": "assistant",
            "content": message
        })

    def get_history(self) -> List[Dict]:
        return list(self._history)

    def clear(self) -> None:
        self._history.clear()

    def size(self) -> int:
        return len(self._history)