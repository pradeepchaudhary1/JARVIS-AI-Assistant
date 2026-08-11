"""
JARVIS Continuous Voice Loop

Wake Word → Speech Recognition → Brain → Tool → Response → TTS
"""

from __future__ import annotations

import time

from voice.voice_controller import VoiceController
from voice.wake_word import WakeWord
from voice.assistant_state import AssistantState
from voice.tts import TTS


class VoiceLoop:

    def __init__(self):

        self.controller = VoiceController()
        self.wake = WakeWord()
        self.state = AssistantState()
        self.tts = TTS()

    def _is_exit_command(self, command: str) -> bool:

        command = command.lower().strip()

        exit_commands = (
            "exit",
            "quit",
            "stop",
            "bye",
            "goodbye",
            "exit jarvis",
            "quit jarvis",
            "stop jarvis",
            "shutdown jarvis",
            "goodbye jarvis",
        )

        return command in exit_commands

    def _speak(self, text: str):

        if not text:
            return {
                "status": "empty",
                "text": ""
            }

        result = self.tts.speak(text)

        if result.get("status") != "success":

            print("⚠ TTS failed:")
            print(result)

        return result

    def start(self):

        print("=" * 50)
        print("JARVIS Sleeping...")
        print("Say 'Hey Jarvis' to wake.")
        print("=" * 50)

        while True:

            # ==================================================
            # SLEEPING / WAKE WORD MODE
            # ==================================================

            if self.state.is_sleeping():

                speech = self.controller.engine.recognize()

                if speech.get("status") != "success":
                    continue

                text = speech.get("text", "").strip()

                if not text:
                    continue

                if self.wake.detected(text):

                    print()
                    print("Wake Word Detected")
                    print("Listening...")

                    self.state.wake()

                    continue

            # ==================================================
            # AUTO SLEEP
            # ==================================================

            if self.state.expired():

                print()
                print("No activity detected.")
                print("Sleeping...")

                self.state.sleep()

                continue

            # ==================================================
            # LISTEN FOR COMMAND
            # ==================================================

            result = self.controller.listen_once()

            status = result.get("status")

            # --------------------------------------------------
            # Recognition failure
            # --------------------------------------------------

            if status != "success":

                if status == "timeout":

                    print("⏱ Listening timed out.")

                elif status == "unknown":

                    print("❓ Could not understand.")

                elif status == "offline":

                    print("🌐 Speech recognition is offline.")

                else:

                    print("❌ Voice error:")
                    print(result)

                continue

            # ==================================================
            # GET RECOGNIZED COMMAND
            # ==================================================

            intent = result.get("intent", {})

            command = intent.get("command", "").strip()

            # Fallback to conversation history
            if not command:

                history = result.get("history", [])

                if len(history) >= 2:

                    command = history[-2].get(
                        "content",
                        ""
                    ).strip()

            if not command:

                print("⚠ Empty command.")

                continue

            # ==================================================
            # EXIT COMMAND
            # ==================================================

            if self._is_exit_command(command):

                print()
                print("🛑 JARVIS voice mode stopping...")

                self._speak("Goodbye sir.")

                self.state.sleep()

                print("JARVIS stopped.")

                break

            # ==================================================
            # DISPLAY RESULT
            # ==================================================

            reply = result.get(
                "assistant_reply",
                ""
            ).strip()

            print()
            print("You :", command)
            print("Jarvis :", reply)

            # ==================================================
            # SPEAK RESPONSE
            # ==================================================

            if reply:

                speech_result = self._speak(reply)

                result["speech_result"] = speech_result

            # ==================================================
            # ACTIVITY UPDATE
            # ==================================================

            self.state.touch()

            print()
            print("🎤 Listening for next command...")

            time.sleep(0.2)