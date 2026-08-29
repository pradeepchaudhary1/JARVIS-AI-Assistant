"""
JARVIS Project Diagnostic Tool
Run this to confirm D: drive setup is healthy before adding new features.
"""
import os, sys, json, importlib.util

BASE_DIR = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")

REQUIRED_FILES = [
    "agent.py",
    "Jarvis_prompts.py",
    "jarvis_paperclip_bridge.py",
    "jarvis_pc_control.py",
    "jarvis_social_lumix.py",
    "jarvis_memory.py",
    "jarvis_worldmonitor.py",
    "jarvis_app.html",
    ".env",
]

OPTIONAL_FILES = [
    "jarvis_memory.json",
    "lumix_cards",
]

def check_files():
    print("\n[1] Checking required files in", BASE_DIR)
    missing = []
    for f in REQUIRED_FILES:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            size = os.path.getsize(path) if os.path.isfile(path) else 0
            print(f"    OK   {f}  ({size} bytes)")
        else:
            print(f"    MISSING  {f}")
            missing.append(f)
    return missing

def check_optional():
    print("\n[2] Checking optional files/folders")
    for f in OPTIONAL_FILES:
        path = os.path.join(BASE_DIR, f)
        status = "OK" if os.path.exists(path) else "not yet created (fine)"
        print(f"    {f}: {status}")

def check_env():
    print("\n[3] Checking .env keys")
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        print("    .env file missing!")
        return
    with open(env_path) as f:
        content = f.read()
    keys = ["GROQ_API_KEY", "ZAPIER_WEBHOOK_URL", "SERPER_API_KEY"]
    for k in keys:
        if k in content and (k + "=your_") not in content.replace(" ", ""):
            print(f"    {k}: looks set")
        elif k in content:
            print(f"    {k}: present but still placeholder value")
        else:
            print(f"    {k}: NOT FOUND in .env")

def check_python_syntax():
    print("\n[4] Checking Python file syntax")
    import ast
    for f in REQUIRED_FILES:
        if not f.endswith(".py"):
            continue
        path = os.path.join(BASE_DIR, f)
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            ast.parse(src)
            print(f"    OK   {f} syntax valid")
        except SyntaxError as e:
            print(f"    ERROR  {f} -> {e}")

def check_base_dir_consistency():
    print("\n[5] Checking BASE_DIR consistency across files")
    for f in REQUIRED_FILES:
        if not f.endswith(".py"):
            continue
        path = os.path.join(BASE_DIR, f)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        # Only flag if a HARDCODED C: drive literal is actually used for BASE_DIR
        # (ignore comments/fallback strings that don't affect runtime path)
        has_dynamic = 'os.environ.get("JARVIS_HOME"' in content or "os.environ.get('JARVIS_HOME'" in content
        has_old_hardcode = 'os.environ.get("USERPROFILE"' in content and "Desktop" in content
        if has_old_hardcode:
            print(f"    WARNING  {f} still has OLD hardcoded USERPROFILE/C: path pattern!")
        elif has_dynamic:
            print(f"    OK   {f} uses dynamic JARVIS_HOME/BASE_DIR")
        elif "BASE_DIR" in content:
            print(f"    OK   {f} references BASE_DIR (check manually if needed)")

def main():
    print("=" * 50)
    print("  JARVIS DIAGNOSTIC")
    print("  Checking:", BASE_DIR)
    print("=" * 50)

    if not os.path.exists(BASE_DIR):
        print("\nFATAL: BASE_DIR does not exist:", BASE_DIR)
        print("Migration to D: drive is not complete yet.")
        input("\nPress Enter to exit...")
        return

    missing = check_files()
    check_optional()
    check_env()
    check_python_syntax()
    check_base_dir_consistency()

    print("\n" + "=" * 50)
    if missing:
        print("  RESULT: ISSUES FOUND -", len(missing), "file(s) missing")
        for m in missing:
            print("   -", m)
    else:
        print("  RESULT: ALL GOOD! Safe to add new features.")
    print("=" * 50)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
