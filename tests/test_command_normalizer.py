"""
JARVIS Command Normalizer Tests
Phase 2.3.1
"""

from tools.command_normalizer import CommandNormalizer


TEST_COMMANDS = [
    "open chrome",
    "Jarvis open chrome",
    "hey Jarvis open chrome",
    "hello Jarvis open chrome",
    "hi Jarvis open chrome",
    "please open chrome",
    "can you open chrome",
    "kindly open chrome",
]


for command in TEST_COMMANDS:

    result = CommandNormalizer.normalize(command)

    print()
    print(command)
    print("->", result)