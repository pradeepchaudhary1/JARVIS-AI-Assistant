"""
JARVIS Window Manager
"""

from __future__ import annotations

import pygetwindow as gw


class WindowManager:

    ALIASES = {

        "chrome": "google chrome",

        "vscode": "visual studio code",

        "vs code": "visual studio code",

        "edge": "microsoft edge"

    }

    @staticmethod
    def _find_window(name: str):

        print("Searching:", name)

        titles = gw.getAllTitles()


        name = WindowManager.ALIASES.get(name.lower(), name.lower())

        titles = gw.getAllTitles()

        for title in titles:

            if not title.strip():
                continue

            if name.lower() in title.lower():

                windows = gw.getWindowsWithTitle(title)

                if windows:
                    return windows[0]

        return None

    @classmethod
    def minimize(cls, name):

        win = cls._find_window(name)

        if not win:
            return {
                "status": "error",
                "message": "Window not found"
            }

        win.minimize()

        return {
            "status": "success",
            "type": "minimize",
            "name": name
        }

    @classmethod
    def maximize(cls, name):

        win = cls._find_window(name)

        if not win:
            return {
                "status": "error",
                "message": "Window not found"
            }

        win.maximize()

        return {
            "status": "success",
            "type": "maximize",
            "name": name
        }

    @classmethod
    def restore(cls, name):

        win = cls._find_window(name)

        if not win:
            return {
                "status": "error",
                "message": "Window not found"
            }

        win.restore()

        return {
            "status": "success",
            "type": "restore",
            "name": name
        }