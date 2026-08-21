from brain.command_safety import CommandSafety


def test_command_safety():

    dangerous_commands = [
        "shutdown",
        "shutdown computer",
        "restart computer",
        "reboot system",
        "delete file",
        "remove folder",
        "erase everything",
        "format drive",
        "kill all processes",
        "close all windows",
    ]

    safe_commands = [
        "open chrome",
        "open my pictures",
        "search youtube lofi music",
        "minimize chrome",
        "maximize chrome",
        "restore chrome",
    ]

    # -----------------------------------------
    # Dangerous commands
    # -----------------------------------------

    for command in dangerous_commands:

        result = CommandSafety.requires_confirmation(command)

        print("\nDANGEROUS:", command)
        print("RESULT   :", result)

        assert result is True

    # -----------------------------------------
    # Safe commands
    # -----------------------------------------

    for command in safe_commands:

        result = CommandSafety.requires_confirmation(command)

        print("\nSAFE:", command)
        print("RESULT:", result)

        assert result is False

    # -----------------------------------------
    # Confirmation
    # -----------------------------------------

    confirmations = [
        "yes",
        "yes jarvis",
        "confirm",
        "confirmed",
        "do it",
        "haan",
        "kar do",
    ]

    for text in confirmations:

        assert CommandSafety.is_confirmation(text) is True

    # -----------------------------------------
    # Cancellation
    # -----------------------------------------

    cancellations = [
        "no",
        "cancel",
        "stop",
        "nahi",
        "mat karo",
    ]

    for text in cancellations:

        assert CommandSafety.is_cancellation(text) is True

    # -----------------------------------------
    # Confirmation response
    # -----------------------------------------

    result = CommandSafety.confirmation_required_response(
        "shutdown computer"
    )

    assert result["status"] == "confirmation_required"
    assert result["command"] == "shutdown computer"

    print("\n" + "=" * 60)
    print("✅ COMMAND SAFETY TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_command_safety()