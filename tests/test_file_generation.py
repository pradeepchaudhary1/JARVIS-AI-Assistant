import csv
import json
from pathlib import Path

from brain.skill_registry import SkillRegistry


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPO_ROOT / "generated_files"


def test_txt_generation_creates_file_and_content():
    from skills.file_generation import execute

    result = execute("Create a txt file named notes.txt with content Hello JARVIS", {})

    assert result["status"] == "success"
    assert result["filename"] == "notes.txt"

    path = Path(result["path"])
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "Hello JARVIS"


def test_markdown_generation_creates_file_and_content():
    from skills.file_generation import execute

    result = execute("Create a markdown file named meeting_notes.md with content # Daily brief\n- Hello", {})

    assert result["status"] == "success"
    assert result["filename"] == "meeting_notes.md"

    path = Path(result["path"])
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "# Daily brief\n- Hello"


def test_json_generation_creates_valid_json_and_handles_unicode():
    from skills.file_generation import execute

    payload = {
        "name": "JARVIS",
        "status": "active",
        "note": "हैलो दुनिया",
    }
    result = execute("Create a json file named sample.json", {"content": payload})

    assert result["status"] == "success"
    path = Path(result["path"])
    assert path.exists()

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded == payload


def test_csv_generation_creates_valid_csv_rows():
    from skills.file_generation import execute

    rows = [
        {"name": "Alice", "score": 10},
        {"name": "Bob", "score": 20},
    ]
    result = execute("Create a csv file named scores.csv", {"content": rows})

    assert result["status"] == "success"
    path = Path(result["path"])
    assert path.exists()

    with path.open("r", newline="", encoding="utf-8") as handle:
        loaded = list(csv.reader(handle))

    assert loaded[0] == ["name", "score"]
    assert loaded[1] == ["Alice", "10"]
    assert loaded[2] == ["Bob", "20"]


def test_path_traversal_and_unsupported_extensions_are_rejected():
    from skills.file_generation import execute

    blocked = [
        execute("Create a txt file named ../escape.txt", {}),
        execute("Create a txt file named C:/Windows/System32/drivers/etc/hosts", {}),
        execute("Create an exe file named bad.exe", {}),
    ]

    for result in blocked:
        assert result["status"] == "error"


def test_skill_registry_discovers_and_executes_file_generation_skill():
    registry = SkillRegistry()
    skill = registry.match("create a text file named notes.txt")

    assert skill is not None
    assert skill.SKILL_NAME == "file_generation"

    result = skill.execute("Create a text file named hello.txt with content Hello there", {})
    assert result["status"] == "success"
    path = Path(result["path"])
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "Hello there"
