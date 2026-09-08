"""
JARVIS Response Handler
Phase 2.3.5

Converts tool execution results into natural assistant replies.
"""


class ResponseHandler:

    @staticmethod
    def handle(user_message: str, tool_result: dict) -> str:

        if not isinstance(tool_result, dict):
            return "Done sir."

        status = tool_result.get("status")

        # ---------------------------------
        # Successful execution
        # ---------------------------------

        if status == "success":

            tool_type = tool_result.get("type", "")

            # Application launched
            if tool_type in (
                "installed_app",
                "path_app",
                "application",
            ):
                return "Done Boss."

            # Website / search
            if tool_type == "website":

                name = tool_result.get("name", "")
                query = tool_result.get("query")

                if query:
                    if name:
                        return f"{name.title()} is open, sir."
                    return "Search opened."

                if name:
                    return f"{name.title()} opened, sir."

                return "Website opened, Boss."

            # Search tool
            if tool_type == "search":

                query = tool_result.get("query", "")

                if query:
                    return f"Searching for that, sir."

                return "Searching, Boss."

            # Close application
            if tool_type == "close":

                name = tool_result.get("name", "")

                if name:
                    return f"{name.title()} closed."

                return "Application closed."

            # File / folder
            if tool_type == "file_launcher":

                target = tool_result.get("target", "")

                if target:
                    return f"{target.title()} opened, sir."

                return "File or folder opened."

            # Window operations
            if tool_type in (
                "minimize",
                "maximize",
                "restore",
            ):
                return "Done sir."

            # Generic success
            return "Done sir."

        # ---------------------------------
        # Failure
        # ---------------------------------

        if status == "error":
            return "Sorry Boss, I couldn't complete that."

        # ---------------------------------
        # Timeout
        # ---------------------------------

        if status == "timeout":
            return "Sorry Boss, that took too long. Please try again."

        # ---------------------------------
        # Unknown state
        # ---------------------------------

        return "Done Sir."