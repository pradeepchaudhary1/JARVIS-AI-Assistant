"""
JARVIS Voice Pipeline

Voice → Wake Word → Brain → Tool → Response → TTS
"""

from voice.wake_word import WakeWordDetector
from voice.listener import VoiceListener
from voice.tts import TTS
from brain.orchestrator import Brain


class VoicePipeline:

    def __init__(self):

        self.wake_word = WakeWordDetector()
        self.listener = VoiceListener()
        self.brain = Brain()
        self.tts = TTS()

    def run(self):

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

        # ---------------------------------
        # Wake Word Gate
        # ---------------------------------

        wake_result = self.wake_word.detect(text)

        # No wake word
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

        # Invalid input
        if wake_result["status"] != "command":

            return wake_result

        # ---------------------------------
        # Extract command
        # ---------------------------------

        command = wake_result.get(
            "command",
            "",
        ).strip()

        if not command:

            return {
                "status": "wake",
                "text": text,
                "wake_word": True,
                "command": "",
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

            brain_result["speech_result"] = {
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

            while True:

                result = self.run()

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

                    intent = result.get("intent", {})

                    command = intent.get(
                        "command",
                        "",
                    ).strip().lower()

                    exit_commands = (
                        "exit",
                        "exit jarvis",
                        "stop",
                        "stop jarvis",
                        "quit",
                        "quit jarvis",
                        "goodbye jarvis",
                        "shutdown jarvis",
                    )

                    if command in exit_commands:

                        print("\n🛑 JARVIS voice mode stopping...")

                        self.tts.speak(
                            "Goodbye sir."
                        )

                        return {
                            "status": "stopped",
                            "command": command,
                        }

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