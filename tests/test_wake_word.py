from voice.wake_word import WakeWordDetector


def test_wake_word():

    tests = [
        ("hey jarvis", "wake_only"),
        ("hello jarvis", "wake_only"),
        ("hi jarvis", "wake_only"),
        ("jarvis", "wake_only"),

        ("hey jarvis open chrome", "command"),
        ("hello jarvis open chrome", "command"),
        ("hi jarvis open chrome", "command"),
        ("jarvis open chrome", "command"),

        ("open chrome", "ignored"),
        ("hello", "ignored"),
        ("2020", "ignored"),
    ]

    for text, expected_status in tests:

        result = WakeWordDetector.detect(text)

        print("\nINPUT :", text)
        print("RESULT:", result)

        assert result["status"] == expected_status

    # ---------------------------------
    # Command extraction
    # ---------------------------------

    result = WakeWordDetector.detect(
        "hey jarvis open chrome"
    )

    assert result["wake_word"] is True
    assert result["command"] == "open chrome"

    result = WakeWordDetector.detect(
        "jarvis search youtube lofi music"
    )

    assert result["wake_word"] is True
    assert result["command"] == "search youtube lofi music"

    # ---------------------------------
    # Case preservation
    # ---------------------------------

    result = WakeWordDetector.detect(
        "Hey Jarvis open Chrome"
    )

    assert result["wake_word"] is True
    assert result["command"] == "open Chrome"

    print("\n✅ Wake-word tests passed")


if __name__ == "__main__":
    test_wake_word()