from brain.error_handler import ErrorHandler


def demo():

    raise ValueError(
        "Testing JARVIS error system"
    )



result = ErrorHandler.safe_execute(
    demo
)


print(result)