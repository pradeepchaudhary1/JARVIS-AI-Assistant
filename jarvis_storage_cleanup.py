"""
JARVIS Storage Cleanup — Free up disk space
"""
import os, shutil, subprocess
from livekit.agents import function_tool

@function_tool
async def check_storage() -> str:
    """Disk storage check karo"""
    try:
        import psutil
        result = "💿 Storage Status:\n"
        for p in ['C:\\', 'D:\\']:
            try:
                u = psutil.disk_usage(p)
                pct = u.percent
                icon = "🔴" if pct > 90 else "🟡" if pct > 75 else "🟢"
                result += f"  {icon} Drive {p}: {u.used/1e9:.1f}/{u.total/1e9:.1f} GB ({pct}% used)\n"
            except Exception:
                pass
        return result
    except Exception as e:
        return f"Error: {e}"

@function_tool
async def free_up_space() -> str:
    """Temp files delete karke space free karo"""
    freed = 0
    cleaned = []

    # Windows Temp folders
    temp_dirs = [
        os.environ.get('TEMP', ''),
        os.environ.get('TMP', ''),
        r'C:\Windows\Temp',
        os.path.join(os.environ.get('LOCALAPPDATA',''), 'Temp'),
    ]

    for d in temp_dirs:
        if not d or not os.path.exists(d):
            continue
        try:
            for item in os.listdir(d):
                item_path = os.path.join(d, item)
                try:
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path)
                        os.remove(item_path)
                        freed += size
                    elif os.path.isdir(item_path):
                        size = sum(
                            os.path.getsize(os.path.join(r, f))
                            for r, _, files in os.walk(item_path)
                            for f in files
                        )
                        shutil.rmtree(item_path, ignore_errors=True)
                        freed += size
                except Exception:
                    pass
            cleaned.append(d)
        except Exception:
            pass

    # Jarvis output files cleanup (keep last 10)
    for folder in ['phase1_output', 'phase2_output']:
        fp = os.path.join(os.path.dirname(__file__), folder)
        if os.path.exists(fp):
            files = sorted(
                [os.path.join(fp, f) for f in os.listdir(fp)],
                key=os.path.getmtime
            )
            for f in files[:-10]:
                try:
                    sz = os.path.getsize(f)
                    os.remove(f)
                    freed += sz
                except Exception:
                    pass

    freed_mb = freed / 1e6
    return (
        f"🧹 Cleanup Complete!\n"
        f"  Freed: {freed_mb:.1f} MB\n"
        f"  Cleaned: {len(cleaned)} folders\n"
        f"  ✅ Temp files deleted"
    )

@function_tool
async def run_disk_cleanup() -> str:
    """Windows Disk Cleanup run karo"""
    try:
        subprocess.Popen('cleanmgr /sagerun:1', shell=True)
        return "🧹 Windows Disk Cleanup shuru ho gaya."
    except Exception as e:
        return f"Error: {e}"
