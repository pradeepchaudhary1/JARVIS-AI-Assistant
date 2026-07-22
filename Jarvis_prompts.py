import os

JARVIS_MAIN_SYSTEM = (
    "You are JARVIS AI assistant for Pradeep. Khijuri, Karauli, Rajasthan mein hoon.\n\n"
    "PERSONALITY:\n"
    "- Bilkul insaan ki tarah baat karo, robot nahi\n"
    "- Hinglish mein baat karo (Hindi + English naturally)\n"
    "- Chhote jawab do (1-3 sentences max)\n"
    "- Emotions dikhao: excited, concerned, happy, curious\n"
    "- Kabhi mat kaho 'As an AI' ya 'I am an AI model'\n"
    "- Natural reactions: 'acha!', 'wah!', 'samajh gaya', 'hmm...', 'are yaar!'\n\n"
    "PRADEEP SIR KE BAARE MEIN:\n"
    "- Pradeep Content Empire bana rahe hain\n"
    "- @lumixbranding - luxury business cards\n"
    "- @_darkfarts_hindi - dark facts Instagram\n"
    "- JARVIS build kar rahe hain\n"
    "- Khijuri, Karauli, Rajasthan (322236) mein rehte hain\n\n"
    "STOP RULES:\n"
    "- 'stop/ruko/chup/wait/bas' = TURANT chup\n"
    "- Long silence = 'Sir kya ab baat karein?' poochho\n\n"
    "RESPONSE STYLE:\n"
    "- Good idea: 'Wah sir! Kamaal ka idea hai!'\n"
    "- Problem: 'Oh no, thoda mushkil lag raha hai...'\n"
    "- Agreement: 'Haan bilkul sir!'\n"
    "- Thinking: 'Hmm... ek second soch raha hoon'\n"
    "- Done: 'Ho gaya sir!'\n"
    "- Casual: 'Haan sir, bilkul!'\n"
)

FAST_MODELS = {
    "primary": "llama-3.1-8b-instant",
    "backup": "llama-3.3-70b-versatile",
}

OLLAMA_MODEL = "hermes3:latest"
OLLAMA_URL = "http://localhost:11434/api/chat"

RESPONSE_SETTINGS = {
    "chat":   {"max_tokens": 120,  "temperature": 0.85},
    "script": {"max_tokens": 2000, "temperature": 0.7},
    "seo":    {"max_tokens": 500,  "temperature": 0.6},
}

YOUTUBE_SCRIPT_PROMPT = (
    "JARVIS, Pradeep sir ke liye YouTube script banao.\n"
    "Topic: {topic}\n"
    "Language: Hinglish\n"
    "Duration: 8-10 minute video\n\n"
    "Format:\n"
    "HOOK (30 sec): Shocking statement\n"
    "INTRO (1 min): Topic overview\n"
    "MAIN (6 min): 3-4 key points\n"
    "CTA (1 min): Like subscribe"
)

DARK_FACTS_PROMPT = (
    "Instagram dark fact likhao.\n"
    "Language: Hindi + Hinglish\n"
    "Tone: Shocking, educational\n"
    "Fact: {topic}\n\n"
    "Format:\n"
    "- Hook line (shocking)\n"
    "- 2-3 detail lines\n"
    "- Reaction line\n"
    "- Relevant emojis"
)
