from tools.universal_launcher import UniversalLauncher

launcher = UniversalLauncher()

tests = [

    "calculator",

    "paint",

    "explorer",

    "cmd",

    "powershell",

    "chrome",

    "vs code",

    "telegram",

    "chatgpt",

    "lumix branding"

]

for item in tests:

    print()

    print(item)

    print(

        launcher.launch(item)

    )