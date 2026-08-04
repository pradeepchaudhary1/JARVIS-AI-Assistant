"""
JARVIS Universal Launcher
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import shutil

from tools.intent_parser import IntentParser
from tools.multi_command_parser import MultiCommandParser

from tools.command_parser import CommandParser
from tools.windows_app_scanner import WindowsAppScanner
from tools.app_registry import APP_REGISTRY
from tools.browser import BrowserTool


class UniversalLauncher:

    WEBSITE_REGISTRY = {

        "instagram": "https://instagram.com",
        "facebook": "https://facebook.com",
        "youtube": "https://youtube.com",
        "telegram": "https://web.telegram.org",
        "whatsapp": "https://web.whatsapp.com",
        "chatgpt": "https://chat.openai.com",
        "openai": "https://chat.openai.com",
        "github": "https://github.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "linkedin": "https://linkedin.com",
        "twitter": "https://x.com",
        "x": "https://x.com",
        "amazon": "https://amazon.in",
        "flipkart": "https://flipkart.com",
        "netflix": "https://netflix.com",
        "hotstar": "https://hotstar.com",
        "razorpay": "https://razorpay.com",
    }

    def __init__(self):

        self.scanner = WindowsAppScanner()
        # Multi command parser
        self.multi_parser = MultiCommandParser()

        # Single command parser
        self.command_parser = CommandParser()

        # Intent parser
        self.intent = IntentParser()

        alias_file = os.path.join(
            "config",
            "app_aliases.json"
        )

        if os.path.exists(alias_file):

            with open(
                alias_file,
                "r",
                encoding="utf-8"
            ) as f:

                self.aliases = json.load(f)

        else:

            self.aliases = {}

    def launch_multiple(self, command: str):

        commands = self.multi_parser.split(command)

        results = []

        for item in commands:

            result = self.launch(item)

            results.append(result)

        return results

    def launch(self, target: str):

        target = self.command_parser.parse(target)

        intent = self.intent.parse(target)

        target = intent["target"]

        query = intent["query"]

        target = self.aliases.get(
            target,
            target
        )

        # -----------------------------
        # Installed Windows Applications
        # -----------------------------

        exe = self.scanner.get(target)

        if exe:

            subprocess.Popen(exe)

            return {

                "status": "success",
                "type": "installed_app",
                "path": exe

            }

        # -----------------------------------
        # PATH Executables
        # -----------------------------------

        exe = shutil.which(target)

        if exe:
            subprocess.Popen(exe)

            return {

                "status": "success",
                "type": "path_app",
                "path": exe
            }    

        # -----------------------------
        # Manual Registry Apps
        # -----------------------------

        if target in APP_REGISTRY:

            executable = APP_REGISTRY[target]

            try:

                subprocess.Popen(executable)

                return {

                    "status": "success",
                    "type": "application",
                    "name": target

                }

            except Exception:

                pass

        # -----------------------------
        # Websites
        # -----------------------------

        if target in self.WEBSITE_REGISTRY:

            url = self.WEBSITE_REGISTRY[target]
            if query:
                if target == "google":
                    url = (
                        "https://www.google.com/search?q="
                        + urllib.parse.quote(query)
                    )

                elif target == "youtube":
                    url = (
                        "https://www.youtube.com/results?search_query="
                        + urllib.parse.quote(query)
                    )    

                elif target == "github":
                    url = (
                        "https://github.com/search?q="
                        + urllib.parse.quote(query)
                    )

            BrowserTool.open(url)

            return {

                "status": "success",

                "type": "website",

                "name": target,

                "query": query

            }

        # -----------------------------
        # Google Search
        # -----------------------------

        query = urllib.parse.quote(target)

        BrowserTool.open(
            f"https://www.google.com/search?q={query}"
        )

        return {

            "status": "success",
            "type": "search",
            "query": target

        }