from brain.orchestrator import Brain


def run(command):
    print("\n" + "=" * 50)
    print("COMMAND :", command)

    brain = Brain()
    result = brain.process(command)

    print("ROUTE   :", result.get("route"))
    print("TOOL    :", result.get("tool_result"))
    print("REPLY   :", result.get("assistant_reply"))

    if command == "search youtube lofi music":
        assert result["status"] == "tier_blocked"
        assert "upgrade" in result.get("assistant_reply", "").lower()
        print("✅ Tier-blocked web search on Basic tier is handled correctly")
        return

    assert result["status"] == "success"
    assert result.get("assistant_reply")

    print("✅ Brain response integration successful")


if __name__ == "__main__":
    run("open chrome")
    run("search youtube lofi music")
    run("close chrome")
    run("open my pictures")