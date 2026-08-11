import time
import speech_recognition as sr


recognizer = sr.Recognizer()

recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.5

microphone = sr.Microphone()

print("Microphone created.")
print("Stay silent for 5 seconds...")

start = time.time()

try:
    with microphone as source:
        print("Listening...")
        audio = recognizer.listen(
            source,
            timeout=5,
            phrase_time_limit=10
        )

    print(
        "LISTEN RETURNED:",
        round(time.time() - start, 2),
        "seconds"
    )

except sr.WaitTimeoutError:
    print(
        "TIMEOUT:",
        round(time.time() - start, 2),
        "seconds"
    )

except KeyboardInterrupt:
    print(
        "BLOCKED — manually interrupted after",
        round(time.time() - start, 2),
        "seconds"
    )

except Exception as e:
    print(
        "ERROR:",
        type(e).__name__,
        str(e)
    )