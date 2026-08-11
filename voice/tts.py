"""
JARVIS Text To Speech
"""

import pyttsx3


class TTS:

    def __init__(self):
        self.engine = pyttsx3.init()

        self.engine.setProperty("rate", 175)
        self.engine.setProperty("volume", 1.0)

    def speak(self, text: str):

        if not text:
            return {
                "status": "empty",
                "text": ""
            }

        try:
            self.engine.say(text)
            self.engine.runAndWait()

            return {
                "status": "success",
                "text": text
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }