"""
JARVIS Filesystem Tool
"""

from __future__ import annotations

import os


class FileSystemTool:

    @staticmethod
    def current_directory():

        return {
            "cwd": os.getcwd()
        }