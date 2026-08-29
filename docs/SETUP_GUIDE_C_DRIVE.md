# JARVIS Complete Setup Guide
# C:\Users\hp\Desktop\JARVIS-AI-Assistant\

## STEP 1 — Download & Place Files

Save all downloaded files in:
C:\Users\hp\Desktop\JARVIS-AI-Assistant\

## STEP 2 — Install Packages

Double-click: INSTALL_ALL.bat
Wait for it to finish.

## STEP 3 — Speed Test (Important!)

Double-click: SPEED_TEST.bat
OR run: python jarvis_speed_fix.py

This will tell you:
- Is Groq API key working?
- How fast is response? (should be under 1.5 sec)
- Is microphone working?
- Which voice is available?

## STEP 4 — Fill .env File

Open env_template.txt
Copy everything
Save as .env (without .txt)
Fill in your keys:
  GROQ_API_KEY = your key from console.groq.com
  ZAPIER_WEBHOOK_URL = from zapier.com (for Lumix posts)

## STEP 5 — Start JARVIS

Double-click: START_JARVIS.bat
Two windows will open:
  Window 1: Paperclip Bridge (port 8765)
  Window 2: JARVIS Main (listening)

## STEP 6 — Test Commands

Say "Jarvis, kya haal hai?" -> Should reply in under 2 seconds
Say "Stop" -> Should go silent immediately
Say "Haan ab bolo" -> Should resume

---

## VOICE COMMANDS

Say "Jarvis" + command:

  "Jarvis kya haal hai"           -> greeting
  "Jarvis kitne baje hain"        -> time
  "Jarvis system status batao"    -> status check
  "Jarvis Lumix card post karo"   -> Instagram + FB post
  "Jarvis video banao AI tools pe"-> YouTube pipeline
  "Stop Jarvis" or "Ruko"         -> pause immediately
  "Haan ab bolo"                  -> resume

## STOP AND WAIT COMMANDS

Stop commands (JARVIS chup ho jayega):
  stop, ruko, chup, wait, bas, ek second,
  ruk jao, chup raho, hold on, abhi nahi

Resume commands (JARVIS dobara bolega):
  haan, ha, ok jarvis, ab bolo, continue,
  ab baat karo, theek hai, chalo

If you don't reply for 30 seconds:
  JARVIS will ask: "Sir kya ab baat kar sakte hain?"

If still no reply for 5 minutes:
  JARVIS will say: "Ok sir, background mein hoon"

---

## SLOW RESPONSE FIX

If JARVIS is slow:

1. Check model in agent.py:
   PRIMARY_MODEL = "llama-3.1-8b-instant"
   (this is the fastest model)

2. Check max_tokens:
   max_tokens=120
   (lower = faster)

3. Check stream=True in get_ai_response()

4. Run SPEED_TEST.bat to diagnose

5. Common issues:
   - Bad internet -> switch network
   - Wrong GROQ_API_KEY -> check console.groq.com
   - Too many open apps -> close Chrome etc

---

## LUMIX BRANDING SETUP

1. Go to zapier.com -> Create Zap
2. Trigger: Webhooks by Zapier -> Catch Hook
3. Action: Instagram Business -> Create Post
4. Copy webhook URL -> paste in .env as ZAPIER_WEBHOOK_URL
5. Put business card PNG in: lumix_cards folder
6. Say: "Jarvis Lumix card post karo"

---

## FILES LIST

File                          Purpose
agent.py                      JARVIS main brain
Jarvis_prompts.py             Personality settings
jarvis_paperclip_bridge.py    Paperclip connector
jarvis_social_lumix.py        Instagram/FB posting
jarvis_speed_fix.py           Speed diagnostic
INSTALL_ALL.bat               Install packages
START_JARVIS.bat              Start everything
SPEED_TEST.bat                Test speed
SETUP_PAPERCLIP.bat           Import Paperclip company
env_template.txt              API keys template
.env                          Your actual keys (rename from template)
lumix_cards/                  Put business card images here

