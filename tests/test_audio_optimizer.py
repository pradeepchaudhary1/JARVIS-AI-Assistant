from voice.audio_optimizer import AudioOptimizer

import speech_recognition as sr

r = sr.Recognizer()

AudioOptimizer.optimize(r)

print()

print("Dynamic:", r.dynamic_energy_threshold)

print("Energy:", r.energy_threshold)

print("Pause:", r.pause_threshold)

print("Phrase:", r.phrase_threshold)

print("Non Speaking:", r.non_speaking_duration)