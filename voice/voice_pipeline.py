"""
JARVIS Voice Pipeline

Voice → Wake Word → Brain → Tool → Response → TTS
"""

import re
import time

from voice.wake_word import WakeWordDetector
from voice.listener import VoiceListener
from voice.tts import TTS
from brain.orchestrator import Brain


class VoicePipeline:

    CONVERSATION_WINDOW_SECONDS = 15

    @staticmethod
    def _normalize_wake_text(text):
        normalized = " ".join((text or "").lower().split())
        separator = r"[\s,.;:!?()\[\]{}\"'\-]+"
        normalized = re.sub(
            rf"^(hey|hello|hi){separator}jarvis(?:{separator}|$)",
            r"\1 jarvis ",
            normalized,
            count=1,
        )
        return " ".join(normalized.split())

    @staticmethod
    def _extract_wake_command(text):
        command = (text or "").strip()
        separator = r"[\s,.;:!?()\[\]{}\"'\-]+"
        command = re.sub(
            rf"^(?:hey|hello|hi){separator}jarvis(?:{separator}|$)",
            "",
            command,
            count=1,
            flags=re.IGNORECASE,
        )
        return re.sub(
            rf"^jarvis(?:{separator}|$)",
            "",
            command,
            count=1,
            flags=re.IGNORECASE,
        ).strip()

    EXIT_COMMANDS = {
        "exit",
        "exit jarvis",
        "stop",
        "stop jarvis",
        "quit",
        "quit jarvis",
        "goodbye jarvis",
        "shutdown jarvis",
    }

    @classmethod
    def _is_exit_command(cls, text):
        normalized = " ".join((text or "").lower().split())
        normalized = re.sub(r"[,.!?;:]+", " ", normalized)
        normalized = " ".join(normalized.split())

        if normalized in cls.EXIT_COMMANDS:
            return True

        exit_patterns = (
            r"^exit jarvis(?: please)?$",
            r"^please exit jarvis$",
            r"^jarvis exit$",
            r"^stop jarvis(?: please)?$",
            r"^please stop jarvis$",
            r"^jarvis stop$",
            r"^quit jarvis(?: please)?$",
            r"^please quit jarvis$",
            r"^jarvis quit$",
        )

        return any(
            re.fullmatch(pattern, normalized)
            for pattern in exit_patterns
        )
    
    def __init__(self):

        self.wake_word = WakeWordDetector()
        self.listener = VoiceListener()
        self.brain = Brain()
        self.tts = TTS()
    
    def run(self, skip_wake_gate=False):

        # ---------------------------------
        # Speech → Text
        # ---------------------------------

        result = self.listener.listen()

        if result.get("status") != "success":
            return result

        text = result.get("text", "").strip()

        if not text:

            return {
                "status": "empty",
                "text": "",
            }

        if self._is_exit_command(text):
            return {
                "status": "stopped",
                "text": text,
                "command": text,
            }

        # ---------------------------------
        # Wake Word Gate
        # ---------------------------------

        if skip_wake_gate:

            command = text

        else:

            wake_result = self.wake_word.detect(
                self._normalize_wake_text(text)
            )

            # Wake word not detected
            if wake_result["status"] == "ignored":

                return {
                    "status": "ignored",
                    "text": text,
                    "wake_word": False,
                    "command": "",
                    "message": "Wake word not detected.",
                }

            # Wake word only
            if wake_result["status"] == "wake_only":

                return {
                    "status": "wake",
                    "text": text,
                    "wake_word": True,
                    "command": "",
                }

            # Invalid wake-word result
            if wake_result["status"] != "command":

                return wake_result

            # Extract command only when wake_result exists
            command = self._extract_wake_command(text)

        # ---------------------------------
        # Empty command
        # ---------------------------------

        if not command:

            return {
                "status": "empty",
                "text": text,
                "command": "",
            }

        normalized_command = " ".join(command.lower().split())
        if self._is_exit_command(normalized_command):
            return {
                "status": "stopped",
                "text": text,
                "command": normalized_command,
            }

        # ---------------------------------
        # Command → Brain
        # ---------------------------------

        brain_result = self.brain.process(command)

        if brain_result.get("status") != "success":
            return brain_result

        # ---------------------------------
        # Brain → Assistant Reply
        # ---------------------------------

        reply = brain_result.get(
            "assistant_reply",
            "",
        ).strip()

        if not reply:


            brain_result["spe" \
            "ech_result"] = {
                "status": "empty",
                "text": "",
            }

            return brain_result

        # ---------------------------------
        # Assistant Reply → TTS
        # ---------------------------------

        speech_result = self.tts.speak(reply)

        brain_result["speech_result"] = speech_result

        # ---------------------------------
        # TTS Failure
        # ---------------------------------

        if speech_result.get("status") != "success":

            brain_result["status"] = "error"
            brain_result["speech_error"] = speech_result

        return brain_result


    # =================================
    # Continuous Voice Loop
    # =================================

    def run_loop(self):

        print("\n" + "=" * 50)
        print("JARVIS CONTINUOUS VOICE MODE")
        print("=" * 50)

        print("\n🎤 JARVIS is listening...")
        print("Say 'Hey Jarvis' to issue a command.")
        print("Say 'exit Jarvis' to quit.")

        try:

            awaiting_command = False
            conversation_deadline = None

            while True:

                if (
                    conversation_deadline is not None
                    and time.monotonic() >= conversation_deadline
                ):
                    conversation_deadline = None

                result = self.run(
                    skip_wake_gate=(
                        awaiting_command
                        or conversation_deadline is not None
                    )
                )
                awaiting_command = False

                status = result.get("status")

                # -----------------------------
                # Ignored speech
                # -----------------------------

                if status == "ignored":

                    print("🔕 Wake word not detected.")
                    continue

                # -----------------------------
                # Wake word only
                # -----------------------------

                if status == "wake":

                    print("👂 Wake word detected.")
                    print("🎤 Listening for command...")
                    awaiting_command = True
                    continue

                # -----------------------------
                # Timeout
                # -----------------------------

                if status == "timeout":

                    print("⏱️ Listening timed out.")
                    continue

                # -----------------------------
                # Unknown speech
                # -----------------------------

                if status == "unknown":

                    print("❓ Could not understand.")
                    continue

                # -----------------------------
                # Offline
                # -----------------------------

                if status == "offline":

                    print("🌐 Speech recognition is offline.")
                    return result

                # -----------------------------
                # Local exit command
                # -----------------------------

                if status == "stopped":

                    print("\n🛑 JARVIS voice mode stopping...")

                    self.tts.speak(
                        "Goodbye sir."
                    )

                    return result

                # -----------------------------
                # Empty
                # -----------------------------

                if status == "empty":

                    print("⚠️ Empty input.")
                    continue

                # -----------------------------
                # Error
                # -----------------------------

                if status == "error":

                    print("❌ Voice pipeline error:")
                    print(result)
                    continue

                # -----------------------------
                # Successful command
                # -----------------------------

                if status == "success":

                    conversation_deadline = (
                        time.monotonic()
                        + self.CONVERSATION_WINDOW_SECONDS
                    )

                    print("\n✅ Command completed.")
                    print("\n🎤 Listening for next command...")

        except KeyboardInterrupt:

            print("\n\n🛑 JARVIS voice mode stopping...")

            self.tts.speak(
                "Voice mode stopped."
            )

            return {
                "status": "stopped",
                "reason": "keyboard_interrupt",
            }