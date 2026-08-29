"""
check_voices.py
Run this AFTER installing Hindi/Indian English voices from Windows Settings
to confirm they're now available to pyttsx3 (and thus to JARVIS).
"""
import pyttsx3
import sys
import os

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("=" * 60)
print("  INSTALLED TTS VOICES")
print("=" * 60)

print("Python:")
print(sys.executable)

print("\nScript Location:")
print(os.path.abspath(__file__))


engine = pyttsx3.init()

voices = engine.getProperty("voices")

print("\nTOTAL VOICES:",len(voices))

print("\nAVAILABLE VOICES")
print("-"*60)


for i,v in enumerate(voices):

    print(f"""
[{i}]
Name : {v.name}
ID   : {v.id}
""")


engine.stop()

print("="*60)