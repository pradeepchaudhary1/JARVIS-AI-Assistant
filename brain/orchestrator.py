"""
JARVIS Brain Orchestrator
Production Version
"""

from brain.router import Router
from brain.dispatcher import Dispatcher
from brain.context import ContextManager
from brain.conversation import ConversationManager

from llm.router import LLMRouter

from memory.short_memory import ShortMemory
from memory.long_memory import LongMemory


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

        # -----------------------------
        # Save user message
        # -----------------------------

        self.conversation.add_user_message(user_message)
        self.short_memory.add("user", user_message)
        long_memory = self.long_memory.all()

        # -----------------------------
        # Context
        # -----------------------------

        context = self.context.build()

        # -----------------------------
        # Routing
        # -----------------------------

        route = self.router.route(user_message)

        # -----------------------------
        # Execute Tool
        # -----------------------------

        result = self.dispatcher.dispatch(
            tool=route,
            command=user_message
        )

        # -----------------------------
        # Generate Assistant Reply
        # -----------------------------

        if result.get("status") == "success":

            assistant_reply = self.llm.ask(
                f"""
User command:
{user_message}

The requested tool has already been executed successfully.

Reply naturally in ONE short sentence.

Owner:
Pradeep Chaudhary

Company:
Lumix Branding
"""
            )

        else:

            assistant_reply = self.llm.ask(user_message)

        # -----------------------------
        # Save Assistant Reply
        # -----------------------------

        self.conversation.add_assistant_message(
            assistant_reply
        )

        self.short_memory.add(
            "assistant",
            assistant_reply
        )

        # -----------------------------
        # Learn User Information
        # -----------------------------

        text = user_message.lower()

        if text.startswith("my name is"):

            name = user_message[10:].strip()

            self.long_memory.remember(
                "owner",
                name
            )

        elif text.startswith("my company is"):

            company = user_message[13:].strip()

            self.long_memory.remember(
                "company",
                company
            )

        # -----------------------------
        # Final Response
        # -----------------------------

        return {
            "status": "success",

            "context": context,

            "route": route,

            "tool_result": result,

            "assistant_reply": assistant_reply,

            "history": self.conversation.get_recent(),

            "conversation": self.conversation.get_recent(),

            "short_memory": self.short_memory.get(),

            "long_memory": self.long_memory.all(),
        }    