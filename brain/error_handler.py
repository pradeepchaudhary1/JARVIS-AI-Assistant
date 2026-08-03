"""
JARVIS Error Handler
Production Exception Management
"""

from __future__ import annotations

import traceback
from datetime import datetime


class ErrorHandler:


    @staticmethod
    def handle(error: Exception):

        return {

            "status": "error",

            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "error_type": type(error).__name__,

            "message": str(error),

            "trace":
                traceback.format_exc()

        }



    @staticmethod
    def safe_execute(function, *args, **kwargs):

        try:

            return {

                "status": "success",

                "result":
                    function(*args, **kwargs)

            }


        except Exception as e:

            return ErrorHandler.handle(e)