from brain.orchestrator import Brain

brain = Brain()

brain.long_memory.clear()

brain.process("My name is Pradeep")

brain.process("My company is Lumix Branding")

result = brain.process("Hello")

print(result["long_memory"])

print(brain.long_memory.recall("owner"))

print(brain.long_memory.recall("company"))