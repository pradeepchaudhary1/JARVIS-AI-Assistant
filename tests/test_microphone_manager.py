from voice.microphone_manager import MicrophoneManager

manager = MicrophoneManager()

print()

print("Detected Microphones")

print("--------------------")

for i, mic in enumerate(manager.list_microphones()):

    print(i, mic)