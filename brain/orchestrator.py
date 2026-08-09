"""
JARVIS Brain Orchestrator
Production Ready
"""

from brain.router import Router
from brain.dispatcher import Dispatcher
from brain.context import ContextManager
from brain.conversation import ConversationManager

from llm.router import LLMRouter

from memory.short_memory import ShortMemory
from memory.long_memory import LongMemory

from brain.error_handler import ErrorHandler
from brain.logger import JarvisLogger


class Brain:

    def __init__(self):

        self.router = Router()
        self.dispatcher = Dispatcher()

        self.context = ContextManager()
        self.conversation = ConversationManager()

        self.short_memory = ShortMemory()
        self.long_memory = LongMemory()

        self.llm = LLMRouter()

    def process(self, user_message: str):

        try:

            # ---------------------------------
            # Save User Message
            # ---------------------------------

            self.conversation.add_user_message(user_message)
            self.short_memory.add("user", user_message)

            # ---------------------------------
            # Context
            # ---------------------------------

            context = self.context.build()

            # ---------------------------------
            # Long Memory Snapshot
            # ---------------------------------

            long_memory = self.long_memory.all()

            # ---------------------------------
            # Route
            # ---------------------------------

            route = self.router.route(user_message)

            # ---------------------------------
            # Execute Tool
            # ---------------------------------

            tool_result = self.dispatcher.dispatch(
                tool=route,
                command=user_message
            )

            # ---------------------------------
            # Assistant Reply
            # ---------------------------------

            if tool_result.get("status") == "success":

                tool_type = tool_result.get("type", "")

                if tool_type == "installed_app":

                    assistant_reply = f"{user_message} completed."

                elif tool_type == "path_app":

                    assistant_reply = f"{user_message} completed."

                elif tool_type == "application":

                    assistant_reply = f"{user_message} completed."

                elif tool_type == "website":

                    name = tool_result.get("name", "")

                    if tool_result.get("query"):

                        assistant_reply = (
                            f"{name.title()} search opened for "
                            f"{tool_result['query']}."
                        )
                    else:
                        assistant_reply = f"{name.title()} opened."

                elif tool_type == "search":

                    assistant_reply = (
                        f"Searching for {tool_result['query']}."
                    )

                else:

                    assistant_reply = "Done."

            else:

                assistant_reply = self.llm.ask(user_message)

            # ---------------------------------
            # Save Assistant Reply
            # ---------------------------------

            self.conversation.add_assistant_message(
                assistant_reply
            )

            self.short_memory.add(
                "assistant",
                assistant_reply
            )

            # ---------------------------------
            # Learn User Information
            # ---------------------------------

            lower = user_message.lower()

            if lower.startswith("my name is"):

                self.long_memory.remember(
                    "owner",
                    user_message[10:].strip()
                )

            elif lower.startswith("my company is"):

                self.long_memory.remember(
                    "company",
                    user_message[13:].strip()
                )

            # ---------------------------------
            # Final Response
            # ---------------------------------

            return {

                "status": "success",

                "context": context,

                "route": route,

                "tool_result": tool_result,

                "assistant_reply": assistant_reply,

                "history": self.conversation.get_recent(),

                "conversation": self.conversation.get_recent(),

                "short_memory": self.short_memory.get(),

                "long_memory": self.long_memory.all(),

            }

        except Exception as e:

            JarvisLogger.error(str(e))

            return ErrorHandler.handle(e)