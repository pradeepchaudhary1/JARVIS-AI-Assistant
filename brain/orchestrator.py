"""
JARVIS Brain Orchestrator
Production Ready
"""

from brain.router import Router
from brain.dispatcher import Dispatcher

from brain.response_handler import ResponseHandler

from brain.intent_detector import IntentDetector
from brain.intent_dispatcher import IntentDispatcher

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

        self.intent_detector = IntentDetector()
        self.intent_dispatcher = IntentDispatcher()

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
            # Intent Detection
            # ---------------------------------

            intent = self.intent_detector.detect(user_message)

            # ---------------------------------
            # Intent → Dispatcher
            # ---------------------------------

            route = None
            tool_result = None

            if intent.get("status") == "success":

                detected_intent = intent.get("intent")

                integrated_intents = {
                    "open_app",
                    "close_app",
                    "minimize_window",
                    "maximize_window",
                    "restore_window",
                    "open_folder",
                    "web_search",
                }

                if detected_intent in integrated_intents:

                    tool_result = self.intent_dispatcher.dispatch(
                        user_message
                    )

                    route_map = {
                        "open_app": "launcher",
                        "close_app": "launcher",
                        "minimize_window": "window",
                        "maximize_window": "window",
                        "restore_window": "window",
                        "open_folder": "filesystem",
                        "web_search": "launcher",
                    }

                    route = route_map.get(
                        detected_intent,
                        self.router.route(user_message)
                    )

                    
            # ---------------------------------
            # Legacy Router Fallback
            # ---------------------------------

            if tool_result is None:

                route = self.router.route(user_message)

                tool_result = self.dispatcher.dispatch(
                    tool=route,
                    command=user_message
                )
                
            # ---------------------------------
            # Assistant Reply
            # ---------------------------------
            
            if tool_result is None:

                assistant_reply = self.llm.ask(user_message)

                tool_result = {
                    "status": "success",
                    "type": "llm",
                    "message": "Handled by LLM fallback",
                }

            elif tool_result.get("status") == "success":

                assistant_reply = ResponseHandler.handle(
                    user_message,
                    tool_result,
                )

            else:

                assistant_reply = ResponseHandler.handle(
                    user_message,
                    tool_result,
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

                "intent": intent,

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