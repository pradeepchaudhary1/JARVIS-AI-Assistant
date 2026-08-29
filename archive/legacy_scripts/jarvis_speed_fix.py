import os, time, sys

BASE_DIR = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
ENV_PATH = os.path.join(BASE_DIR, ".env")

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except:
    pass

def test_groq_speed():
    print("\n[1] Testing Groq API speed...")
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("    ERROR: GROQ_API_KEY not found in .env")
        return
    try:
        from groq import Groq
        client = Groq(api_key=key)
        models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
        for model in models:
            start = time.time()
            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Say hi only"}],
                    max_tokens=5
                )
                elapsed = time.time() - start
                print(f"    OK  {model}: {elapsed:.2f}s")
            except Exception as e:
                print(f"    ERR {model}: {e}")
    except Exception as e:
        print(f"    Groq import error: {e}")

def test_tts():
    print("\n[2] Testing TTS...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        print(f"    Found {len(voices)} voices:")
        for i, v in enumerate(voices):
            print(f"      {i}: {v.name}")
        engine.setProperty("rate", 170)
        engine.say("Hello sir, JARVIS speed test!")
        engine.runAndWait()
        print("    TTS OK")
    except Exception as e:
        print(f"    TTS error: {e}")

def test_microphone():
    print("\n[3] Testing microphone (5 sec)...")
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.pause_threshold = 0.6
        with sr.Microphone() as mic:
            r.adjust_for_ambient_noise(mic, duration=0.5)
            print("    Speak something now!")
            try:
                audio = r.listen(mic, timeout=5, phrase_time_limit=5)
                text = r.recognize_google(audio, language="hi-IN")
                print(f"    Heard: {text}")
                print("MIC OK")
            except sr.WaitTimeoutError:
                print("    Timeout - no speech. Mic may be off.")
            except sr.UnknownValueError:
                print("    Could not understand speech.")
    except Exception as e:
        print(f"    Mic error: {e}")

def show_fixes():
    print("\n[4] Recommended settings for fast JARVIS:")
    print("    In agent.py:")
    print("      PRIMARY_MODEL = 'llama-3.1-8b-instant'")
    print("      max_tokens = 120")
    print("      stream = True")
    print("    In recognizer setup:")
    print("      recognizer.pause_threshold = 0.6")
    print("      recognizer.energy_threshold = 300")

if __name__ == "__main__":
    print("=" * 45)
    print("  JARVIS Speed Diagnostic")
    print("=" * 45)
    test_groq_speed()
    test_tts()
    test_microphone()
    show_fixes()
    print("\nDone! Check errors above and fix them.")
    input("Press Enter to exit...")
