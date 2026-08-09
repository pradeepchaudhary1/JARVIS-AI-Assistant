"""
Assistant State
"""

from __future__ import annotations

import time

class AssistantState:

    def __init__(self):
        self.sleeping = True
        self.last_active = 0

    def wake(self):
        self.sleeping = False
        self.last_active = time.time()

    def sleep(self):
        self.sleeping = True

    def touch(self):
        self.last_active = time.time()

    def expired(self, timeout=20):
        return (
            not self.sleeping
            and
            (time.time() - self.last_active) > timeout
        )

    def is_sleeping(self):
        return self.sleeping
