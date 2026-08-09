"""
JARVIS Continuous Voice Loop
"""

from __future__ import annotations

import time

from voice.voice_controller import VoiceController
from voice.wake_word import WakeWord
from voice.assistant_state import AssistantState


class VoiceLoop:

    def __init__(self):

        self.controller = VoiceController()

        self.wake = WakeWord()

        self.state = AssistantState()

    def start(self):

        print("=" * 50)
        print("JARVIS Sleeping...")
        print("Say 'Hey Jarvis' to wake.")
        print("=" * 50)

        while True:

            if self.state.is_sleeping():
                speech = self.controller.engine.recognize()

                if speech.get("status") != "success":
                    continue
                
                text = speech.get("text", "")

                if self.wake.detected(text):

                    print()

                    print("Wake Word Detected")

                    print("Listening...")

                    self.state.wake()

                    continue

            if self.state.expired():

                print()

                print("No activity detected.")

                print("Sleeping...")

                self.state.sleep()

                continue

            result = self.controller.listen_once()

            status = result.get("status")

            if status != "success":

                print(result)
                continue

            command = ""

            history = result.get("history", [])

            if history:
                command = history[-2]["content"]

            print()
            print("You :", command)
            print("Jarvis :", result["assistant_reply"])

            self.state.touch()

            print()

            command = command.lower().strip()

            if any(

                x == command
                for x in (
                    "exit",
                    "quit",
                    "stop",
                    "bye",
                    "goodbye",
                    "exit jarvis",
                    "quit jarvis",
                    "stop jarvis",
                )
            ):
                print("Goodbye.")
                break

            time.sleep(0.2)