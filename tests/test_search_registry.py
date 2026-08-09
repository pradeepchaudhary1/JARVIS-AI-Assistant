from brain.dispatcher import Dispatcher

dispatcher = Dispatcher()

tests = [

    "youtube arijit songs",

    "google python decorators",

    "github openai whisper",

    "amazon laptop",

    "flipkart mobile",

]

for t in tests:

    print()
    print(t)

    print(

        dispatcher.dispatch(

            "launcher",

            t

        )

    )