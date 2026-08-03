"""
JARVIS Microphone Manager
Production Version
"""

from __future__ import annotations

import speech_recognition as sr


class MicrophoneManager:
    """
    Handles microphone selection and initialization.
    """

    def __init__(self):

        self.recognizer = sr.Recognizer()

    def list_microphones(self):

        return sr.Microphone.list_microphone_names()

    def get_default_microphone(self):

        return sr.Microphone()

    def get_microphone(self, device_index: int):

        return sr.Microphone(device_index=device_index)