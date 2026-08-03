import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import math
import os
import json
import subprocess
import sys

STATUS_FILE = os.path.join(os.path.dirname(__file__), "jarvis_status.json")
LOG_FILE    = os.path.join(os.path.dirname(__file__), "jarvis_log.txt")

BG         = "#050d1a"
PANEL      = "#0a1628"
ACCENT     = "#00d4ff"
ACCENT2    = "#0066ff"
GREEN      = "#00ff88"
RED        = "#ff3366"
TEXT       = "#c8e6f0"
DIM        = "#2a4a5a"
FONT_TITLE = ("Courier New", 22, "bold")
FONT_STATUS= ("Courier New", 11, "bold")
FONT_LOG   = ("Courier New", 10)
FONT_BTN   = ("Courier New", 11, "bold")

def write_status(state: str):
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump({"status": state}, f)
    except Exception:
        pass

def read_status() -> str:
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE) as f:
                return json.load(f).get("status", "offline")
    except Exception:
        pass
    return "offline"

def append_log(msg: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass

class JarvisGUI:
    def __init__(self, root: tk.Tk):
        self.root        = root
        self.root.title("J.A.R.V.I.S — AI Assistant")
        self.root.configure(bg=BG)
        self.root.geometry("860x640")
        self.root.resizable(True, True)          # ✅ FIX: minimize/maximize enable
        self.root.minsize(700, 520)

        self._angle       = 0.0
        self._wave_offset = 0.0
        self._agent_proc  = None
        self._running     = True
        self._status      = "offline"
        self._last_log_sz = 0

        self._build_ui()
        self._tick()

    def _build_ui(self):
        root = self.root

        # Top bar
        top = tk.Frame(root, bg=BG, height=70)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="◈  J.A.R.V.I.S", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack(side="left", padx=24, pady=14)

        self._status_lbl = tk.Label(top, text="● OFFLINE",
                                    font=FONT_STATUS, bg=BG, fg=RED)
        self._status_lbl.pack(side="right", padx=24, pady=14)

        tk.Frame(root, bg=DIM, height=1).pack(fill="x")

        # Body
        body = tk.Frame(root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        # Left panel
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 14))

        self._canvas = tk.Canvas(left, width=260, height=260,
                                 bg=BG, highlightthickness=0)
        self._canvas.pack()

        btn_frame = tk.Frame(left, bg=BG)
        btn_frame.pack(pady=10, fill="x")

        self._start_btn = tk.Button(
            btn_frame, text="▶  START", font=FONT_BTN,
            bg="#003322", fg=GREEN, activebackground="#005533",
            activeforeground=GREEN, relief="flat", bd=0,
            cursor="hand2", width=11,
            command=self._start_agent
        )
        self._start_btn.pack(side="left", padx=(0, 8))

        self._stop_btn = tk.Button(
            btn_frame, text="■  STOP", font=FONT_BTN,
            bg="#220011", fg=RED, activebackground="#440022",
            activeforeground=RED, relief="flat", bd=0,
            cursor="hand2", width=11,
            command=self._stop_agent
        )
        self._stop_btn.pack(side="left")

        # Clear log button
        tk.Button(
            left, text="🗑  CLEAR LOG", font=("Courier New", 9, "bold"),
            bg=PANEL, fg=DIM, activebackground=BG,
            relief="flat", bd=0, cursor="hand2",
            command=self._clear_log
        ).pack(pady=(4, 0))

        # Right log panel
        right = tk.Frame(body, bg=PANEL)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text=" SYSTEM LOG", font=FONT_STATUS,
                 bg=PANEL, fg=ACCENT).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Frame(right, bg=DIM, height=1).pack(fill="x", padx=12)

        self._log = scrolledtext.ScrolledText(
            right, font=FONT_LOG, bg="#06111f", fg=TEXT,
            insertbackground=ACCENT, relief="flat", bd=0,
            state="disabled", wrap="word",
            selectbackground=ACCENT2
        )
        self._log.pack(fill="both", expand=True, padx=8, pady=8)

        # Waveform
        tk.Frame(root, bg=DIM, height=1).pack(fill="x")
        self._wave_canvas = tk.Canvas(root, height=52,
                                      bg=PANEL, highlightthickness=0)
        self._wave_canvas.pack(fill="x")

        tk.Label(root, text="JARVIS v2.0  |  LiveKit + Gemini Realtime",
                 font=("Courier New", 8), bg=BG, fg=DIM).pack(pady=4)

    def _draw_radar(self):
        c = self._canvas
        c.delete("all")
        cx, cy, r = 130, 130, 110

        for rad, col in [(r, "#0a2a3a"), (r-18, "#0e3348"),
                         (r-36, "#133d55"), (r-54, "#1a5070")]:
            c.create_oval(cx-rad, cy-rad, cx+rad, cy+rad, outline=col, width=1)

        for dx, dy in [(0, r), (0, -r), (r, 0), (-r, 0)]:
            c.create_line(cx, cy, cx+dx, cy+dy, fill=DIM, width=1, dash=(4, 6))

        sweep_len = r - 4
        sx = cx + sweep_len * math.cos(math.radians(self._angle))
        sy = cy + sweep_len * math.sin(math.radians(self._angle))
        c.create_line(cx, cy, sx, sy, fill=ACCENT, width=2)

        for i in range(1, 6):
            ta = self._angle - i * 10
            tx = cx + sweep_len * math.cos(math.radians(ta))
            ty = cy + sweep_len * math.sin(math.radians(ta))
            shade = ["#003d4d","#002e3a","#001f28","#001218","#000a0f"][i-1]
            c.create_line(cx, cy, tx, ty, fill=shade, width=2)

        color = (GREEN if self._status == "online" else
                 ACCENT if self._status == "listening" else
                 "#ffaa00" if self._status == "speaking" else RED)
        c.create_oval(cx-7, cy-7, cx+7, cy+7, fill=color, outline="")
        c.create_oval(cx-12, cy-12, cx+12, cy+12, outline=color, width=1)

        label = {"online": "ONLINE", "offline": "OFFLINE",
                 "listening": "LISTENING", "speaking": "SPEAKING"}.get(
                 self._status, "OFFLINE")
        c.create_text(cx, cy+r+16, text=label,
                      font=("Courier New", 9, "bold"), fill=color)

    def _draw_wave(self):
        c = self._wave_canvas
        c.update_idletasks()
        w = c.winfo_width() or 860
        h = 52
        c.delete("all")

        active = self._status in ("online", "listening", "speaking")
        amp    = 14 if active else 3

        pts = []
        for x in range(0, w+1, 3):
            y = h//2 + amp * math.sin(0.04*x + self._wave_offset)
            pts += [x, y]
        if len(pts) >= 4:
            c.create_line(pts, fill=ACCENT if active else DIM, width=2, smooth=True)

        pts2 = []
        for x in range(0, w+1, 3):
            y = h//2 - (amp*0.5) * math.sin(0.04*x + self._wave_offset + 0.8)
            pts2 += [x, y]
        if len(pts2) >= 4:
            c.create_line(pts2, fill=ACCENT2 if active else PANEL, width=1, smooth=True)

    def _tick(self):
        if not self._running:
            return

        self._angle       = (self._angle + 4) % 360
        self._wave_offset = (self._wave_offset + 0.12) % (2 * math.pi)

        s = read_status()
        if s != self._status:
            self._status = s
            self._update_status_label()

        # Auto-detect if agent process died
        if self._agent_proc and self._agent_proc.poll() is not None:
            write_status("offline")
            self._agent_proc = None

        self._draw_radar()
        self._draw_wave()
        self._poll_log()

        self.root.after(40, self._tick)

    def _update_status_label(self):
        colors = {"online": GREEN, "offline": RED,
                  "listening": ACCENT, "speaking": "#ffaa00"}
        icons  = {"online": "●", "offline": "●",
                  "listening": "◉", "speaking": "◎"}
        c = colors.get(self._status, RED)
        i = icons.get(self._status, "●")
        self._status_lbl.config(text=f"{i} {self._status.upper()}", fg=c)

    def _poll_log(self):
        if not os.path.exists(LOG_FILE):
            return
        try:
            sz = os.path.getsize(LOG_FILE)
            if sz == self._last_log_sz:
                return
            self._last_log_sz = sz
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            last = "".join(lines[-300:])
            self._log.config(state="normal")
            self._log.delete("1.0", "end")
            self._log.insert("end", last)
            self._log.see("end")
            self._log.config(state="disabled")
        except Exception:
            pass

    def _clear_log(self):
        try:
            open(LOG_FILE, "w").close()
            self._last_log_sz = 0
        except Exception:
            pass

    def _start_agent(self):
        if self._agent_proc and self._agent_proc.poll() is None:
            append_log("⚠ Jarvis already running.")
            return
        append_log("▶ Starting Jarvis agent...")
        write_status("online")
        agent_path = os.path.join(os.path.dirname(__file__), "agent.py")
        try:
            log_f = open(LOG_FILE, "a", encoding="utf-8")
            self._agent_proc = subprocess.Popen(
                [sys.executable, agent_path, "console"],
                stdout=log_f, stderr=log_f,
            )
            append_log(f"✅ Agent started (PID {self._agent_proc.pid})")
        except Exception as e:
            append_log(f"❌ Failed: {e}")
            write_status("offline")

    def _stop_agent(self):
        if self._agent_proc and self._agent_proc.poll() is None:
            self._agent_proc.terminate()
            append_log("■ Agent stopped.")
        write_status("offline")
        self._agent_proc = None

    def on_close(self):
        self._running = False
        self._stop_agent()
        self.root.destroy()


def main():
    root = tk.Tk()
    app  = JarvisGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
