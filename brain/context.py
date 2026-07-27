"""
Context Manager
Provides runtime context for JARVIS.
"""

from datetime import datetime
import platform
import os
import getpass


class ContextManager:

    def __init__(self):
        self.session_start = datetime.now()

    def build(self):

        return {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_start": self.session_start.strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
            "user": getpass.getuser(),
            "cwd": os.getcwd(),
            "assistant": "JARVIS V3"
        }