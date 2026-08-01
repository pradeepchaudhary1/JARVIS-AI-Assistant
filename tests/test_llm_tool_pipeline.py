from brain.orchestrator import Brain

brain = Brain()

result = brain.process("open youtube")

print()

print(result["result"])

print()

print(result["history"][-1])