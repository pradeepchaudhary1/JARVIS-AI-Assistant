"""
JARVIS Dispatcher

Routes commands from the Brain to the appropriate tool/service.

Author: Lumix Branding
"""

from typing import Callable, Dict, Any


class Dispatcher:
    """
    Universal command dispatcher.

    Example:

        dispatcher = Dispatcher()

        dispatcher.dispatch(
            tool="youtube",
            command="open youtube"
        )
    """

    def __init__(self):
        self._handlers: Dict[str, Callable[[str], Any]] = {}

    def register(self, tool: str, handler: Callable[[str], Any]) -> None:
        """
        Register a handler.

        Example:

            dispatcher.register("youtube", youtube_handler)
        """

        self._handlers[tool.lower()] = handler

    def available_tools(self):
        """Return registered tools."""

        return sorted(self._handlers.keys())

    def dispatch(self, tool: str, command: str):

        tool = tool.lower()

        if tool in self._handlers:

            return self._handlers[tool](command)

        return {
            "status": "ok",
            "tool": tool,
            "command": command,
            "message": "No handler registered yet."
        }