# JARVIS — Phase 2.7: Skill Framework (Plugin Architecture)

**Portable spec — usable with GitHub Copilot, ChatGPT, Claude, or any coding
assistant. Paste this whole file as context, then give the exact task at the
bottom.**

---

## 0. Context (read first, do not skip)

Repo: `D:\JARVIS-AI-Assistant`, branch `v2-dev`, Python 3.12.10, Windows 11.

Completed and CLOSED phases (do not re-touch, do not regress):
- Phase 2.4.4 — command safety + confirmation flow (`brain/command_safety.py`,
  `brain/confirmation_manager.py`, `brain/orchestrator.py`)
- Phase 2.6a — tier-based feature gating (`brain/tier_gate.py`,
  `config/tiers.json`)
- Phase 2.6b — tier-aware licensing + daily command limits
  (`license_manager.py`, `brain/orchestrator.py::_check_daily_limit`)

Current architecture (unchanged by this phase):
```
voice → brain/orchestrator.py (Brain.process())
    → intent_detector.py → command_safety → tier_gate → intent_dispatcher/router → dispatcher → tools/
    → (if no known intent) → llm/router.py (Groq/Ollama fallback)
    → response_handler.py → tts
```

**Development rules (non-negotiable, same as every previous phase):**
1. Inspect existing files before changing anything — do not guess file content.
2. Smallest safe change only. No unrelated rewrites.
3. Run relevant tests after every change.
4. Do NOT touch `process_confirmed_command()`.
5. Do NOT modify existing `config/tiers.json` `allowed_intents` values.
6. Do NOT commit or push until a human has reviewed the exact `git diff`.
7. If a file can't be read/verified directly, say so explicitly — never
   invent or guess file contents and patch against the guess.

---

## 1. Why this phase exists

Right now, adding one new capability to JARVIS requires editing 4 separate
files (`intent_detector.py`, `dispatcher.py`, `intent_dispatcher.py`,
`config/tiers.json`). This makes it slow to keep adding new tricks/skills.

**Goal:** a plugin folder (`skills/`) where each new capability is ONE
self-contained file. JARVIS auto-discovers it at startup. No other file
needs to be touched to add a new skill (tier-gating is declared inside the
skill file itself).

---

## 2. Skill contract — what every skill file must look like

Every file in `skills/` (except `__init__.py` and files starting with `_`)
must define these 4 module-level things:

```python
SKILL_NAME = "unique_snake_case_name"       # str, required, unique across all skills
TRIGGER_PHRASES = ["some phrase", "another"] # list[str], required, lowercase
MIN_TIER = "basic"                           # str, required: basic|professional|pro|lifetime

def execute(command: str, context: dict) -> dict:
    """
    Required. Must return a dict shaped like existing tool_result dicts
    elsewhere in the codebase, e.g.:
        {"status": "success", "type": "skill", "message": "..."}
    or on failure:
        {"status": "error", "type": "skill", "message": "..."}
    Must never raise — catch its own exceptions and return an error dict.
    """
```

`context` passed to `execute()` should at minimum contain
`{"raw_command": command}` — the registry can be extended later to pass more
(short_memory, long_memory, etc.) but keep it minimal for this phase.

---

## 3. Files to CREATE

### 3a. `skills/__init__.py`
Empty file, just makes `skills/` a proper package.

### 3b. `brain/skill_registry.py`

Responsibilities:
- On init, scan the `skills/` folder for `.py` files (skip `__init__.py` and
  any file starting with `_`).
- Import each module dynamically (`importlib`).
- Validate it has all 4 required attributes (`SKILL_NAME`, `TRIGGER_PHRASES`,
  `MIN_TIER`, `execute`). If a skill file is malformed (missing an
  attribute, import error), **log a warning and skip it — do not crash
  JARVIS startup.**
- Build a lookup: for each loaded skill, store its trigger phrases pointing
  to the skill module.
- Expose a method:
  ```python
  def match(self, command: str) -> "skill module or None":
      """Case-insensitive substring match against TRIGGER_PHRASES.
      Returns the first matching skill module, or None."""
  ```
- Expose a method:
  ```python
  def is_tier_sufficient(self, skill, current_tier: str, tiers_config: dict) -> bool:
      """Compare current_tier's rank against skill.MIN_TIER's rank.
      Tier rank order (low to high): basic < professional < pro == lifetime.
      Use a simple ordered list, not the tiers.json allowed_intents (that's
      for built-in intents only, unrelated to skills)."""
  ```

Keep this file self-contained — do not import anything from `tools/`,
`brain/dispatcher.py`, etc. It only knows about skill modules.

### 3c. `skills/example_ping.py` (proof-of-concept sample skill)

A trivial skill to prove the framework works end-to-end:
```python
SKILL_NAME = "example_ping"
TRIGGER_PHRASES = ["jarvis are you there", "ping jarvis", "system check"]
MIN_TIER = "basic"

def execute(command: str, context: dict) -> dict:
    return {
        "status": "success",
        "type": "skill",
        "message": "Yes sir, all systems online.",
    }
```

### 3d. `tests/test_skill_registry.py`

Cover, using a temporary skills directory (NOT the real `skills/` folder —
use `tmp_path` + `monkeypatch`, same pattern as Phase 2.6b's license tests):
- A well-formed skill file loads correctly and `match()` finds it by trigger
  phrase.
- A skill file missing a required attribute (e.g. no `MIN_TIER`) is skipped
  with a warning, does NOT crash the registry.
- `is_tier_sufficient()` correctly ranks basic < professional < pro/lifetime.
- No match returns `None` for an unrelated command.
- Also add ONE integration test using the REAL `skills/example_ping.py` via
  `brain.orchestrator.Brain` — confirm `brain.process("jarvis are you there")`
  returns `status: success` with the ping message. (Real skills/ folder is
  fine to use here since example_ping.py is a permanent, harmless skill.)

---

## 4. Files to MODIFY (minimal, surgical)

### 4a. `brain/orchestrator.py`

**`Brain.__init__`** — add one line (alongside existing `self.xxx = ...`
initializations):
```python
from brain.skill_registry import SkillRegistry
...
self.skill_registry = SkillRegistry()
```

**`Brain.process()`** — the skill check goes in EXACTLY ONE place: after the
existing `integrated_intents` block has been tried and found no match
(i.e., where `tool_result is None`, same place `_check_daily_limit()` was
added in Phase 2.6b), but BEFORE falling through to `self.llm.ask()`.

Find this existing block (from Phase 2.6b):
```python
            if tool_result is None:

                daily_limit_result = self._check_daily_limit()
                if daily_limit_result is not None:
                    return daily_limit_result

                assistant_reply = self.llm.ask(user_message)
```

Insert a skill-match attempt between the daily-limit check and the LLM call:
```python
            if tool_result is None:

                daily_limit_result = self._check_daily_limit()
                if daily_limit_result is not None:
                    return daily_limit_result

                matched_skill = self.skill_registry.match(user_message)

                if matched_skill is not None:
                    if not self.skill_registry.is_tier_sufficient(
                        matched_skill, self.tier_gate.current_tier, self.tier_gate.tiers
                    ):
                        return {
                            "status": "tier_blocked",
                            "assistant_reply": (
                                f"Sir, this feature requires the "
                                f"{matched_skill.MIN_TIER.title()} plan or higher."
                            ),
                        }

                    tool_result = matched_skill.execute(
                        user_message, {"raw_command": user_message}
                    )
                    assistant_reply = tool_result.get(
                        "message", "Done."
                    )

                else:
                    assistant_reply = self.llm.ask(user_message)
                    tool_result = {
                        "status": "success",
                        "type": "llm",
                        "message": "Handled by LLM fallback",
                    }
```

**IMPORTANT:** the existing lines right after this (that build `tool_result`
for the plain-LLM case) must be removed/merged so `tool_result` isn't set
twice — read the actual current code around this block carefully before
patching, don't duplicate logic.

Do NOT touch anything else in `orchestrator.py`. Do NOT touch
`process_confirmed_command()`.

---

## 5. Regression suite — run ALL of these after implementation, before any commit

```powershell
python -m pytest tests/test_skill_registry.py -q
python -m pytest tests/test_tier_gate.py tests/test_tier_gate_phase_2_6b.py -q
python -m tests.test_command_safety
python -m tests.test_confirmation_manager
python -m tests.test_wake_word
python -m tests.test_brain_confirmation_integration
python -m tests.test_brain_response_integration
python agent.py    # crash-free startup check only, Ctrl+C after confirming it's alive
```

All must pass / stay green. If anything regresses, report the exact failure
— do not silently patch around it.

---

## 6. Before commit — mandatory diff review

Do NOT commit automatically. Stop after tests pass and produce:
```powershell
git status --short
git diff -- brain/orchestrator.py brain/skill_registry.py
```
A human must review this exact diff before `git add` / `git commit` / `git push`.

Suggested commit message once approved:
```
Implement Phase 2.7: skill plugin framework (skills/ auto-discovery, tier-gated)
```

---

## 7. Explicitly OUT OF SCOPE for this phase (do not build now)

- No real "invoice PDF + WhatsApp reminder" skill yet — that comes AFTER
  this framework is proven with the trivial `example_ping` skill.
- No hot-reloading of skills while JARVIS is running (discovery happens once
  at `Brain.__init__`, that's enough for now).
- No skill marketplace / remote skill download — purely local `skills/`
  folder for now.
- No changes to `config/tiers.json` structure — `MIN_TIER` lives inside each
  skill file, not in the tiers config.

---

## 8. Task to give your coding assistant (Copilot / ChatGPT / etc.)

> "Implement Phase 2.7 exactly as specified in this document — sections 3
> and 4 only. Create the 4 new files (§3a-3d) and make the one surgical
> edit to `brain/orchestrator.py` (§4a). Do not touch anything outside this
> scope. After implementing, run the full regression suite in §5 and report
> exact results. Do NOT commit or push — stop after tests pass and give me
> the exact `git diff` output for `brain/orchestrator.py` and
> `brain/skill_registry.py` per §6, so I can review before approving the
> commit."
