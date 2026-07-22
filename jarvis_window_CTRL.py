import os
import subprocess
import logging
import sys
import asyncio
from fuzzywuzzy import process

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func): return func

try:
    import win32gui, win32con
except ImportError:
    win32gui = win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import pyautogui
except Exception:
    pyautogui = None

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ FIX: GitHub + baaki common apps add kiye
APP_MAPPINGS = {
    # Browsers
    "chrome":          r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome":   r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge":            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "firefox":         r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "brave":           r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",

    # Dev Tools
    "vs code":         r"C:\Users\hp\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vscode":          r"C:\Users\hp\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "code":            r"C:\Users\hp\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "github":          r"C:\Users\hp\AppData\Local\GitHubDesktop\GitHubDesktop.exe",  # ✅ GitHub Desktop
    "github desktop":  r"C:\Users\hp\AppData\Local\GitHubDesktop\GitHubDesktop.exe",
    "git":             "cmd /k git",
    "postman":         r"C:\Users\hp\AppData\Local\Postman\Postman.exe",
    "terminal":        "wt",   # Windows Terminal
    "cmd":             "cmd",
    "command prompt":  "cmd",
    "powershell":      "powershell",

    # Office & Productivity
    "notepad":         "notepad",
    "word":            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":           r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":      r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",

    # Media
    "vlc":             r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "spotify":         r"C:\Users\hp\AppData\Roaming\Spotify\Spotify.exe",
    "youtube":         "https://youtube.com",

    # Social & Communication
    "whatsapp":        r"shell:AppsFolder\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "telegram":        r"C:\Users\hp\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "discord":         r"C:\Users\hp\AppData\Local\Discord\Update.exe --processStart Discord.exe",

    # System
    "calculator":      "calc",
    "paint":           "mspaint",
    "control panel":   "control",
    "settings":        "start ms-settings:",
    "task manager":    "taskmgr",
    "file explorer":   "explorer",

    # Creative
    "canva":           "https://canva.com",
    "figma":           "https://figma.com",
    "photoshop":       r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe",

    # AI Tools (browser me kholenge)
    "chatgpt":         "https://chat.openai.com",
    "gemini":          "https://gemini.google.com",
    "claude":          "https://claude.ai",
    "ai studio":       "https://aistudio.google.com",
}


async def focus_window(title_keyword: str) -> bool:
    if not gw:
        return False
    await asyncio.sleep(1.5)
    title_keyword = title_keyword.lower().strip()
    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False


async def index_items(base_dirs):
    item_index = []
    for base_dir in base_dirs:
        try:
            for root, dirs, files in os.walk(base_dir):
                for d in dirs:
                    item_index.append({"name": d,
                                       "path": os.path.join(root, d),
                                       "type": "folder"})
                for f in files:
                    item_index.append({"name": f,
                                       "path": os.path.join(root, f),
                                       "type": "file"})
        except Exception:
            pass
    logger.info(f"✅ Indexed {len(item_index)} items.")
    return item_index


async def search_item(query, index, item_type):
    filtered = [i for i in index if i["type"] == item_type]
    choices  = [i["name"] for i in filtered]
    if not choices:
        return None
    best, score = process.extractOne(query, choices)
    if score > 70:
        for item in filtered:
            if item["name"] == best:
                return item
    return None


async def open_folder(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"Folder open error: {e}")


async def play_file(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"File open error: {e}")


async def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder create ho gaya: {path}"
    except Exception as e:
        return f"❌ Folder create error: {e}"


async def rename_item(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        return f"✅ Naam badal diya: {new_path}"
    except Exception as e:
        return f"❌ Rename error: {e}"


async def delete_item(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return f"🗑️ Deleted: {path}"
    except Exception as e:
        return f"❌ Delete error: {e}"


@function_tool
async def open(app_title: str) -> str:
    """Open any application or website"""
    app_lower   = app_title.lower().strip()
    app_command = APP_MAPPINGS.get(app_lower)

    # Fuzzy match agar exact match na mile
    if not app_command:
        keys = list(APP_MAPPINGS.keys())
        best, score = process.extractOne(app_lower, keys)
        if score > 75:
            app_command = APP_MAPPINGS[best]
            logger.info(f"Fuzzy matched '{app_lower}' → '{best}' (score: {score})")
        else:
            app_command = app_title  # Original try karega

    try:
        # URL hai toh browser me kholo
        if app_command and (str(app_command).startswith("http://") or
                            str(app_command).startswith("https://")):
            import webbrowser
            webbrowser.open(app_command)
            return f"✅ {app_title} browser mein khol diya."

        # ✅ FIX: Start menu se try karo pehle (fast)
        if pyautogui:
            try:
                async def _open_via_start():
                    await asyncio.to_thread(pyautogui.hotkey, 'win')
                    await asyncio.sleep(0.8)
                    await asyncio.to_thread(pyautogui.write, app_lower, interval=0.05)
                    await asyncio.sleep(0.8)
                    await asyncio.to_thread(pyautogui.press, 'enter')

                await asyncio.wait_for(_open_via_start(), timeout=8)
                await asyncio.sleep(1.5)
                focused = await focus_window(app_lower)
                if focused:
                    return f"✅ {app_title} khul gaya."
            except asyncio.TimeoutError:
                logger.warning(f"Start menu timeout for: {app_title}")
            except Exception as e:
                logger.warning(f"Start search failed: {e}")

        # Direct command fallback
        if app_command and os.path.exists(str(app_command)):
            await asyncio.create_subprocess_shell(f'start "" "{app_command}"')
            await asyncio.sleep(1.5)
            return f"✅ {app_title} launch kar diya."

        # Windows shell command
        await asyncio.create_subprocess_shell(f'start "" "{app_command or app_title}"')
        return f"✅ {app_title} launch karne ki koshish ki."

    except Exception as e:
        return f"❌ {app_title} nahi khul saka: {e}"


@function_tool
async def close(window_title: str) -> str:
    """Close an application window"""
    if not win32gui:
        return "❌ pywin32 install karo: pip install pywin32"

    closed = []

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_title.lower() in title.lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                closed.append(title)

    win32gui.EnumWindows(enumHandler, None)

    if closed:
        return f"✅ Band kar diya: {', '.join(closed)}"
    return f"⚠ '{window_title}' naam ki koi window nahi mili."


@function_tool
async def folder_file(command: str) -> str:
    """Open, create, rename, delete files and folders"""
    folders_to_index = ["D:/", "C:/Users/hp/Desktop",
                        "C:/Users/hp/Documents", "C:/Users/hp/Downloads"]
    index        = await index_items(folders_to_index)
    command_lower = command.lower()

    if "create folder" in command_lower:
        folder_name = command.replace("create folder", "").strip()
        return await create_folder(os.path.join("D:/", folder_name))

    if "rename" in command_lower:
        parts = command_lower.replace("rename", "").strip().split(" to ")
        if len(parts) == 2:
            item = await search_item(parts[0].strip(), index, "folder")
            if item:
                new_path = os.path.join(os.path.dirname(item["path"]),
                                        parts[1].strip())
                return await rename_item(item["path"], new_path)
        return "❌ Rename command valid nahi hai। Format: 'rename X to Y'"

    if "delete" in command_lower:
        item = (await search_item(command, index, "folder") or
                await search_item(command, index, "file"))
        if item:
            return await delete_item(item["path"])
        return "❌ Delete karne ke liye item nahi mila।"

    if "folder" in command_lower:
        item = await search_item(command, index, "folder")
        if item:
            await open_folder(item["path"])
            return f"✅ Folder khola: {item['name']}"
        return "❌ Folder nahi mila।"

    item = await search_item(command, index, "file")
    if item:
        await play_file(item["path"])
        return f"✅ File kholi: {item['name']}"

    return "⚠ Kuch match nahi hua।"
