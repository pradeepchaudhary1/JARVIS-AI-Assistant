"""
JARVIS Memory Manager
"""

from __future__ import annotations

from memory.long_memory import LongMemory


class MemoryManager:

    def __init__(self):

        self.long_memory = LongMemory()

    def learn(self, user_message: str):

        text = user_message.lower()

        if "my name is" in text:

            value = user_message.split("my name is", 1)[1].strip()

            self.long_memory.remember("owner_name", value)

        elif "i live in" in text:

            value = user_message.split("i live in", 1)[1].strip()

            self.long_memory.remember("city", value)

        elif "my company is" in text:

            value = user_message.split("my company is", 1)[1].strip()

            self.long_memory.remember("company", value)

    def recall(self, key):

        return self.long_memory.recall(key)