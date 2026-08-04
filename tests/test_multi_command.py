from tools.multi_command_parser import MultiCommandParser

parser = MultiCommandParser()

tests = [

    "open chrome and youtube",

    "open chrome then calculator",

    "telegram aur whatsapp",

    "chrome, youtube, github",

    "open vscode; open word"

]

for command in tests:

    print()

    print(command)

    print(

        parser.split(command)

    )