from pathlib import Path

import license_manager

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_license(email: str, tier: str, groq_key: str | None = None):
    rows = [email, tier]
    if groq_key is not None:
        rows.append(groq_key)
    (REPO_ROOT / ".jarvis_license").write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_env_fallback_is_used_when_license_missing(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    (REPO_ROOT / ".jarvis_license").unlink(missing_ok=True)
    monkeypatch.setenv("GROQ_API_KEY", "env-key")

    assert license_manager.read_groq_key() == "env-key"


def test_customer_license_key_takes_priority(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    _write_license("customer@example.com", "professional", "customer-key")
    monkeypatch.setenv("GROQ_API_KEY", "env-key")

    assert license_manager.read_groq_key() == "customer-key"


def test_missing_or_invalid_key_returns_empty_string(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    (REPO_ROOT / ".jarvis_license").unlink(missing_ok=True)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert license_manager.read_groq_key() == ""

    _write_license("customer@example.com", "professional", "")
    assert license_manager.read_groq_key() == ""


def test_router_tries_groq_then_ollama(monkeypatch):
    from llm.router import LLMRouter

    class DummyGroq:
        def ask(self, prompt):
            raise RuntimeError("groq down")

    class DummyOllama:
        def ask(self, prompt):
            return "fallback-ok"

    router = LLMRouter()
    monkeypatch.setattr(router, "providers", [("groq", DummyGroq()), ("ollama", DummyOllama())])

    assert router.ask("hello") == "fallback-ok"
