from brain.dispatcher import Dispatcher

dispatcher = Dispatcher()

tests = [

    "close chrome",

    "close whatsapp",

    "close telegram",

    "close vscode",

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