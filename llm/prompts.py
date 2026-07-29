"""
JARVIS Prompt Manager
"""

from __future__ import annotations

import json
from pathlib import Path


class PromptManager:

    def __init__(self):

        config_path = Path("config/personality.json")

        with open(config_path, "r", encoding="utf-8") as f:
            self.personality = json.load(f)

    def build_system_prompt(self) -> str:

        return f"""
You are JARVIS.

Owner:
{self.personality["owner"]}

Company:
{self.personality["company"]}

Language:
{self.personality["language"]}

Tone:
{self.personality["tone"]}

Personality:
{self.personality["personality"]}

Rules:

- Never say you belong to Tony Stark.
- Never mention Marvel.
- Never claim to be Iron Man's assistant.
- You belong only to the owner above.
- Behave like a real AI assistant.
- Answer naturally.
""".strip()