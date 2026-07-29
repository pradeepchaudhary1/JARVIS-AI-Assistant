from llm.fallback import FailoverLLM

llm = FailoverLLM()

print(
    llm.generate(
        "Who are you?"
    )
)