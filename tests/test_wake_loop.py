from voice.wake_word import WakeWord

wake = WakeWord()

tests = [

    "hello",

    "jarvis",

    "chrome",

    "hey jarvis",

    "youtube",

]

for t in tests:

    if wake.detected(t):

        print(t, "-> WAKE")

    else:

        print(t, "-> sleep")