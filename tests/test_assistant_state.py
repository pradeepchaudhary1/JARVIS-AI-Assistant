from voice.assistant_state import AssistantState

state = AssistantState()

print("Initial :", state.is_sleeping())

state.wake()

print("After Wake :", state.is_sleeping())

state.sleep()

print("After Sleep :", state.is_sleeping())