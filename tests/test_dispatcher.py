from brain.dispatcher import Dispatcher

dispatcher = Dispatcher()

print("------ YouTube ------")
print(dispatcher.dispatch("youtube", "open youtube"))

print()

print("------ Browser ------")
print(dispatcher.dispatch("browser", "open google.com"))

print()

print("------ WhatsApp ------")
print(dispatcher.dispatch("whatsapp", "open whatsapp"))

print()

print("------ Filesystem ------")
print(dispatcher.dispatch("filesystem", "current directory"))