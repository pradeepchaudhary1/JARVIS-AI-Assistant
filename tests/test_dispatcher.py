from brain.dispatcher import Dispatcher


dispatcher = Dispatcher()

result = dispatcher.dispatch(
    tool="youtube",
    command="open youtube"
)

print(result)