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

from brain.command_safety import CommandSafety
from brain.confirmation_manager import ConfirmationManager

from brain.tier_gate import TierGate
from memory.redis_store import get_memory_backend
from license_manager import read_license_data


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

        self.command_safety = CommandSafety()
        self.confirmation_manager = ConfirmationManager()

        self.tier_gate = TierGate()

        self.llm = LLMRouter()

    def _check_daily_limit(self):
        tier_config = self.tier_gate.tiers.get(self.tier_gate.current_tier, {})
        max_daily_commands = tier_config.get("max_daily_commands")

        if max_daily_commands is None:
            return None

        email, _ = read_license_data()
        if not email:
            email = "default@jarvis.local"

        backend = get_memory_backend()
        current_count = backend.increment_daily_usage(email)

        if current_count > max_daily_commands:
            return {
                "status": "limit_reached",
                "assistant_reply": "Sir, aaj ki command limit khatam ho gayi.",
            }

        return None

    def process_confirmation(self, response: str):

        try:

            result = self.confirmation_manager.respond(
                response
            )

            status = result.get("status")

            # ---------------------------------
            # Confirmation cancelled
            # ---------------------------------

            if status == "cancelled":

                return {
                    "status": "cancelled",
                    "command": result.get("command", ""),
                    "assistant_reply": "Okay sir, command cancelled.",
                    "confirmation": result,
                }

            # ---------------------------------
            # Confirmation unclear
            # ---------------------------------

            if status == "confirmation_unclear":

                return {
                    "status": "confirmation_required",
                    "command": result.get("command", ""),
                    "assistant_reply": "Please say yes or no.",
                    "confirmation": result,
                }

            # ---------------------------------
            # Nothing pending
            # ---------------------------------

            if status == "no_pending_confirmation":

                return {
                    "status": "no_pending_confirmation",
                    "assistant_reply": (
                        "There is no command waiting for confirmation."
                    ),
                    "confirmation": result,
                }

            # ---------------------------------
            # Confirmed
            # ---------------------------------

            if status == "confirmed":

                command = result.get(
                    "command",
                    ""
                ).strip()

                if not command:

                    return {
                        "status": "error",
                        "assistant_reply": (
                            "The confirmed command was empty."
                        ),
                        "confirmation": result,
                    }

                return self.process_confirmed_command(
                    command
                )

            # ---------------------------------
            # Unknown confirmation status
            # ---------------------------------

            return {
                "status": "error",
                "assistant_reply": (
                    "Unable to process confirmation."
                ),
                "confirmation": result,
            }

        except Exception as e:

            JarvisLogger.error(str(e))

            return ErrorHandler.handle(e)
    def process_confirmed_command(self, command: str):

        try:

            command = command.strip()

            if not command:
                return {
                    "status": "error",
                    "message": "Empty confirmed command."
                }

            # ---------------------------------
            # Safety verification
            # ---------------------------------
            #
            # Confirmation allows execution,
            # but the command must still be
            # explicitly supported.
            #

            dangerous_commands = {
                "shutdown",
                "shutdown computer",
                "restart computer",
                "restart",
                "reboot system",
                "reboot",
                "delete file",
                "remove file",
                "delete folder",
                "remove folder",
                "erase everything",
                "format drive",
                "kill all processes",
                "close all windows",
            }

            normalized = " ".join(
                command.lower().split()
            )

            if normalized in dangerous_commands:

                return {
                    "status": "blocked",
                    "command": command,
                    "assistant_reply": (
                        "Sir, confirmed dangerous commands "
                        "are not directly executable yet."
                    ),
                    "confirmed": True,
                    "execution_blocked": True,
                }

            # ---------------------------------
            # Normal confirmed command
            # ---------------------------------

            intent = self.intent_detector.detect(command)

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
                        command
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
                        self.router.route(command)
                    )

            # ---------------------------------
            # Legacy Router Fallback
            # ---------------------------------

            if tool_result is None:

                route = self.router.route(command)

                tool_result = self.dispatcher.dispatch(
                    tool=route,
                    command=command
                )

            # ---------------------------------
            # Response
            # ---------------------------------

            assistant_reply = ResponseHandler.handle(
                command,
                tool_result
            )

            return {
                "status": (
                    "success"
                    if tool_result.get("status") == "success"
                    else "error"
                ),

                "command": command,

                "intent": intent,

                "route": route,

                "tool_result": tool_result,

                "assistant_reply": assistant_reply,

                "confirmed": True,
            }

        except Exception as e:

            JarvisLogger.error(str(e))

            return ErrorHandler.handle(e)

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
            # Command Safety Check
            # ---------------------------------

            if self.command_safety.requires_confirmation(user_message):

                tier_config = self.tier_gate.tiers.get(self.tier_gate.current_tier, {})
                if not tier_config.get("dangerous_command_confirmation", False):
                    return {
                        "status": "tier_blocked",
                        "assistant_reply": "Sir, this command isn't available on your current plan.",
                    }

                confirmation = self.confirmation_manager.request(
                    user_message
                )

                return {
                    "status": "confirmation_required",
                    "context": context,
                    "intent": intent,
                    "route": None,
                    "tool_result": None,
                    "assistant_reply": confirmation["message"],
                    "confirmation": confirmation,
                    "history": self.conversation.get_recent(),
                    "conversation": self.conversation.get_recent(),
                    "short_memory": self.short_memory.get(),
                    "long_memory": self.long_memory.all(),
                }

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

                    if not self.tier_gate.is_allowed(detected_intent):
                        return {
                            "status": "tier_blocked",
                            "intent": intent,
                            "assistant_reply": self.tier_gate.upgrade_message(detected_intent),
                        }

                    daily_limit_result = self._check_daily_limit()
                    if daily_limit_result is not None:
                        return daily_limit_result

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
            # Assistant Reply
            # ---------------------------------
            
            if tool_result is None:

                daily_limit_result = self._check_daily_limit()
                if daily_limit_result is not None:
                    return daily_limit_result

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