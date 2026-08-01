class Brain:

    def __init__(self):

        self.router = Router()

        self.context = ContextBuilder()

        self.dispatcher = Dispatcher()

        self.conversation = ConversationManager()

        self.memory = ShortMemory(max_messages=20)