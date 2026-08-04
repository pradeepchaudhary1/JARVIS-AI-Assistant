from voice.voice_pipeline import VoicePipeline

pipeline = VoicePipeline()

print()

print("======= SPEAK NOW =======")

result = pipeline.run()

print()

print(result)

print()

print("Assistant Reply:")

if result.get("assistant_reply"):

    print(result["assistant_reply"])