"""
JARVIS Production Speech Engine
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

            text = self.recognizer.recognize_google(audio)

            return {
                "status": "success",
                "text": text
            }

        except sr.WaitTimeoutError:

            return {
                "status": "timeout",
                "text": ""
            }

        except sr.UnknownValueError:

            return {
                "status": "unknown",
                "text": ""
            }

        except sr.RequestError:

            return {
                "status": "offline",
                "text": ""
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }