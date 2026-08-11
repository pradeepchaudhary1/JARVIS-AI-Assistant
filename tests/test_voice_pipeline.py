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

    if result.get("status") == "success":

        print("\n✅ Voice → Brain → Tool → Response → TTS successful")

    else:

        print("\n❌ Voice pipeline failed")


if __name__ == "__main__":
    main()