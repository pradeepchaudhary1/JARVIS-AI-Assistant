"""
Conversation Manager
Maintains short-term conversation history for JARVIS.
"""

from typing import Dict, List


class ConversationManager:
    """
    Handles conversation history between user and assistant.
    """

    def __init__(self, history_limit: int = 20):
        self.history_limit = history_limit
        self.history: List[Dict[str, str]] = []

    def _trim_history(self) -> None:
        """Keep only the most recent messages."""
        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit:]

    def add_user_message(self, message: str) -> None:
        """Add a user message."""
        self.history.append(
            {
                "role": "user",
                "content": message
            }
        )
        self._trim_history()

    def add_assistant_message(self, message: str) -> None:
        """Add an assistant message."""
        self.history.append(
            {
                "role": "assistant",
                "content": message
            }
        )
        self._trim_history()

    def get_recent(self) -> List[Dict[str, str]]:
        """Return recent conversation."""
        return self.history.copy()

    def clear(self) -> None:
        """Clear conversation."""
        self.history.clear()

    def export(self) -> List[Dict[str, str]]:
        """Export conversation."""
        return self.history.copy()