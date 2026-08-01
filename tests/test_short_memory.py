from memory.short_memory import ShortMemory

memory = ShortMemory(limit=3)

memory.add("user", "Hello")
memory.add("assistant", "Hi")
memory.add("user", "How are you?")
memory.add("assistant", "I'm fine.")

print(memory.get())
print("Size:", memory.size())