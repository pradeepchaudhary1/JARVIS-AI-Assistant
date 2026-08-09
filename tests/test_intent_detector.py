"""
JARVIS Intent Detector Tests
Phase 2.3.2
"""

from brain.intent_detector import IntentDetector


TEST_COMMANDS = [

    "open chrome",

    "launch telegram",

    "close whatsapp",

    "minimize chrome",

    "maximize chrome",

    "restore chrome",

    "open my pictures",

    "open my videos",

    "open my desktop",

    "search youtube lofi music",

    "search google python decorators",

    "what is the time",

    "hello jarvis",

]


for command in TEST_COMMANDS:

    result = IntentDetector.detect(command)

    print()
    print(command)
    print("->", result)