"""
JARVIS Windows Installed Application Scanner
"""

from __future__ import annotations

import os
from pathlib import Path


SEARCH_DIRS = [

    os.environ.get("ProgramFiles", r"C:\Program Files"),

    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),

    os.environ.get("LOCALAPPDATA", ""),

]


class WindowsAppScanner:

    def __init__(self):

        self.apps = {}

        self.scan()

    def scan(self):

        for base in SEARCH_DIRS:

            if not base:
                continue

            if not os.path.exists(base):
                continue

            for root, dirs, files in os.walk(base):

                for file in files:

                    if file.lower().endswith(".exe"):

                        name = Path(file).stem.lower()

                        if name not in self.apps:

                            self.apps[name] = os.path.join(root, file)

    def get(self, name: str):

        return self.apps.get(name.lower())

    def all(self):

        return self.apps