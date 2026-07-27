from brain.dispatcher import Dispatcher


dispatcher = Dispatcher()


def youtube_handler(command):

    return {
        "status": "executed",
        "tool": "youtube",
        "command": command
    }


dispatcher.register(
    "youtube",
    youtube_handler
)


print(
    dispatcher.dispatch(
        "youtube",
        "open youtube"
    )
)