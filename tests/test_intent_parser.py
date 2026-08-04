from tools.intent_parser import IntentParser

parser = IntentParser()

tests = [

    "open youtube",

    "open youtube search lofi",

    "open google search python decorators",

    "launch chrome",

    "please open github",

    "open instagram",

    "youtube search arijit songs",

    "google search ai agents"

]

for t in tests:

    print()

    print(t)

    print(

        parser.parse(t)

    )