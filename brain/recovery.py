"""
JARVIS Recovery Manager
"""

from __future__ import annotations


class RecoveryManager:

    @staticmethod
    def recover(error: Exception):

        return {
            "status": "recovered",
            "message": str(error)
        }