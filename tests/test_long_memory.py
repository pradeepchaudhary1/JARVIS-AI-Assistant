from memory.long_memory import LongMemory

memory = LongMemory()

memory.clear()

memory.remember("owner", "Pradeep")

memory.remember("company", "Lumix Branding")

print(memory.recall("owner"))

print(memory.recall("company"))

print(memory.load())