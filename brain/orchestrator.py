from brain.router import Router
from brain.dispatcher import Dispatcher
from brain.context import ContextManager
from brain.conversation import ConversationManager

from llm.router import LLMRouter
from brain.dispatcher import Dispatcher
from memory.short_memory import ShortMemory
from memory.long_memory import LongMemory


class Brain:

    def __init__(self):
        
        self.llm = LLMRouter()
        self.router = Router()
        self.dispatcher = Dispatcher()
        self.context = ContextManager()
        self.conversation = ConversationManager()

        self.dispatcher = Dispatcher()
        self.short_memory = ShortMemory()
        self.long_memory = LongMemory()

    def process(self, user_message: str):

        # Conversation
        self.conversation.add_user_message(user_message)

        # Short Memory
        self.short_memory.add("user", user_message)

        # Long Memory Snapshot
        long_memory = self.long_memory.all()

        # Context
        ctx = self.context.build()

        # Route
        route = self.router.route(user_message)

        # Dispatch
        result = self.dispatcher.dispatch(
            tool=route,
            command=user_message
        )
        assistant_reply = ""

        if result.get("status") == "success":

            tool = result.get("tool", "")

            assistant_reply = self.llm.ask(
                f"""
        User command:

        {user_message}

        Tool executed successfully.

        Reply in one short sentence.

        Owner:

        Pradeep Chaudhary

        Company:

        Lumix Branding
        """
            )

        else:

             assistant_reply = self.llm.ask(user_message)
                
        assistant_reply = "processed"

        self.conversation.add_assistant_message(assistant_reply)

        self.short_memory.add("assistant", assistant_reply)

        text = user_message.lower()

        if text.startswith("my name is"):
            name = user_message[10:].strip()
            self.long_memory.remember("owner", name)

        if text.startswith("my company is"):
            company = user_message[13:].strip()
            self.long_memory.remember("company", company)

        return {
            "context": ctx,
            "route": route,
            "result": result,
            "history": self.conversation.get_recent(),
            "short_memory": self.short_memory.get(),
            "long_memory": self.long_memory.all(),
        }