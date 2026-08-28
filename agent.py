"""
JARVIS — Entry Point
=====================
Ye file sirf JARVIS ko START karti hai. Koi bhi actual logic yahan nahi hai.

Real logic kahan hai:
  brain/   -> intent detection, routing, memory, safety (Brain class)
  voice/   -> wake word + mic listen + TTS speak (VoicePipeline class)
  memory/  -> short-term + long-term memory
  llm/     -> Groq + Ollama fallback
  tools/   -> PC control, browser, apps, search etc.

Agar kal koi naya feature add karna hai, wo iss file me NAHI aayega —
uska apna module brain/ ya tools/ me banega, aur brain/orchestrator.py
usko wire karega. Ye file hamesha chhoti rahegi.
"""

import os
import sys

from dotenv import load_dotenv

# Project root ko dynamically detect karo — koi hardcoded D:/ path nahi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

from license_manager import activate
if not activate():
    sys.exit(1)

from voice.voice_pipeline import VoicePipeline


def main():
    print("=" * 45)
    print("  JARVIS AI Assistant — Online")
    print("  Pradeep Content Empire")
    print("=" * 45)
    print("  Say 'Hey Jarvis' + command")
    print("  Say 'exit jarvis' to quit")
    print("=" * 45 + "\n")

    if not os.getenv("GROQ_API_KEY"):
        print("[JARVIS] WARNING: GROQ_API_KEY .env me nahi mili.")
        print("[JARVIS] Root folder me .env banao aur ye line daalo:")
        print("[JARVIS]   GROQ_API_KEY=your_key_here\n")

    pipeline = VoicePipeline()

    try:
        pipeline.run_loop()
    except KeyboardInterrupt:
        print("\n[JARVIS] Ok Boss, band kar raha hoon. Alvida!")


if __name__ == "__main__":
    main()
