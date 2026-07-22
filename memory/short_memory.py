"""
short_memory.py
Holds the CURRENT conversation/session only — like RAM, not disk.
Resets every time JARVIS restarts. Used for immediate context
(last N messages, current task being worked on, active mood).

This does NOT replace jarvis_memory.py (which is long-term, file-based).
Think of it as: short_memory = what JARVIS is thinking about RIGHT NOW.
"""
import time

class ShortMemory:
    def __init__(self, max_messages=20):
        self.max_messages = max_messages
        self.messages = []          # [{role, content, ts}]
        self.active_task = None     # e.g. "writing youtube script"
        self.active_agent = None    # e.g. "developer_agent" (used later in Step 5)
        self.session_start = time.time()

    def add(self, role, content):
        self.messages.append({
            "role": role,
            "content": content,
            "ts": time.time()
        })
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_recent(self, n=10):
        return self.messages[-n:]

    def set_active_task(self, task_text):
        self.active_task = task_text

    def clear_active_task(self):
        self.active_task = None

    def set_active_agent(self, agent_name):
        self.active_agent = agent_name

    def session_duration_minutes(self):
        return round((time.time() - self.session_start) / 60, 1)

    def to_groq_messages(self):
        """Convert to the {role, content} format Groq's chat API expects."""
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

    def reset(self):
        self.messages = []
        self.active_task = None
        self.active_agent = None
        self.session_start = time.time()


# Singleton instance — import this everywhere instead of creating new ones
short_mem = ShortMemory()

if __name__ == "__main__":
    short_mem.add("user", "Jarvis time bata do")
    short_mem.add("assistant", "Sir, abhi 9 baj rahe hain")
    print(short_mem.get_recent())
    print("Session minutes:", short_mem.session_duration_minutes())
