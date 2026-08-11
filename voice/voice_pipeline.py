"""
JARVIS Voice Pipeline
Voice → Brain → TTS
"""

from voice.listener import VoiceListener
from voice.tts import TTS
from brain.orchestrator import Brain


class VoicePipeline:

    def __init__(self):

        self.listener = VoiceListener()
        self.brain = Brain()
        self.tts = TTS()

    def run(self):

        # -------------------------
        # Speech → Text
        # -------------------------

        result = self.listener.listen()

        if result.get("status") != "success":
            return result

        text = result.get("text", "").strip()

        if not text:
            return {
                "status": "empty",
                "text": ""
            }

        # -------------------------
        # Text → Brain
        # -------------------------

        brain_result = self.brain.process(text)

        if brain_result.get("status") != "success":
            return brain_result

        # -------------------------
        # Brain → Assistant Reply
        # -------------------------

        reply = brain_result.get(
            "assistant_reply",
            ""
        ).strip()

        if not reply:

            brain_result["speech_result"] = {
                "status": "empty",
                "text": ""
            }

            return brain_result

        # -------------------------
        # Assistant Reply → TTS
        # -------------------------

        speech_result = self.tts.speak(reply)

        brain_result["speech_result"] = speech_result

        # -------------------------
        # TTS Failure
        # -------------------------

        if speech_result.get("status") != "success":

            brain_result["status"] = "error"

            brain_result["speech_error"] = speech_result

        return brain_result

    # ==================================================
    # CONTINUOUS VOICE LOOP
    # ==================================================

    def run_loop(self):

        print("\n" + "=" * 50)
        print("JARVIS CONTINUOUS VOICE MODE")
        print("=" * 50)

        print("\n🎤 JARVIS is listening...")
        print("Say 'exit Jarvis' or 'stop Jarvis' to quit.")

        while True:

            result = self.run()

            # -------------------------
            # Voice recognition failure
            # -------------------------

            if result.get("status") != "success":

                status = result.get("status")

                if status == "timeout":

                    print("⏱️ Listening timed out. Listening again...")
                    continue

                if status == "unknown":

                    print("❓ Could not understand. Listening again...")
                    continue

                if status == "offline":

                    print("🌐 Speech recognition is offline.")
                    return result

                if status == "empty":

                    print("⚠️ Empty command. Listening again...")
                    continue

                print("❌ Voice pipeline error:")
                print(result)

                continue

            # -------------------------
            # Check recognized command
            # -------------------------

            intent = result.get("intent", {})

            command = intent.get(
                "command",
                ""
            ).strip().lower()

            # -------------------------
            # Exit commands
            # -------------------------

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

                print("\n🛑 JARVIS voice mode stopped.")

                self.tts.speak(
                    "Goodbye sir."
                )

                return {
                    "status": "stopped",
                    "command": command
                }

            # -------------------------
            # Command completed
            # -------------------------

            print("\n✅ Command completed.")

            # -------------------------
            # Continue listening
            # -------------------------

            print("\n🎤 Listening for next command...")