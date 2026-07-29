"""
JARVIS Ollama Client
Production Ready
"""

from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:

    def __init__(self):

        self.url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434"
        )

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "hermes3:latest"
        )

    def ask(self, prompt: str) -> str:

        response = requests.post(

            f"{self.url}/api/generate",

            json={

                "model": self.model,

                "prompt": prompt,

                "stream": False

            },

            timeout=120

        )

        response.raise_for_status()

        return response.json()["response"]