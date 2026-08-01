"""
Ollama Client
"""

from __future__ import annotations

import os

import requests

from llm.prompts import PromptManager


class OllamaClient:

    def __init__(self):

        self.url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434/api/generate",
        )

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "hermes3:latest",
        )

        self.prompts = PromptManager()

    def chat(self, message: str) -> str:

        prompt = (
            self.prompts.build_system_prompt()
            + "\n\nUser: "
            + message
        )

        response = requests.post(

            self.url,

            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },

            timeout=120,
        )

        response.raise_for_status()

        return response.json()["response"]

    def ask(self, message: str) -> str:
        """
        Standard interface used by LLMRouter.
        """
        return self.chat(message)    