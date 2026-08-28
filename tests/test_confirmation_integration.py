from brain.orchestrator import Brain


def test_confirmation_integration():

    brain = Brain()

    # -----------------------------------------
    # Dangerous command must NOT execute
    # -----------------------------------------

    result = brain.process(
        "shutdown computer"
    )

    print("\nDANGEROUS COMMAND:")
    print(result)

    assert result["status"] == "confirmation_required"
    assert result["tool_result"] is None
    assert result["confirmation"]["status"] == "confirmation_required"

    # -----------------------------------------
    # Cancel
    # -----------------------------------------

    result = brain.process_confirmation(
        "no"
    )

    print("\nCANCEL:")
    print(result)

    assert result["status"] == "cancelled"

    # -----------------------------------------
    # New dangerous command
    # -----------------------------------------

    result = brain.process(
        "delete file"
    )

    print("\nSECOND DANGEROUS COMMAND:")
    print(result)

    assert result["status"] == "confirmation_required"
    assert result["tool_result"] is None

    # -----------------------------------------
    # Unclear response
    # -----------------------------------------

    result = brain.process_confirmation(
        "maybe"
    )

    print("\nUNCLEAR:")
    print(result)

    assert result["status"] == "confirmation_required"

    # -----------------------------------------
    # Confirm
    # -----------------------------------------

    result = brain.process_confirmation(
        "yes"
    )

    print("\nCONFIRMED:")
    print(result)

    # We DO NOT want an actual delete/shutdown
    # operation during the test.
    #
    # Therefore this test only verifies that
    # confirmation reached the execution layer.

    assert result.get("confirmed") is True

    print("\n" + "=" * 60)
    print("✅ CONFIRMATION INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_confirmation_integration()