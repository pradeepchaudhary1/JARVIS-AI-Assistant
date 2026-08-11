"""
JARVIS Speech Engine

Microphone → Speech Recognition → Text
"""

from __future__ import annotations

import speech_recognition as sr

from voice.microphone_manager import MicrophoneManager


class SpeechEngine:

    def __init__(self):

        self.manager = MicrophoneManager()

        from voice.audio_optimizer import AudioOptimizer

        self.recognizer = AudioOptimizer.optimize(
            self.manager.recognizer
        )

    def recognize(self):

        microphone = self.manager.get_default_microphone()

        try:

            # ---------------------------------
            # Microphone
            # ---------------------------------

            with microphone as source:

                print("🎤 Calibrating...")

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                print("🎤 Listening...")

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            # ---------------------------------
            # Speech → Text
            # ---------------------------------

            print("🧠 Recognizing...")

            text = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            text = text.strip()

            if not text:

                return {
                    "status": "empty",
                    "text": ""
                }

            return {
                "status": "success",
                "text": text
            }

        # ---------------------------------
        # Microphone timeout
        # ---------------------------------

        except sr.WaitTimeoutError:

            return {
                "status": "timeout",
                "text": ""
            }

        # ---------------------------------
        # Speech not understood
        # ---------------------------------

        except sr.UnknownValueError:

            return {
                "status": "unknown",
                "text": ""
            }

        # ---------------------------------
        # Google/API/network failure
        # ---------------------------------

        except sr.RequestError as e:

            return {
                "status": "offline",
                "text": "",
                "message": str(e)
            }

        # ---------------------------------
        # Unexpected failure
        # ---------------------------------

        except Exception as e:

            return {
                "status": "error",
                "text": "",
                "message": str(e)
            }