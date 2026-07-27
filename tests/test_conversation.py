from brain.conversation import ConversationManager

conv = ConversationManager()

conv.add_user_message("Hello")
conv.add_assistant_message("Hi")

print(conv.get_recent())