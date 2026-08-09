"""
JARVIS Production Voice Controller
"""

from __future__ import annotations

from voice.speech_engine import SpeechEngine
from brain.orchestrator import Brain


class VoiceController:

    def __init__(self):

        self.engine = SpeechEngine()
        self.brain = Brain()

    def listen_once(self):

        speech = self.engine.recognize()

        if speech.get("status") != "success":
            return speech

        command = speech.get("text", "").strip()

        for wake in (
            "hey jarvis",
            "hello jarvis",
            "hi jarvis",
            "jarvis"
        ):
            command = command.replace(wake, "").strip()

        if not command:
            return {
                "status": "empty",
                "text": ""
            }

        result = self.brain.process(command)

        return result