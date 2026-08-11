from brain.intent_dispatcher import IntentDispatcher


dispatcher = IntentDispatcher()


commands = [
    "open chrome",
    "close chrome",
    "open my pictures",
    "search youtube lofi music",
]


for command in commands:

    print("=" * 50)
    print("COMMAND :", command)

    result = dispatcher.dispatch(command)

    print("RESULT  :", result)