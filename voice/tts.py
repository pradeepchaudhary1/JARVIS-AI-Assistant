"""
JARVIS Text To Speech
"""

import asyncio
import os
import tempfile
import threading

import edge_tts
import pygame


class TTS:
    DEFAULT_VOICE = "en-US-AndrewNeural"
    SUPPORTED_VOICES = {
        "en-US-AndrewNeural": "English (US) - Andrew",
        "en-US-JennyNeural": "English (US) - Jenny",
        "hi-IN-MadhurNeural": "Hindi (India) - Madhur",
        "hi-IN-SwaraNeural": "Hindi (India) - Swara",
        "en-IN-PrabhatNeural": "Indian English - Prabhat",
        "en-IN-NeerjaNeural": "Indian English - Neerja",
    }

    def __init__(self, voice_id: str | None = None):
        self.voice_id = self.DEFAULT_VOICE
        if voice_id is not None:
            self.set_voice(voice_id)

    def _normalize_voice_id(self, voice_id: str) -> str:
        if not voice_id:
            return self.DEFAULT_VOICE

        normalized = str(voice_id).strip()
        if normalized not in self.SUPPORTED_VOICES:
            raise ValueError(
                f"Unsupported voice_id '{voice_id}'. Supported: {sorted(self.SUPPORTED_VOICES)}"
            )

        return normalized

    def set_voice(self, voice_id: str) -> str:
        normalized = self._normalize_voice_id(voice_id)
        self.voice_id = normalized
        return normalized

    async def _generate_audio(self, text: str, output_file: str) -> None:
        communicate = edge_tts.Communicate(text, self.voice_id)
        await communicate.save(output_file)

    def _generate_audio_sync(self, text: str, output_file: str) -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self._generate_audio(text, output_file))
            return

        result = {}

        def runner():
            try:
                asyncio.run(self._generate_audio(text, output_file))
                result["ok"] = True
            except Exception as exc:
                result["error"] = exc

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join()

        if "error" in result:
            raise result["error"]

    def _play_audio(self, file_path: str) -> None:
        pygame.init()
        pygame.mixer.init()
        sound = pygame.mixer.Sound(file_path)
        channel = sound.play()

        while channel is not None and channel.get_busy():
            pygame.time.Clock().tick(20)

        pygame.mixer.quit()
        pygame.quit()

    def speak(self, text: str):
        if not text:
            return {
                "status": "empty",
                "text": "",
            }

        temp_file = None

        try:
            temp_fd, temp_file = tempfile.mkstemp(suffix=".mp3")
            os.close(temp_fd)

            self._generate_audio_sync(text, temp_file)
            self._play_audio(temp_file)

            return {
                "status": "success",
                "text": text,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass