from voice.wake_word import WakeWord

wake = WakeWord()

tests = [

    "jarvis",
    "hello jarvis",
    "hey jarvis",
    "hi jarvis",

    "chrome",
    "youtube",

]

for t in tests:

    print(t)

    print(wake.detected(t))

    print()