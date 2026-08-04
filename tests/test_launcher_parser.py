from tools.universal_launcher import UniversalLauncher

launcher = UniversalLauncher()

tests = [

    "please open chrome",

    "jarvis launch telegram",

    "mujhe chrome kholo",

    "jara whatsapp kholo",

    "can you open github",

    "open calculator",

    "run word",

    "launch excel"

]

for item in tests:

    print()

    print(item)

    print(

        launcher.launch(item)

    )