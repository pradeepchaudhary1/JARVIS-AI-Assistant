from tools.command_executor import CommandExecutor


executor = CommandExecutor()


def demo_browser(command):

    return {

        "status": "success",

        "tool": "browser",

        "command": command

    }


executor.register(

    "browser",

    demo_browser

)

print(

    executor.execute(

        "browser",

        "open google"

    )

)

print()

print(

    executor.registered_tools()

)