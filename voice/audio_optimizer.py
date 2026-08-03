"""
JARVIS Audio Optimizer
Production Version
"""

from __future__ import annotations

import speech_recognition as sr


class AudioOptimizer:

    @staticmethod
    def optimize(recognizer: sr.Recognizer):

        # Automatically adjust to changing environments
        recognizer.dynamic_energy_threshold = True

        # Initial energy level
        recognizer.energy_threshold = 300

        # Pause after speech ends
        recognizer.pause_threshold = 0.8

        # Minimum speech length
        recognizer.phrase_threshold = 0.3

        # Silence before phrase starts
        recognizer.non_speaking_duration = 0.5

        return recognizer