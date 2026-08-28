"""
JARVIS Production Dispatcher
"""

from __future__ import annotations

import urllib.parse

from tools.browser import BrowserTool
from tools.universal_launcher import UniversalLauncher
from tools.command_parser import CommandParser
from tools.search_registry import SEARCH_REGISTRY
from tools.process_manager import ProcessManager
from tools.window_manager import WindowManager

class Dispatcher:

    def __init__(self):

        self.launcher = UniversalLauncher()
        self.parser = CommandParser()

    def dispatch(self, tool: str, command: str):

        tool = tool.lower()

        # -------------------------
        # Universal Open Commands
        # -------------------------

        if command.lower().startswith(("close", "kill")):

            target = command.lower()

            target = (
                target
                .replace("close", "")
                .replace("kill", "")
                .strip()
            )

            target = self.parser.parse(target)

            return ProcessManager.close(target)

        if command.lower().startswith("minimize"):

            target = command.lower().replace("minimize", "", 1).strip()

            return WindowManager.minimize(target)


        if command.lower().startswith("maximize"):

            target = command.lower().replace("maximize", "", 1).strip()
    
            return WindowManager.maximize(target)


        if command.lower().startswith("restore"):

            target = command.lower().replace("restore", "", 1).strip()

            return WindowManager.restore(target)
         
        if tool == "launcher":

            target = self.parser.parse(command)

            target = target.strip()

            parts = target.split(maxsplit=1)

            if len(parts) == 2:

                app = parts[0]
                query = " ".join(parts[1:]).strip()

                if app in SEARCH_REGISTRY:

                    url = SEARCH_REGISTRY[app].format(
                        urllib.parse.quote(query)
                    )

                    BrowserTool.open(url)

                    return {

                        "status": "success",
                        "type": "website",
                        "name": app,
                        "query": query

                    }

            return self.launcher.launch(target)

        # -------------------------
        # Browser
        # -------------------------

        elif tool == "browser":

            text = command.lower()

            if "http://" in text or "https://" in text:
                return BrowserTool.open(command.strip())

            return BrowserTool.open("https://google.com")

        # -------------------------
        # Filesystem
        # -------------------------

        elif tool == "filesystem":

            text = command.lower().strip()

            # -------------------------
            # Remove command words
            # -------------------------

            remove_words = (
                "open",
                "launch",
                "start",
                "run",
                "please",
                "jarvis",
                "mujhe",
                "khol",
                "kholo",
                "kholna",
                "the",
                "my"
            )

            for word in remove_words:
                text = text.replace(word, " ")

            # -------------------------
            # Clean target
            # -------------------------

            target = " ".join(text.split()).strip()

            if not target:
                return {
                    "status": "error",
                    "type": "file_launcher",
                    "message": "No file or folder specified."
                }

            # -------------------------
            # File / Folder Launcher
            # -------------------------

            from tools.file_launcher import FileLauncher

            return FileLauncher.open(target)

        # -------------------------

        return {
            "status": "error",
            "tool": tool,
            "message": "Unknown Tool"
        }