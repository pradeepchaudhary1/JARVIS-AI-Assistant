import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty("voices")

for v in voices:
    print(v.name)

# Kalpana select
for v in voices:
    if "kalpana" in v.name.lower():
        engine.setProperty("voice", v.id)
        print("Kalpana selected")
        break

engine.say("Namaste Pradeep, main Jarvis hoon")
engine.runAndWait()