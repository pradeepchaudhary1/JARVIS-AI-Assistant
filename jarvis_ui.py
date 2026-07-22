import tkinter as tk
import threading

class JarvisUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S - AI Assistant")
        self.root.geometry("420x550")
        self.root.configure(bg="#0a0e14")

        title = tk.Label(self.root, text="J.A.R.V.I.S", font=("Consolas", 26, "bold"),
                          fg="#00d4ff", bg="#0a0e14")
        title.pack(pady=15)

        self.status_label = tk.Label(self.root, text="● ONLINE", font=("Consolas", 12, "bold"),
                                       fg="#00ff80", bg="#0a0e14")
        self.status_label.pack()

        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="#0a0e14", highlightthickness=0)
        self.canvas.pack(pady=15)
        self._draw_radar()

        log_frame = tk.Frame(self.root, bg="#0d1320", highlightbackground="#00d4ff", highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)

        tk.Label(log_frame, text="SYSTEM LOG", font=("Consolas", 10, "bold"),
                 fg="#00d4ff", bg="#0d1320").pack(anchor="w", padx=8, pady=4)

        self.log_box = tk.Text(log_frame, bg="#0d1320", fg="#00ff80", font=("Consolas", 9),
                                wrap="word", borderwidth=0)
        self.log_box.pack(fill="both", expand=True, padx=8, pady=5)

    def _draw_radar(self):
        c = self.canvas
        c.create_oval(20, 20, 280, 280, outline="#00d4ff", width=2)
        c.create_oval(70, 70, 230, 230, outline="#00d4ff", width=1)
        c.create_oval(120, 120, 180, 180, outline="#00d4ff", width=1)
        c.create_line(150, 20, 150, 280, fill="#00d4ff", dash=(2, 4))
        c.create_line(20, 150, 280, 150, fill="#00d4ff", dash=(2, 4))
        c.create_oval(140, 140, 160, 160, fill="#ff2050", outline="")

    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def set_status(self, online=True):
        if online:
            self.status_label.config(text="● ONLINE", fg="#00ff80")
        else:
            self.status_label.config(text="● OFFLINE", fg="#ff2050")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ui = JarvisUI()
    ui.log("[JARVIS] Good morning sir! JARVIS ready hai.")
    ui.run()
