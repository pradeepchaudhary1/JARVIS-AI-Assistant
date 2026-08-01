"""
LLM Router
"""

from llm.client_groq import GroqClient
from llm.client_ollama import OllamaClient


class LLMRouter:

    def __init__(self):

        self.groq = GroqClient()

        self.ollama = OllamaClient()

    def ask(self, prompt: str):

        try:

            return self.groq.ask(prompt)

        except Exception:

            return self.ollama.ask(prompt)