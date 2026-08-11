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

        if result["status"] != "success":
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