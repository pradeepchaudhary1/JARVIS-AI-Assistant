"""
JARVIS Brain Orchestrator

Coordinates all brain modules.

Author: Lumix Branding
"""

from brain.context import ContextManager
from brain.conversation import ConversationManager
from brain.router import Router
from brain.dispatcher import Dispatcher


class Brain:

    def __init__(self):

        self.context = ContextManager()

        self.conversation = ConversationManager()

        self.router = Router()

        self.dispatcher = Dispatcher()

    def process(self, user_message: str):

        # Save user message
        self.conversation.add_user_message(user_message)

        # Collect runtime context
        context = self.context.build()

        # Decide route
        route = self.router.route(user_message)

        # Execute tool
        result = self.dispatcher.dispatch(
            tool=route,
            command=user_message
        )

        # Save assistant response
        self.conversation.add_assistant_message("processed")

        return {
            "context": context,
            "route": route,
            "result": result,
            "history": self.conversation.get_recent()
        }