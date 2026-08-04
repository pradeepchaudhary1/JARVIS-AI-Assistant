"""
JARVIS Multi Command Parser
"""

from __future__ import annotations

import re


class MultiCommandParser:

    SEPARATORS = [

        " and ",

        " then ",

        " aur ",

        ",",

        ";"

    ]

    def split(self, command: str):

        command = command.lower().strip()

        for separator in self.SEPARATORS:

            command = command.replace(
                separator,
                "|"
            )

        commands = []

        for item in command.split("|"):

            item = item.strip()

            if item:

                commands.append(item)

        return commands