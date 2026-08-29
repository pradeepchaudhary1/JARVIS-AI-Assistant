"""
JARVIS Phase 2.2 Step 6
Production Voice Filesystem Integration Test

Flow:

Microphone
    ↓
Wake Word
    ↓
Voice Command
    ↓
Brain
    ↓
Router
    ↓
Dispatcher
    ↓
FileLauncher
"""

from __future__ import annotations

from voice.voice_pipeline import VoicePipeline
from voice.voice_controller import VoiceController
from voice.wake_word import WakeWord


def main():

    print("=" * 60)
    print("JARVIS PHASE 2.2 - STEP 6")
    print("VOICE → FILESYSTEM INTEGRATION TEST")
    print("=" * 60)

    print()
    print("Step 1:")
    print("Say: Hey Jarvis")
    print()

    controller = VoiceController()
    wake = WakeWord()

    # -----------------------------------------
    # STEP 1 — WAIT FOR WAKE WORD
    # -----------------------------------------

    while True:

        print("🎤 Waiting for wake word...")

        speech = controller.engine.recognize()

        if speech.get("status") != "success":
            continue

        text = speech.get("text", "").strip()

        if not text:
            continue

        print("Heard :", text)

        if wake.detected(text):

            print()
            print("✅ Wake Word Detected")
            break

    # -----------------------------------------
    # STEP 2 — LISTEN FOR COMMAND
    # -----------------------------------------

    print()
    print("Now say:")
    print("open my pictures")
    print()

    result = controller.listen_once()

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print(result)

    # -----------------------------------------
    # STEP 3 — VALIDATE RESULT
    # -----------------------------------------

    if result.get("status") != "success":

        print()
        print("❌ Voice command failed.")
        return

    route = result.get("route")
    tool_result = result.get("tool_result", {})

    print()
    print("Route :", route)
    print("Tool  :", tool_result)

    # -----------------------------------------
    # STEP 4 — VALIDATE FILESYSTEM
    # -----------------------------------------

    if route != "filesystem":

        print()
        print("❌ Wrong route.")
        print("Expected : filesystem")
        print("Received :", route)
        return

    if tool_result.get("status") != "success":

        print()
        print("❌ Filesystem tool failed.")
        return

    if tool_result.get("type") != "file_launcher":

        print()
        print("❌ Wrong tool type.")
        print("Expected : file_launcher")
        print("Received :", tool_result.get("type"))
        return

    # -----------------------------------------
    # SUCCESS
    # -----------------------------------------

    print()
    print("=" * 60)
    print("✅ PHASE 2.2 STEP 6 PASSED")
    print("=" * 60)

    print()
    print("Voice → Wake Word → Brain → Router")
    print("→ Dispatcher → FileLauncher")
    print()
    print("Filesystem voice integration is working.")
    print()


if __name__ == "__main__":
    main()