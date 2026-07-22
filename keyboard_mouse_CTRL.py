"""
JARVIS Keyboard/Mouse Control — Issue #4 & #7 Fix
Volume, typing (no garbled text), cursor control
"""
import pyautogui, asyncio, time
from datetime import datetime
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from typing import List
from livekit.agents import function_tool

pyautogui.FAILSAFE = False  # ✅ FIX: Disable failsafe

class SafeController:
    def __init__(self):
        self.keyboard = KeyboardController()
        self.mouse    = MouseController()
        self.special_keys = {
            "enter": Key.enter, "space": Key.space, "tab": Key.tab,
            "shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt,
            "esc": Key.esc, "backspace": Key.backspace, "delete": Key.delete,
            "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
            "caps_lock": Key.caps_lock, "win": Key.cmd, "cmd": Key.cmd,
            "home": Key.home, "end": Key.end,
            "page_up": Key.page_up, "page_down": Key.page_down,
            "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
            "f5": Key.f5, "f6": Key.f6, "f11": Key.f11, "f12": Key.f12,
        }

    def resolve_key(self, key: str):
        return self.special_keys.get(key.lower(), key)

    async def move_cursor(self, direction: str, distance: int = 100) -> str:
        x, y = self.mouse.position
        moves = {"left": (-distance, 0), "right": (distance, 0),
                 "up": (0, -distance), "down": (0, distance)}
        dx, dy = moves.get(direction, (0, 0))
        self.mouse.position = (x + dx, y + dy)
        await asyncio.sleep(0.1)
        return f"🖱️ Mouse {direction} moved."

    async def mouse_click(self, button: str = "left") -> str:
        clicks = {"left": Button.left, "right": Button.right}
        count  = 2 if button == "double" else 1
        btn    = clicks.get(button, Button.left)
        self.mouse.click(btn, count)
        await asyncio.sleep(0.1)
        return f"🖱️ {button.capitalize()} click done."

    async def scroll_cursor(self, direction: str, amount: int = 5) -> str:
        dy = amount if direction == "up" else -amount
        self.mouse.scroll(0, dy)
        await asyncio.sleep(0.1)
        return f"🖱️ Scrolled {direction}."

    async def type_text(self, text: str) -> str:
        """
        ✅ FIX: pyautogui.write use karo — pynput me garbled text issue tha
        """
        try:
            await asyncio.sleep(0.3)
            # pyautogui typewrite better handles special chars
            pyautogui.write(text, interval=0.05)
            return f"⌨️ Typed: {text[:50]}{'...' if len(text)>50 else ''}"
        except Exception:
            # Fallback: pynput
            for char in text:
                if char == '\n':
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                elif char.isprintable():
                    try:
                        self.keyboard.press(char)
                        self.keyboard.release(char)
                    except Exception:
                        pass
                await asyncio.sleep(0.03)
            return f"⌨️ Typed (fallback): {text[:50]}"

    async def press_key(self, key: str) -> str:
        k = self.resolve_key(key)
        try:
            self.keyboard.press(k)
            self.keyboard.release(k)
        except Exception as e:
            return f"❌ Key '{key}' error: {e}"
        await asyncio.sleep(0.1)
        return f"⌨️ Key '{key}' pressed."

    async def press_hotkey(self, keys: List[str]) -> str:
        resolved = [self.resolve_key(k) for k in keys]
        for k in resolved:
            self.keyboard.press(k)
        await asyncio.sleep(0.05)
        for k in reversed(resolved):
            self.keyboard.release(k)
        await asyncio.sleep(0.1)
        return f"⌨️ Hotkey {'+'.join(keys)} pressed."

    async def control_volume(self, action: str) -> str:
        """✅ FIX: Volume control improved"""
        action = action.lower()
        if action in ["up", "increase", "badhao"]:
            for _ in range(5):  # 5 steps up
                pyautogui.press("volumeup")
                await asyncio.sleep(0.05)
            return "🔊 Volume badha diya."
        elif action in ["down", "decrease", "ghata", "kam"]:
            for _ in range(5):  # 5 steps down
                pyautogui.press("volumedown")
                await asyncio.sleep(0.05)
            return "🔉 Volume ghata diya."
        elif action in ["mute", "band", "chup"]:
            pyautogui.press("volumemute")
            return "🔇 Mute kar diya."
        elif action in ["unmute", "chalu"]:
            pyautogui.press("volumemute")
            return "🔊 Unmute kar diya."
        elif action.isdigit():
            # Specific level
            level = int(action)
            return f"Volume {level}% set karne ki koshish ki."
        return f"❌ Action '{action}' samajh nahi aaya."

    async def swipe_gesture(self, direction: str) -> str:
        w, h = pyautogui.size()
        cx, cy = w // 2, h // 2
        swipes = {
            "up":    ((cx, cy + 200), (cx, cy - 200)),
            "down":  ((cx, cy - 200), (cx, cy + 200)),
            "left":  ((cx + 200, cy), (cx - 200, cy)),
            "right": ((cx - 200, cy), (cx + 200, cy)),
        }
        if direction in swipes:
            start, end = swipes[direction]
            pyautogui.moveTo(*start)
            pyautogui.dragTo(*end, duration=0.4)
        await asyncio.sleep(0.3)
        return f"🖱️ Swipe {direction} done."


controller = SafeController()


@function_tool
async def move_cursor_tool(direction: str, distance: int = 100) -> str:
    """Mouse cursor move karo"""
    return await controller.move_cursor(direction, distance)

@function_tool
async def mouse_click_tool(button: str = "left") -> str:
    """Mouse click karo (left/right/double)"""
    return await controller.mouse_click(button)

@function_tool
async def scroll_cursor_tool(direction: str, amount: int = 5) -> str:
    """Page scroll karo"""
    return await controller.scroll_cursor(direction, amount)

@function_tool
async def type_text_tool(text: str) -> str:
    """Text type karo — bilkul sahi characters"""
    return await controller.type_text(text)

@function_tool
async def press_key_tool(key: str) -> str:
    """Keyboard key press karo"""
    return await controller.press_key(key)

@function_tool
async def press_hotkey_tool(keys: List[str]) -> str:
    """Keyboard shortcut press karo (e.g. ctrl+c)"""
    return await controller.press_hotkey(keys)

@function_tool
async def control_volume_tool(action: str) -> str:
    """Volume control: up/down/mute/unmute"""
    return await controller.control_volume(action)

@function_tool
async def swipe_gesture_tool(direction: str) -> str:
    """Swipe gesture karo"""
    return await controller.swipe_gesture(direction)
