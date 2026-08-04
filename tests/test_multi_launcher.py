from tools.universal_launcher import UniversalLauncher

launcher = UniversalLauncher()

tests = [

    "open chrome and youtube",

    "telegram aur whatsapp",

    "calculator then paint",

    "chrome, github, instagram"

]

for command in tests:

    print()

    print(command)

    result = launcher.launch_multiple(command)

    for item in result:

        print(item)