from brain.intent_detector import IntentDetector
from brain.intent_dispatcher import IntentDispatcher


def main():

    print("=" * 60)
    print("JARVIS VOICE → INTENT → DISPATCHER INTEGRATION TEST")
    print("=" * 60)

    # Simulated speech-recognized commands.
    # VoiceController has already been tested separately.
    commands = [
        "open my pictures",
        "open chrome",
        "search youtube lofi music",
        "close chrome",
    ]

    detector = IntentDetector()
    dispatcher = IntentDispatcher()

    for command in commands:

        print()
        print("-" * 60)
        print("VOICE TEXT :", command)

        detected = detector.detect(command)

        print("INTENT     :", detected)

        if detected.get("status") != "success":
            print("❌ Intent detection failed.")
            continue

        result = dispatcher.dispatch(command)

        print("DISPATCH   :", result)

        if result.get("status") == "success":
            print("✅ Command executed successfully.")
        else:
            print("⚠️ Command reached dispatcher but execution failed.")

    print()
    print("=" * 60)
    print("Integration test completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()