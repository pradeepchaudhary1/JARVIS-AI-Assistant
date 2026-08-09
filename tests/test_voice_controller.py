from voice.voice_controller import VoiceController

controller = VoiceController()

print()

print("Speak after the microphone starts...")

print()

result = controller.listen_once()

print()

print(result)