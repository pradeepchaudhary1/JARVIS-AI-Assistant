"""
JARVIS Confirmation Manager Tests
"""

from brain.confirmation_manager import ConfirmationManager


def test_confirmation_manager():

    manager = ConfirmationManager()

    # -----------------------------------------
    # Request
    # -----------------------------------------

    result = manager.request("shutdown computer")

    print("\nREQUEST:")
    print(result)

    assert result["status"] == "confirmation_required"
    assert result["command"] == "shutdown computer"

    assert manager.has_pending() is True
    assert manager.get_pending() == "shutdown computer"

    # -----------------------------------------
    # YES
    # -----------------------------------------

    result = manager.respond("yes")

    print("\nYES:")
    print(result)

    assert result["status"] == "confirmed"
    assert result["command"] == "shutdown computer"

    assert manager.has_pending() is False

    # -----------------------------------------
    # NO
    # -----------------------------------------

    manager.request("delete file")

    result = manager.respond("no")

    print("\nNO:")
    print(result)

    assert result["status"] == "cancelled"
    assert result["command"] == "delete file"

    assert manager.has_pending() is False

    # -----------------------------------------
    # UNCLEAR
    # -----------------------------------------

    manager.request("format drive")

    result = manager.respond("maybe")

    print("\nMAYBE:")
    print(result)

    assert result["status"] == "confirmation_unclear"
    assert result["command"] == "format drive"

    assert manager.has_pending() is True

    # -----------------------------------------
    # Confirm after unclear response
    # -----------------------------------------

    result = manager.respond("haan")

    print("\nHAAN:")
    print(result)

    assert result["status"] == "confirmed"
    assert result["command"] == "format drive"

    assert manager.has_pending() is False

    print("\n" + "=" * 60)
    print("✅ CONFIRMATION MANAGER TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_confirmation_manager()