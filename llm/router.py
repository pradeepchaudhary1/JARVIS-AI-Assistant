"""
LLM Router
"""

from __future__ import annotations

from llm.client_groq import GroqClient
from llm.client_ollama import OllamaClient


class LLMRouter:

    def __init__(self):
        self.providers = [
            ("groq", GroqClient()),
            ("ollama", OllamaClient()),
        ]

    def ask(self, prompt: str):
        last_error = None

        for _, provider in self.providers:
            try:
                return provider.ask(prompt)
            except Exception as exc:
                last_error = exc
                continue

        if last_error is not None:
            raise last_error

        raise RuntimeError("No LLM provider available")