import os, subprocess, time, ctypes, re
import pyautogui

# App name -> launch command
APPS = {
    "whatsapp":   "whatsapp:",
    "youtube":    "https://youtube.com",
    "instagram":  "https://instagram.com",
    "facebook":   "https://facebook.com",
    "gmail":      "https://gmail.com",
    "notion":     "https://notion.so",
    "spotify":    "spotify:",
    "chrome":     None,       # special: chrome.exe
    "browser":    None,
    "notepad":    None,
    "calculator": None,
    "calc":       None,
    "paint":      None,
    "settings":   "ms-settings:",
    "camera":     "microsoft.windows.camera:",
}

EXE_APPS = {
    "chrome":     "chrome.exe",
    "browser":    "chrome.exe",
    "notepad":    "notepad.exe",
    "calculator": "calc.exe",
    "calc":       "calc.exe",
    "paint":      "mspaint.exe",
}

# Process names used to find & close apps via taskkill.
# Browser-based apps (whatsapp, instagram, youtube, etc.) actually run
# inside chrome.exe, so "closing" them really means closing Chrome.
PROCESS_NAMES = {
    "chrome":     "chrome.exe",
    "browser":    "chrome.exe",
    "youtube":    "chrome.exe",
    "instagram":  "chrome.exe",
    "facebook":   "chrome.exe",
    "gmail":      "chrome.exe",
    "notion":     "chrome.exe",
    "whatsapp":   "chrome.exe",
    "notepad":    "notepad.exe",
    "calculator": "calc.exe",
    "calc":       "calc.exe",
    "paint":      "mspaint.exe",
    "spotify":    "Spotify.exe",
}

def close_app(name):
    name = name.strip().lower()
    proc = PROCESS_NAMES.get(name)
    if not proc:
        return None
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", proc],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "Sir, " + name + " band kar diya!"
        else:
            return "Sir, " + name + " already band tha ya mila nahi."
    except Exception as e:
        return "Error closing " + name + ": " + str(e)

def open_app(name):
    name = name.strip().lower()
    if name in EXE_APPS:
        try:
            subprocess.Popen(EXE_APPS[name])
            return "Sir, " + name + " khol diya!"
        except Exception as e:
            return "Error: " + str(e)
    if name in APPS and APPS[name]:
        try:
            os.startfile(APPS[name])
            return "Sir, " + name + " khol diya!"
        except Exception as e:
            # fallback: try as web URL via default browser
            try:
                subprocess.Popen(["cmd", "/c", "start", APPS[name]], shell=True)
                return "Sir, " + name + " khol diya!"
            except Exception as e2:
                return "Error: " + str(e2)
    return None

def lock_pc():
    ctypes.windll.user32.LockWorkStation()
    return "Sir, PC lock kar diya!"

def type_in_notepad(text, save_path=None):
    subprocess.Popen("notepad.exe")
    time.sleep(1.5)
    pyautogui.typewrite(text, interval=0.02)
    if save_path:
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "s")
        time.sleep(1)
        pyautogui.typewrite(save_path, interval=0.02)
        pyautogui.press("enter")
        time.sleep(0.5)
        pyautogui.press("enter")
    return "Sir, notepad mein type karke save kar diya!"

def control_pc(command):
    cmd = command.lower()

    # Lock PC
    if "lock" in cmd:
        return lock_pc()

    # "close X" / "band karo X" / "X band karo" / "X band kardo"
    close_words = ["close", "band karo", "band kardo", "band kar do", "exit"]
    if any(w in cmd for w in close_words):
        for app in PROCESS_NAMES.keys():
            if app in cmd:
                return close_app(app)

    # "open X" / "khol X" / "X khol do" / "X khol"
    open_words  = ["open", "khol do", "khol", "kholo", "start", "launch"]
    if any(w in cmd for w in open_words):

        # notepad with typing
        if "notepad" in cmd and any(w in cmd for w in ["likho", "type", "likh", "write"]):
            text = cmd
            for w in ["likho", "type", "likh", "write"]:
                text = text.split(w)[-1]
            return type_in_notepad(text.strip() or "Hello sir, JARVIS here!")

        # check known app names anywhere in command
        for app in APPS.keys():
            if app in cmd:
                return open_app(app)

    return None
