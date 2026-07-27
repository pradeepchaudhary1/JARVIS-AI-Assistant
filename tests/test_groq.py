from llm.client_groq import GroqClient

client = GroqClient()

response = client.generate(
    "Say hello in one short sentence."
)

print(response)