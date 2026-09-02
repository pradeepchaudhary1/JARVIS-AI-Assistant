import license_manager
from brain.orchestrator import Brain


def run(command):
    print("\n" + "=" * 50)
    print("COMMAND :", command)

    original = license_manager.read_license_data
    license_manager.read_license_data = lambda: ("user@example.com", "basic")
    try:
        brain = Brain()
        result = brain.process(command)
    finally:
        license_manager.read_license_data = original

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