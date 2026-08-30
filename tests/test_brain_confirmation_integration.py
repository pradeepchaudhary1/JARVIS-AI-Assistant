"""
JARVIS Phase 2.4.4
Brain Confirmation -> Execution Integration Test
"""

from brain.orchestrator import Brain


def main():

    print("=" * 60)
    print("JARVIS PHASE 2.4.4")
    print("CONFIRMATION -> EXECUTION INTEGRATION TEST")
    print("=" * 60)

    brain = Brain()
    brain.tier_gate.current_tier = "professional"

    # --------------------------------------------------
    # TEST 1: Dangerous command must be blocked
    # --------------------------------------------------

    print("\nTEST 1: Dangerous command")

    result = brain.process("shutdown computer")

    print("RESULT:")
    print(result)

    assert result.get("status") == "confirmation_required"
    assert result.get("confirmation", {}).get("command") == "shutdown computer"
    assert result.get("confirmed") is not True
    assert brain.confirmation_manager.has_pending()

    print("✅ Dangerous command correctly asked for confirmation (not auto-executed)")
    
    # --------------------------------------------------
    # TEST 2: Unclear response
    # --------------------------------------------------

    print("\nTEST 2: Unclear confirmation")

    result = brain.process_confirmation("maybe")

    print("RESULT:")
    print(result)

    assert result.get("status") == "confirmation_required"
    assert brain.confirmation_manager.has_pending()

    print("✅ Unclear confirmation handled")

    # --------------------------------------------------
    # TEST 3: Cancel command
    # --------------------------------------------------

    print("\nTEST 3: Cancel confirmation")

    result = brain.process_confirmation("no")

    print("RESULT:")
    print(result)

    assert result.get("status") == "cancelled"
    assert not brain.confirmation_manager.has_pending()

    print("✅ Dangerous command cancelled")

    # --------------------------------------------------
    # TEST 4: Confirm a dangerous command
    # --------------------------------------------------

    print("\nTEST 4: Confirm command")

    result = brain.process("shutdown computer")

    print("REQUEST:")
    print(result)

    assert result.get("status") == "confirmation_required"
    assert brain.confirmation_manager.has_pending()

    result = brain.process_confirmation("yes")

    print("CONFIRMED RESULT:")
    print(result)

    assert result.get("confirmed") is True
    assert result.get("command") == "shutdown computer"

    print("✅ Confirmation reached execution layer")

    # --------------------------------------------------
    # TEST 5: No pending confirmation
    # --------------------------------------------------

    print("\nTEST 5: No pending confirmation")

    result = brain.process_confirmation("yes")

    print("RESULT:")
    print(result)

    assert result.get("status") == "no_pending_confirmation"

    print("✅ Pending-state handling successful")

    print("\n" + "=" * 60)
    print("✅ PHASE 2.4.4 TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()