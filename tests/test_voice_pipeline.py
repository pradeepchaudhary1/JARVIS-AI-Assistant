from voice.voice_pipeline import VoicePipeline


def main():

    print("\n" + "=" * 50)
    print("JARVIS FULL VOICE PIPELINE TEST")
    print("=" * 50)

    pipeline = VoicePipeline()

    print("\n🎤 Speak a command...")
    print("Example: Hey Jarvis open Chrome")

    result = pipeline.run()

    print("\nVOICE PIPELINE RESULT:")
    print(result)

    if result.get("status") != "success":

        print("\n⚠️ Voice pipeline did not execute a command.")

        if result.get("status") == "ignored":
            print("Reason: Wake word was not detected.")
            print("Say: Hey Jarvis open Chrome")

        elif result.get("status") == "wake":
            print("Wake word detected, but no command was given.")

        return

    speech_result = result.get(
        "speech_result",
        {},
    )

    if speech_result.get("status") != "success":

        print("\n❌ TTS failed")
        print(speech_result)
        return

    print("\n" + "=" * 50)
    print("✅ Voice → Wake Word → Brain → Tool → Response → TTS successful")
    print("=" * 50)


if __name__ == "__main__":
    main()