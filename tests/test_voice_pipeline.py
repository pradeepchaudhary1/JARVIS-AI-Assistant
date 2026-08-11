from voice.voice_pipeline import VoicePipeline


def main():

    print("\n" + "=" * 50)
    print("JARVIS FULL VOICE PIPELINE TEST")
    print("=" * 50)

    pipeline = VoicePipeline()

    print("\n🎤 Speak a command...")
    print("Example: open chrome")

    result = pipeline.run()

    print("\nVOICE PIPELINE RESULT:")
    print(result)

    if result.get("status") != "success":
        print("\n❌ Voice pipeline failed")
        return

    speech_result = result.get("speech_result", {})

    if speech_result.get("status") != "success":
        print("\n❌ TTS failed")
        print(speech_result)
        return

    print("\n" + "=" * 50)
    print("✅ Voice → Brain → Tool → Response → TTS successful")
    print("=" * 50)


if __name__ == "__main__":
    main()