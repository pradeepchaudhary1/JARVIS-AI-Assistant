SKILL_NAME = "follow_up_action"
from pathlib import Path

try:
    SKILL_NAME = "follow_up_action"
    from docx2pdf import convert
except ImportError:
    convert = None


TRIGGER_PHRASES = [
    "isko pdf bana do",
    "ise pdf banao",
    "isko pdf mein save kar do",
    "convert it to pdf",
    "isko docx mein banao",
    "ise word mein save karo",
]

MIN_TIER = "basic"


def _get_last_artifact(context):
    session_context = context.get("session_context") if context else None

    if not session_context:
        return None, {
            "status": "error",
            "type": "follow_up_action",
            "message": "No session context available",
        }

    artifact = session_context.get_last_artifact()

    if not artifact:
        return None, {
            "status": "error",
            "type": "follow_up_action",
            "message": "No recent artifact available",
        }

    source_path = Path(artifact["path"])

    if not source_path.exists():
        return None, {
            "status": "error",
            "type": "follow_up_action",
            "message": "Recent artifact file no longer exists",
        }

    return artifact, None


def execute(user_message, context=None):
    context = context or {}

    artifact, error = _get_last_artifact(context)

    if error:
        return error

    source_path = Path(artifact["path"])
    text = (user_message or "").strip().lower()

    if "pdf" in text:
        if source_path.suffix.lower() != ".docx":
            return {
                "status": "error",
                "type": "follow_up_action",
                "message": "PDF conversion currently requires a DOCX source file",
            }

        if convert is None:
            return {
                "status": "error",
                "type": "follow_up_action",
                "message": "docx2pdf is not installed",
            }

        target_path = source_path.with_suffix(".pdf")

        try:
            convert(str(source_path), str(target_path))
        except Exception as exc:
            if not target_path.exists() or target_path.stat().st_size == 0:
                return {
                    "status": "error",
                    "type": "follow_up_action",
                    "message": f"PDF conversion failed: {exc}",
                }

        session_context = context.get("session_context")
        if session_context:
            session_context.set_last_artifact(str(target_path), "pdf")

        return {
            "status": "success",
            "type": "follow_up_action",
            "format": "pdf",
            "source_path": str(source_path),
            "path": str(target_path),
            "message": f"PDF created at {target_path}",
        }

    if "docx" in text or "word" in text:
        return {
            "status": "error",
            "type": "follow_up_action",
            "message": "DOCX conversion is not implemented yet",
        }

    return {
        "status": "error",
        "type": "follow_up_action",
        "message": "Unknown follow-up format",
    }