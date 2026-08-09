"""
JARVIS Process Manager
"""

from __future__ import annotations

import subprocess


class ProcessManager:

    PROCESS_MAP = {

        "chrome": "chrome.exe",

        "telegram": "telegram.exe",

        "whatsapp": "WhatsApp.exe",

        "code": "Code.exe",

        "vscode": "Code.exe",

        "spotify": "Spotify.exe",

        "discord": "Discord.exe",

        "excel": "EXCEL.EXE",

        "word": "WINWORD.EXE",

        "powerpoint": "POWERPNT.EXE",

        "paint": "mspaint.exe",

        "calculator": "Calculator.exe",

    }

    @classmethod
    def close(cls, app):

        exe = cls.PROCESS_MAP.get(app.lower())

        if not exe:

            return {

                "status": "error",

                "message": "Unknown application"

            }

        subprocess.call(

            ["taskkill", "/F", "/IM", exe],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

        return {

            "status": "success",

            "type": "close",

            "name": app

        }