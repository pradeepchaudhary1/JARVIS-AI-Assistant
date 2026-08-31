"""JARVIS local file generation skill."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_NAME = "file_generation"
TRIGGER_PHRASES = [
    "create a file",
    "create file",
    "generate a file",
    "generate file",
    "save this as",
    "save as",
    "make a txt file",
    "make a markdown file",
    "make a md file",
    "create a json file",
    "create a csv file",
    "create a text file",
    "create markdown file",
    "write a file",
    "write file",
]
MIN_TIER = "basic"

ALLOWED_EXTENSIONS = {
    ".txt": "txt",
    ".md": "md",
    ".json": "json",
    ".csv": "csv",
}

OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "generated_files"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)


def _normalize_name(value: str) -> str:
    text = str(value or "").strip().strip('"\'')
    text = text.replace("\\", "/")
    return text.strip()


def _safe_output_root() -> Path:
    root = OUTPUT_ROOT.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _detect_format(user_message: str, context: dict | None) -> str:
    text = (user_message or "") + " " + str((context or {}).get("format", ""))
    lowered = text.lower()

    if ".json" in lowered or "json" in lowered:
        return "json"
    if ".csv" in lowered or "csv" in lowered:
        return "csv"
    if ".md" in lowered or "markdown" in lowered or "md file" in lowered:
        return "md"
    if ".txt" in lowered or "text file" in lowered or "txt" in lowered:
        return "txt"

    return "txt"


def _detect_filename(user_message: str, context: dict | None) -> str | None:
    search_space = " ".join(
        part for part in [user_message or "", str((context or {}).get("filename", ""))] if part
    )

    if not search_space:
        return None

    patterns = [
        r"(?:named|called|filename|file name|save as)\s+([^\n\r]+?)(?=\s+(?:with|and|that|for|is)\b|$)",
        r"(?<![\\/])([A-Za-z0-9_.-]+\.(?:txt|md|json|csv))(?![A-Za-z0-9_.-])",
    ]

    for pattern in patterns:
        match = re.search(pattern, search_space, re.IGNORECASE)
        if match:
            value = match.group(1).strip().strip('"\'')
            if value:
                return value

    return None


def _is_safe_filename(filename: str | None) -> bool:
    if not filename:
        return False

    candidate = _normalize_name(filename)
    if not candidate:
        return False

    if candidate.startswith("/") or candidate.startswith("\\"):
        return False

    if any(separator in candidate for separator in ("/", "\\")):
        return False

    if ":" in candidate:
        return False

    if ".." in candidate:
        return False

    path = Path(candidate)
    if ".." in path.parts:
        return False

    suffix = path.suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return False

    return True


def _resolve_output_path(filename: str) -> Path:
    safe_name = _normalize_name(filename)
    if not _is_safe_filename(safe_name):
        raise ValueError("Invalid or unsafe filename")

    root = _safe_output_root()
    return root / safe_name


def _read_content(user_message: str, context: dict | None) -> Any:
    if not context:
        context = {}

    for key in ("content", "data", "payload", "body"):
        value = context.get(key)
        if value is not None:
            return value

    text = user_message.strip()
    if not text:
        return ""

    patterns = [
        r"(?:with\s+)(?:content|data|body)\s*[:\-]?\s*(.+)$",
        r"(?:content|data|body)\s*[:\-]?\s*(.+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip().strip('"\'')
            if value and value.lower() not in {"content", "data", "body"}:
                return value

    if "with " in text.lower():
        prefix = re.search(r"with\s+", text, re.IGNORECASE)
        if prefix:
            remainder = text[prefix.end() :].strip()
            if remainder:
                return remainder

    return text


def _serialize_for_format(file_type: str, data: Any) -> str:
    if file_type == "json":
        payload = data if isinstance(data, (dict, list, str, int, float, bool, type(None))) else str(data)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    if file_type == "csv":
        rows = data
        if isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            rows = [[str(rows)]]
        if rows and isinstance(rows[0], dict):
            headers = list(rows[0].keys())
            csv_rows = [headers]
            for row in rows:
                csv_rows.append([row.get(header, "") for header in headers])
            rows = csv_rows
        output = []
        for row in rows:
            output.append([str(cell) for cell in row])
        formatted = []
        for row in output:
            formatted.append(','.join('"' + value.replace('"', '""') + '"' if ',' in value or '"' in value or '\n' in value else value for value in row))
        return "\n".join(formatted) + ("\n" if output else "")

    if file_type in {"txt", "md"}:
        return str(data) if data is not None else ""

    raise ValueError(f"Unsupported format: {file_type}")


def _write_file(file_type: str, filename: str, payload: Any) -> dict[str, Any]:
    output_path = _resolve_output_path(filename)
    root = _safe_output_root()

    if file_type == "json":
        if isinstance(payload, str):
            try:
                parsed = json.loads(payload)
            except json.JSONDecodeError:
                parsed = {"content": payload}
            text = json.dumps(parsed, ensure_ascii=False, indent=2)
        else:
            text = json.dumps(payload, ensure_ascii=False, indent=2)
        output_path.write_text(text, encoding="utf-8")

    elif file_type == "csv":
        rows = payload
        if isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            rows = [[str(rows)]]
        if rows and isinstance(rows[0], dict):
            header = list(rows[0].keys())
            all_rows = [header]
            for row in rows:
                all_rows.append([row.get(col, "") for col in header])
            rows = all_rows

        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, quoting=csv.QUOTE_MINIMAL)
            writer.writerows(rows)

    else:
        text = payload if isinstance(payload, str) else str(payload)
        output_path.write_text(text, encoding="utf-8")

    relative_path = output_path.relative_to(root)
    return {
        "status": "success",
        "type": "file_generation",
        "format": file_type,
        "filename": output_path.name,
        "path": str(output_path),
        "relative_path": str(relative_path),
        "message": f"{file_type.upper()} file created at {output_path}",
    }


def execute(user_message: str, context: dict | None) -> dict[str, Any]:
    """Create a local generated file in the safe JARVIS output directory."""
    context = context or {}

    try:
        file_type = _detect_format(user_message, context)
        requested_name = _detect_filename(user_message, context)
        if not requested_name:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            requested_name = f"jarvis_output_{timestamp}.{file_type if file_type != 'md' else 'md'}"

        explicit_filename = context.get("filename") or requested_name
        if not _is_safe_filename(explicit_filename):
            return {
                "status": "error",
                "type": "file_generation",
                "message": "Invalid filename. Use a safe name inside the generated-files directory with a supported extension.",
            }

        payload = _read_content(user_message, context)
        if payload is None or payload == "":
            payload = "Generated by JARVIS"

        result = _write_file(file_type, explicit_filename, payload)
        return result

    except Exception as exc:  # pragma: no cover - defensive guard for runtime use
        return {
            "status": "error",
            "type": "file_generation",
            "message": f"Could not generate file: {exc}",
        }
