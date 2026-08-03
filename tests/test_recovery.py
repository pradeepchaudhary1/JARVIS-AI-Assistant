from brain.recovery import RecoveryManager

try:
    raise RuntimeError("Recovery Test")

except Exception as e:

    print(
        RecoveryManager.recover(e)
    )