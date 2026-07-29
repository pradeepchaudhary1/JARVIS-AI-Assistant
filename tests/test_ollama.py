from llm.client_ollama import OllamaClient

client = OllamaClient()

print(
    client.ask(
        "Say hello in one sentence."
    )
)