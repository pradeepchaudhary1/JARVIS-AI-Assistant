"""
JARVIS Voice Listener
Production Version
"""

from __future__ import annotations

import speech_recognition as sr

from voice.microphone_manager import MicrophoneManager


class VoiceListener:

    def __init__(self):

        self.manager = MicrophoneManager()

        self.recognizer = self.manager.recognizer

    def listen(self):

        mic = self.manager.get_default_microphone()

        with mic as source:

            print("🎤 Listening...")

            audio = self.recognizer.listen(source)

        text = self.recognizer.recognize_google(audio)

        return text