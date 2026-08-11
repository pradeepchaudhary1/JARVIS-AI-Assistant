"""
JARVIS Intent Dispatcher

Phase 2.3.3
Connects IntentDetector output to the existing Dispatcher.
"""

from __future__ import annotations

from brain.intent_detector import IntentDetector
from brain.dispatcher import Dispatcher


class IntentDispatcher:

    def __init__(self):
        self.detector = IntentDetector()
        self.dispatcher = Dispatcher()

    def dispatch(self, command: str):

        command = command.strip()

        if not command:
            return {
                "status": "error",
                "message": "Empty command"
            }

        # ---------------------------------
        # Detect intent
        # ---------------------------------

        detected = self.detector.detect(command)

        if detected.get("status") != "success":
            return detected

        intent = detected.get("intent")

        # ---------------------------------
        # Existing Dispatcher mapping
        # ---------------------------------

        # App opening
        if intent == "open_app":
            return self.dispatcher.dispatch(
                "launcher",
                detected.get("command", command)
            )

        # Close application
        if intent == "close_app":
            return self.dispatcher.dispatch(
                "launcher",
                detected.get("command", command)
            )

        # Window controls
        if intent == "minimize_window":
            return self.dispatcher.dispatch(
                "window",
                detected.get("command", command)
            )

        if intent == "maximize_window":
            return self.dispatcher.dispatch(
                "window",
                detected.get("command", command)
            )

        if intent == "restore_window":
            return self.dispatcher.dispatch(
                "window",
                detected.get("command", command)
            )

        # Filesystem
        if intent == "open_folder":
            return self.dispatcher.dispatch(
                "filesystem",
                detected.get("command", command)
            )

        # Web search
        if intent == "web_search":
            return self.dispatcher.dispatch(
                "launcher",
                detected.get("command", command)
            )

        # Time / unknown / future intents
        return {
            "status": "error",
            "intent": intent,
            "message": f"Intent '{intent}' is not integrated yet."
        }