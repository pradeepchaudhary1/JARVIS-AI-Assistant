from brain.orchestrator import Brain


def test_better_intent_routing():

    brain = Brain()

    tests = [
        ("open chrome", "open_app", "launcher"),
        ("close chrome", "close_app", "launcher"),
        ("minimize chrome", "minimize_window", "window"),
        ("maximize chrome", "maximize_window", "window"),
        ("restore chrome", "restore_window", "window"),
        ("open my pictures", "open_folder", "filesystem"),
        ("search youtube lofi music", "web_search", "launcher"),
    ]

    for command, expected_intent, expected_route in tests:

        result = brain.process(command)

        print("\n" + "=" * 60)
        print("COMMAND :", command)
        print("INTENT  :", result.get("intent"))
        print("ROUTE   :", result.get("route"))
        print("TOOL    :", result.get("tool_result"))
        print("REPLY   :", result.get("assistant_reply"))

        assert result.get("status") == "success"

        intent = result.get("intent", {})

        assert intent.get("status") == "success"
        assert intent.get("intent") == expected_intent

        assert result.get("route") == expected_route

        tool_result = result.get("tool_result", {})

        # Known intent must reach the intended dispatcher.
        assert isinstance(tool_result, dict)

        print("✅ Intent + route integration successful")


if __name__ == "__main__":
    test_better_intent_routing()