"""
JARVIS Brain V3
"""

from __future__ import annotations

from brain.router import Router
from brain.context import ContextBuilder
from brain.dispatcher import Dispatcher
from brain.conversation import ConversationManager


class Brain:

    def __init__(self):

        self.router = Router()

        self.context = ContextBuilder()

        self.dispatcher = Dispatcher()

        self.memory = ConversationManager()

    def process(self, text: str):

        self.memory.add_user(text)

        context = self.context.build()

        route = self.router.detect(text)

        result = self.dispatcher.dispatch(route, text)

        self.memory.add_assistant("processed")

        return {

            "context": context,

            "route": route,

            "result": result,

            "history": self.memory.get_history()

        }