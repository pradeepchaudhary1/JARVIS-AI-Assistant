import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqClient:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError("GROQ_API_KEY not found in .env")

        self.client = Groq(api_key=api_key)

        self.default_model = "llama-3.3-70b-versatile"

    def chat(
        self,
        messages,
        model=None,
        temperature=0.4,
        max_tokens=1024,
    ):

        response = self.client.chat.completions.create(

            model=model or self.default_model,

            messages=messages,

            temperature=temperature,

            max_tokens=max_tokens,

        )

        return response.choices[0].message.content