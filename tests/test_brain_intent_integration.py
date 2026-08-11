from brain.orchestrator import Brain


def main():

    print("=" * 60)
    print("JARVIS BRAIN → INTENT INTEGRATION TEST")
    print("=" * 60)

    brain = Brain()

    commands = [
        "open my pictures",
        "open chrome",
        "search youtube lofi music",
        "close chrome",
    ]

    for command in commands:

        print()
        print("-" * 60)
        print("COMMAND :", command)

        result = brain.process(command)

        print("INTENT  :", result.get("intent"))
        print("ROUTE   :", result.get("route"))
        print("TOOL    :", result.get("tool_result"))
        print("REPLY   :", result.get("assistant_reply"))

        if result.get("status") == "success":
            print("✅ Brain integration successful")
        else:
            print("❌ Brain integration failed")

    print()
    print("=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()