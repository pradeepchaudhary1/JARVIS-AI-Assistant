"""
JARVIS Command Executor
Production Ready

Central execution layer for all tools.
"""

from typing import Callable, Dict, Any


class CommandExecutor:

    def __init__(self):

        self._commands: Dict[str, Callable[[str], Any]] = {}

    # -------------------------------------
    # Register a Tool
    # -------------------------------------

    def register(
        self,
        tool_name: str,
        handler: Callable[[str], Any]
    ) -> None:

        self._commands[tool_name] = handler

    # -------------------------------------
    # Execute Tool
    # -------------------------------------

    def execute(
        self,
        tool_name: str,
        command: str
    ) -> dict:

        handler = self._commands.get(tool_name)

        if handler is None:

            return {

                "status": "error",

                "tool": tool_name,

                "message": f"No executor registered for '{tool_name}'."

            }

        try:

            result = handler(command)

            if isinstance(result, dict):

                return result

            return {

                "status": "success",

                "tool": tool_name,

                "result": result

            }

        except Exception as e:

            return {

                "status": "error",

                "tool": tool_name,

                "message": str(e)

            }

    # -------------------------------------
    # Registered Tools
    # -------------------------------------

    def registered_tools(self):

        return list(self._commands.keys())