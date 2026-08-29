# JARVIS AI Assistant — Copilot Project Instructions

## Communication style
Owner communicates and thinks in Hinglish (Hindi-English mix). Always
respond in Hinglish, the same way — not pure English, not pure Hindi
script-only. Keep explanations short, direct, and step-by-step. When
something fails: say exactly what failed, why, which file, the fix, and
the test command to verify — then stop and wait for the next instruction.

## What this project is
Windows AI voice assistant ("JARVIS V3"). Python 3.12.10, Windows 11.
Repo: github.com/pradeepchaudhary1/JARVIS-AI-Assistant, branch `v2-dev`.
Local path: `D:\JARVIS-AI-Assistant`.

Goal: voice wake-word → intent detection → safe command execution → LLM
fallback → TTS reply. Eventually a sellable product (Basic/Professional/Pro
tiers, monthly/annual/lifetime licensing), later a website + Android app.

## Development rules — follow these strictly
1. Do NOT randomly rewrite working modules. Inspect the file, its imports,
   and its tests before changing anything.
2. Make the smallest safe change that fixes the actual problem.
3. Run the relevant test(s) after every change before considering it done.
4. One phase / one task at a time. Do not mix unrelated module changes in
   a single edit.
5. Do not commit until tests are green.
6. When giving/making a change, be explicit about: which file, which
   function/section, and what exactly changed.
7. Owner communicates in Hinglish and prefers direct, step-by-step,
   practical answers — no long theory dumps.

## Architecture (do not restructure without being asked)
```
voice/listener.py → voice/wake_word.py → voice/voice_pipeline.py
   → brain/orchestrator.py (Brain.process())
       → brain/context.py, brain/conversation.py
       → memory/short_memory.py, memory/long_memory.py
       → brain/intent_detector.py → brain/command_safety.py
       → brain/confirmation_manager.py (dangerous commands only)
       → brain/intent_dispatcher.py / brain/router.py + brain/dispatcher.py
           → tools/ (universal_launcher, process_manager, window_manager,
                      file_launcher, browser, command_parser, search_registry)
       → llm/router.py → llm/client_groq.py (primary) → llm/client_ollama.py (fallback)
       → brain/response_handler.py
   → voice/tts.py
```
`agent.py` is a THIN entry point only (~28 lines) — it just does license
check + `VoicePipeline().run_loop()`. All real logic lives in brain/,
voice/, memory/, llm/, tools/. Never put logic back into agent.py.

## Current status (as of 28-Aug-2026)
- Phase 2.4.4 (command safety + confirmation integration) is CLOSED. All 6
  tests in tests/ pass: test_command_safety, test_confirmation_manager,
  test_wake_word, test_brain_response_integration,
  test_brain_confirmation_integration, test_voice_pipeline.
- Root folder cleanup done — dead/duplicate files moved to `archive/`
  (not deleted). `legacy/` and `lagacy/` folders still need manual merge.
- `voice/voice_loop.py` and `voice/voice_controller.py` are an OLDER,
  UNUSED alternate implementation — the active path is
  `voice/voice_pipeline.py`. Don't "fix" the old ones; they're slated for
  removal in Phase 2.5.
- `doctor/` and `vision/` folders contain only 0-byte stub files —
  future capabilities, not built yet.
- `license_manager.py` (email + key, offline check) is built and working.
  `agent.py` checks a local `.jarvis_license` file before starting.

## Known safety behavior — do not weaken
Dangerous commands (shutdown, restart, delete, format, kill all processes,
close all windows) must NEVER execute without explicit user confirmation
("yes"). Even after "yes", `brain/orchestrator.py`'s
`process_confirmed_command()` currently hard-blocks real execution of these
specific commands (returns `status: "blocked"`) — this is intentional
until real destructive execution is deliberately wired up later. Never
remove this block as a "cleanup."

## Never touch / never expose
`.env`, `client_secret.json`, `youtube_token.pickle`, `.jarvis_license` —
all contain secrets, all confirmed `.gitignore`d. Never suggest committing
them, printing them, or including them in any output.

## Roadmap — what's next, in order
Phase 2.5 → legacy/lagacy merge + retire voice_loop.py/voice_controller.py
Phase 2.6 → tier/licensing system: `config/tiers.json` (feature list per
            tier: Basic/Professional/Pro) + `brain/tier_gate.py` (checks
            active license tier before allowing a command through Brain)
Phase 2.7 → PyInstaller .exe packaging + Razorpay payment automation
Phase 2.8 → QA pass, V1 launch (sellable CLI product)
Phase 3   → FastAPI backend exposing Brain.process() over HTTP/WebSocket
Phase 4   → Website frontend (holographic-orb UI), wired to backend
Phase 5   → Android app (WebView first, native later)
Phase 6   → Multi-user support, billing automation, V2 launch

## Unrelated folders in the same repo — ignore unless explicitly asked
`worldmonitor/`, `jarvis-content-company/`, `crewAi-Automation/`,
`crew_agent/`, `lumix_cards/`, `jarvis_faces/`, `jarvis_voices/`,
`screenshots/`, `phase1_output/`, `phase2_output/` — separate side
projects/content-business tooling, not part of JARVIS's code path.
