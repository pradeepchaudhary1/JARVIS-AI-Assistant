"""
JARVIS Groq Client
------------------
Handles communication with Groq LLM.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GroqClient:
    """
    Production Groq client.
    """

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError("GROQ_API_KEY not found.")

        self.client = Groq(api_key=api_key)

        self.model = "llama-3.3-70b-versatile"

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are JARVIS.",
        temperature: float = 0.4,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate response from Groq.
        """

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=temperature,

            max_tokens=max_tokens,
        )

        return response.choices[0].message.content.strip()