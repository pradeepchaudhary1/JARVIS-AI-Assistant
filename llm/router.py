"""
Smart LLM Router
"""

from llm.client_groq import GroqClient
from llm.client_ollama import OllamaClient


class LLMRouter:

    def __init__(self):

        self.groq = GroqClient()

        self.ollama = OllamaClient()

    def chat(self, message: str):

        try:

            return self.groq.chat(message)

        except Exception:

            return self.ollama.chat(message)