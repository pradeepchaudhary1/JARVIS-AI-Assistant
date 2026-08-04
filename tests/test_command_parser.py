from tools.command_parser import CommandParser

parser = CommandParser()

tests = [

    "open chrome",

    "launch telegram",

    "please open whatsapp",

    "Jarvis open calculator",

    "can you open instagram",

    "start vscode",

    "run paint",

    "mujhe chrome kholo",

    "jarvis launch word"

]

for item in tests:

    print()

    print(item)

    print("->", parser.parse(item))