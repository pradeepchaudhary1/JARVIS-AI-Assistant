"""
JARVIS Long-Term Memory
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LongMemory:

    def __init__(self, file_path: str = "memory/project_memory.json"):

        self.file = Path(file_path)

        if not self.file.exists():

            self.file.parent.mkdir(parents=True, exist_ok=True)

            self.file.write_text("{}")

    def load(self) -> dict[str, Any]:

        with open(self.file, "r", encoding="utf-8") as f:

            return json.load(f)

    def save(self, data: dict[str, Any]) -> None:

        with open(self.file, "w", encoding="utf-8") as f:

            json.dump(data, f, indent=4)

    def remember(self, key: str, value: Any):

        data = self.load()

        data[key] = value

        self.save(data)

    def recall(self, key: str):

        return self.load().get(key)

    def clear(self):

        self.save({})

    def all(self):

        return self.load()