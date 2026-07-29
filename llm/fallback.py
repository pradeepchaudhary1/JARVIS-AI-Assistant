"""
LLM Failover Manager
"""

from __future__ import annotations

from llm.client_groq import GroqClient
from llm.client_ollama import OllamaClient


class FailoverLLM:

    """
    Groq

    ↓

    Ollama

    ↓

    Default response
    """

    def __init__(self):

        self.groq = GroqClient()

        self.ollama = OllamaClient()

    def generate(self, prompt: str) -> str:

        # Try Groq

        try:

            return self.groq.generate(prompt)

        except Exception:

            pass

        # Try Ollama

        try:

            return self.ollama.generate(prompt)

        except Exception:

            pass

        return "Sorry Boss, every AI model is unavailable right now."