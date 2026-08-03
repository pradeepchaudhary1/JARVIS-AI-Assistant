from voice.listener import VoiceListener

listener = VoiceListener()

text = listener.listen()

print()

print("Recognized:")

print(text)