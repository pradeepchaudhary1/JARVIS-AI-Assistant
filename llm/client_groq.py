"""
Groq Client
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

from llm.prompts import PromptManager

# Load .env once
load_dotenv()


class GroqClient:
    """
    Production-ready Groq client.
    """

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError("GROQ_API_KEY not found in .env")

        self.client = Groq(api_key=api_key)

        self.prompts = PromptManager()

    def chat(self, message: str) -> str:

        system_prompt = self.prompts.build_system_prompt()

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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