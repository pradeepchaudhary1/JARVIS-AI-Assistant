from llm.client_groq import GroqClient

ai = GroqClient()

reply = ai.chat(
    "Who are you?"
)

print(reply)