from brain.dispatcher import Dispatcher

dispatcher = Dispatcher()

tests = [

    "open youtube and search arijit songs",

    "open google and search python decorators",

    "open github and search openai whisper",

    "search youtube lofi music",

    "google search ai agents",

]

for item in tests:

    print()
    print(item)

    print(
        dispatcher.dispatch(
            "launcher",
            item
        )
    )