from tools.universal_launcher import UniversalLauncher

launcher = UniversalLauncher()

tests = [

    "google search python decorators",

    "youtube search arijit songs",

    "github search openai whisper",

    "open youtube",

    "open github",

    "open chrome"

]

for item in tests:

    print()

    print(item)

    print(

        launcher.launch(item)

    )