"""
Groq Client
"""

from __future__ import annotations

from dotenv import load_dotenv
from groq import Groq

from license_manager import read_groq_key
from llm.prompts import PromptManager

# Load .env once
load_dotenv()


class GroqClient:
    """
    Production-ready Groq client.
    """

    def __init__(self):

        api_key = read_groq_key()

        if not api_key:
            raise RuntimeError("No Groq API key available from .jarvis_license or .env")

        self.client = Groq(api_key=api_key)

        self.prompts = PromptManager()

    def chat(self, message: str) -> str:

        system_prompt = self.prompts.build_system_prompt()

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=0.5,
        )

        return response.choices[0].message.content

    def ask(self, message: str) -> str:
        """
        Standard interface used by LLMRouter.
        """
        return self.chat(message)
