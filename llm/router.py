from llm.client_groq import GroqClient


class LLMRouter:

    def __init__(self):
        self.groq = GroqClient()

    def ask(self, messages):

        try:
            return self.groq.chat(messages)

        except Exception as e:

            print("Groq Failed:", e)

            return "JARVIS: All online providers unavailable."