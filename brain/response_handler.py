"""
JARVIS Response Handler
Phase 2.3.5

Converts tool execution results into natural assistant replies.
"""

class ResponseHandler:

    @staticmethod
    def handle(user_message: str, tool_result: dict) -> str:

        if not isinstance(tool_result, dict):
            return "Done."

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
                return f"{user_message} completed."

            # Website / search
            if tool_type == "website":

                name = tool_result.get("name", "")
                query = tool_result.get("query")

                if query:
                    return (
                        f"{name.title()} search opened for "
                        f"{query}."
                    )

                if name:
                    return f"{name.title()} opened."

                return "Website opened."

            # Search tool
            if tool_type == "search":

                query = tool_result.get("query", "")

                if query:
                    return f"Searching for {query}."

                return "Searching."

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
                    return f"{target.title()} opened."

                return "File or folder opened."

            # Window operations
            if tool_type in (
                "minimize",
                "maximize",
                "restore",
            ):
                return "Done."

            # Generic success
            return "Done."

        # ---------------------------------
        # Failure
        # ---------------------------------

        if status == "error":

            message = tool_result.get("message")

            if message:
                return f"Sir, I couldn't complete that: {message}"

            return "Sir, I couldn't complete that command."

        # ---------------------------------
        # Timeout / unknown state
        # ---------------------------------

        if status == "timeout":
            return "Sir, the operation timed out. Please try again."

        return "Done."