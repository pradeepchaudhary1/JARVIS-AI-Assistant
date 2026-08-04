from tools.universal_launcher import UniversalLauncher

launcher = UniversalLauncher()

tests = [

    "google chrome",

    "vs code",

    "visual studio code",

    "word",

    "excel",

    "calculator"

]

for item in tests:

    print()

    print(item)

    print(

        launcher.launch(item)

    )