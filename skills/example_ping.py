SKILL_NAME = "example_ping"
TRIGGER_PHRASES = ["jarvis are you there", "ping jarvis", "system check"]
MIN_TIER = "basic"


def execute(command: str, context: dict) -> dict:
    return {
        "status": "success",
        "type": "skill",
        "message": "Yes sir, all systems online.",
    }
