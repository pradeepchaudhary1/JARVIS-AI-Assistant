"""
JARVIS Voice Listener
Production Version
"""

from voice.speech_engine import SpeechEngine


class VoiceListener:

    def __init__(self):

        self.engine = SpeechEngine()

    def listen(self):

        result = self.engine.recognize()

        return result