"""
JARVIS Confirmation Manager

Handles confirmation for potentially dangerous commands.
"""

from __future__ import annotations


class ConfirmationManager:

    YES_WORDS = (
        "yes",
        "yeah",
        "yep",
        "haan",
        "ha",
        "confirm",
        "confirmed",
        "do it",
        "continue",
    )

    NO_WORDS = (
        "no",
        "nope",
        "nah",
        "nahi",
        "cancel",
        "stop",
        "don't",
        "do not",
    )

    def __init__(self):
        self.pending_command = None

    # --------------------------------------------------
    # Request confirmation
    # --------------------------------------------------

    def request(self, command: str):

        command = command.strip()

        if not command:
            return {
                "status": "error",
                "command": "",
                "message": "Empty command."
            }

        self.pending_command = command

        return {
            "status": "confirmation_required",
            "command": command,
            "message": (
                f"Sir, '{command}' is a potentially dangerous command. "
                "Do you want me to continue?"
            )
        }

    # --------------------------------------------------
    # Handle confirmation response
    # --------------------------------------------------

    def respond(self, response: str):

        response = response.strip().lower()

        if not self.pending_command:

            return {
                "status": "no_pending_confirmation",
                "command": "",
                "message": "There is no command waiting for confirmation."
            }

        command = self.pending_command

        # YES
        if response in self.YES_WORDS:

            self.pending_command = None

            return {
                "status": "confirmed",
                "command": command,
                "message": "Command confirmed."
            }

        # NO
        if response in self.NO_WORDS:

            self.pending_command = None

            return {
                "status": "cancelled",
                "command": command,
                "message": "Command cancelled."
            }

        # UNCLEAR
        return {
            "status": "confirmation_unclear",
            "command": command,
            "message": "Please say yes or no."
        }

    # --------------------------------------------------
    # Pending state
    # --------------------------------------------------

    def has_pending(self) -> bool:
        return self.pending_command is not None

    def get_pending(self):
        return self.pending_command