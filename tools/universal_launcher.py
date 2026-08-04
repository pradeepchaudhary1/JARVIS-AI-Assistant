"""
JARVIS Universal Launcher
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import shutil

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

    def launch(self, target: str):

        target = target.lower().strip()

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

            BrowserTool.open(
                self.WEBSITE_REGISTRY[target]
            )

            return {

                "status": "success",
                "type": "website",
                "name": target

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