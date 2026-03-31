"""
MC Helper - Remote Control Panel
Minecraft hile kontrol paneli
"""

import tkinter as tk
from tkinter import font as tkfont
import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 25567

# Module definitions
MODULES = [
    {"id": "fullbright", "name": "Fullbright", "icon": "SUN", "desc": "Karanlikta gorme", "key": "G"},
    {"id": "fly",        "name": "Fly",        "icon": "WING", "desc": "Ucma modu", "key": "H"},
    {"id": "speed",      "name": "Speed",      "icon": "BOLT", "desc": "Hizli hareket (1.8x)", "key": "J"},
    {"id": "autosprint", "name": "Sprint",     "icon": "RUN", "desc": "Otomatik kosma", "key": "K"},
    {"id": "nofall",     "name": "No Fall",    "icon": "SHLD", "desc": "Dusme hasari yok", "key": "N"},
    {"id": "xray",       "name": "X-Ray",      "icon": "EYE", "desc": "Cevherleri gor", "key": "X"},
]

# Colors
BG_DARK = "#0d1117"
BG_CARD = "#161b22"
BG_CARD_HOVER = "#1c2333"
ACCENT_GREEN = "#3fb950"
ACCENT_RED = "#f85149"
ACCENT_BLUE = "#58a6ff"
ACCENT_PURPLE = "#bc8cff"
TEXT_PRIMARY = "#f0f6fc"
TEXT_SECONDARY = "#8b949e"
BORDER_COLOR = "#30363d"
BORDER_ACTIVE = "#3fb950"


class MCHelperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MC Helper Control Panel")
        self.root.geometry("420x620")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.sock = None
        self.connected = False
        self.module_states = {m["id"]: False for m in MODULES}
        self.module_buttons = {}
        self.module_indicators = {}

        self.setup_fonts()
        self.build_ui()
        self.try_connect()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def setup_fonts(self):
        self.font_title = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.font_subtitle = tkfont.Font(family="Segoe UI", size=10)
        self.font_module = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_desc = tkfont.Font(family="Segoe UI", size=9)
        self.font_key = tkfont.Font(family="Consolas", size=9, weight="bold")
        self.font_status = tkfont.Font(family="Segoe UI", size=9)
        self.font_icon = tkfont.Font(family="Consolas", size=11, weight="bold")

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG_DARK, pady=15)
        header.pack(fill="x")

        title_frame = tk.Frame(header, bg=BG_DARK)
        title_frame.pack()

        tk.Label(title_frame, text="MC", font=self.font_title,
                 fg=ACCENT_GREEN, bg=BG_DARK).pack(side="left")
        tk.Label(title_frame, text=" Helper", font=self.font_title,
                 fg=TEXT_PRIMARY, bg=BG_DARK).pack(side="left")

        tk.Label(header, text="Minecraft Kontrol Paneli",
                 font=self.font_subtitle, fg=TEXT_SECONDARY, bg=BG_DARK).pack()

        # Connection status bar
        self.status_frame = tk.Frame(self.root, bg=BG_CARD, pady=6, padx=15)
        self.status_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.status_dot = tk.Canvas(self.status_frame, width=10, height=10,
                                     bg=BG_CARD, highlightthickness=0)
        self.status_dot.pack(side="left", padx=(0, 8))
        self.status_dot.create_oval(1, 1, 9, 9, fill=ACCENT_RED, outline="")

        self.status_label = tk.Label(self.status_frame, text="Baglanti bekleniyor...",
                                      font=self.font_status, fg=TEXT_SECONDARY, bg=BG_CARD)
        self.status_label.pack(side="left")

        self.reconnect_btn = tk.Label(self.status_frame, text="[Baglan]",
                                       font=self.font_status, fg=ACCENT_BLUE, bg=BG_CARD,
                                       cursor="hand2")
        self.reconnect_btn.pack(side="right")
        self.reconnect_btn.bind("<Button-1>", lambda e: self.try_connect())

        # Separator
        tk.Frame(self.root, bg=BORDER_COLOR, height=1).pack(fill="x", padx=15)

        # Module list
        scroll_frame = tk.Frame(self.root, bg=BG_DARK, pady=10)
        scroll_frame.pack(fill="both", expand=True)

        for mod in MODULES:
            self.create_module_card(scroll_frame, mod)

        # Footer
        footer = tk.Frame(self.root, bg=BG_DARK, pady=8)
        footer.pack(fill="x")

        # All on / All off buttons
        btn_frame = tk.Frame(footer, bg=BG_DARK)
        btn_frame.pack()

        all_on_btn = tk.Label(btn_frame, text="  Hepsini Ac  ", font=self.font_status,
                               fg=BG_DARK, bg=ACCENT_GREEN, padx=15, pady=4, cursor="hand2")
        all_on_btn.pack(side="left", padx=5)
        all_on_btn.bind("<Button-1>", lambda e: self.enable_all())

        all_off_btn = tk.Label(btn_frame, text="  Hepsini Kapat  ", font=self.font_status,
                                fg=TEXT_PRIMARY, bg=ACCENT_RED, padx=15, pady=4, cursor="hand2")
        all_off_btn.pack(side="left", padx=5)
        all_off_btn.bind("<Button-1>", lambda e: self.disable_all())

        tk.Label(footer, text="Port: 25567  |  MC Helper v1.0",
                 font=self.font_desc, fg=TEXT_SECONDARY, bg=BG_DARK).pack(pady=(8, 0))

    def create_module_card(self, parent, mod):
        card = tk.Frame(parent, bg=BG_CARD, padx=12, pady=10,
                        highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.pack(fill="x", padx=15, pady=3)

        # Left side - icon
        icon_label = tk.Label(card, text=mod["icon"], font=self.font_icon,
                               fg=TEXT_SECONDARY, bg=BG_CARD, width=4)
        icon_label.pack(side="left")

        # Middle - name and description
        info_frame = tk.Frame(card, bg=BG_CARD)
        info_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))

        name_frame = tk.Frame(info_frame, bg=BG_CARD)
        name_frame.pack(anchor="w")

        tk.Label(name_frame, text=mod["name"], font=self.font_module,
                 fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left")

        tk.Label(name_frame, text=f"  [{mod['key']}]", font=self.font_key,
                 fg=TEXT_SECONDARY, bg=BG_CARD).pack(side="left")

        tk.Label(info_frame, text=mod["desc"], font=self.font_desc,
                 fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w")

        # Right side - toggle button
        toggle_frame = tk.Frame(card, bg=BG_CARD)
        toggle_frame.pack(side="right")

        indicator = tk.Canvas(toggle_frame, width=44, height=24,
                               bg=BG_CARD, highlightthickness=0)
        indicator.pack()

        # Draw toggle switch background
        self.draw_toggle(indicator, False)

        indicator.bind("<Button-1>", lambda e, m=mod["id"]: self.toggle_module(m))
        card.bind("<Button-1>", lambda e, m=mod["id"]: self.toggle_module(m))

        # Make all children clickable
        for widget in card.winfo_children():
            widget.bind("<Button-1>", lambda e, m=mod["id"]: self.toggle_module(m))
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    child.bind("<Button-1>", lambda e, m=mod["id"]: self.toggle_module(m))

        self.module_buttons[mod["id"]] = card
        self.module_indicators[mod["id"]] = indicator

    def draw_toggle(self, canvas, active):
        canvas.delete("all")
        bg = ACCENT_GREEN if active else "#484f58"
        circle_x = 30 if active else 14
        # Background pill
        canvas.create_oval(2, 2, 22, 22, fill=bg, outline="")
        canvas.create_oval(22, 2, 42, 22, fill=bg, outline="")
        canvas.create_rectangle(12, 2, 32, 22, fill=bg, outline="")
        # Circle
        canvas.create_oval(circle_x - 8, 4, circle_x + 8, 20, fill="white", outline="")

    def update_module_ui(self, mod_id, active):
        self.module_states[mod_id] = active
        if mod_id in self.module_indicators:
            self.draw_toggle(self.module_indicators[mod_id], active)
        if mod_id in self.module_buttons:
            border = BORDER_ACTIVE if active else BORDER_COLOR
            self.module_buttons[mod_id].configure(highlightbackground=border)

    def toggle_module(self, mod_id):
        if not self.connected:
            self.try_connect()
            return
        self.send_command(f"toggle {mod_id}")

    def enable_all(self):
        if not self.connected:
            self.try_connect()
            return
        for mod in MODULES:
            if not self.module_states[mod["id"]]:
                self.send_command(f"enable {mod['id']}")

    def disable_all(self):
        if not self.connected:
            self.try_connect()
            return
        for mod in MODULES:
            if self.module_states[mod["id"]]:
                self.send_command(f"disable {mod['id']}")

    def send_command(self, cmd):
        try:
            if self.sock:
                self.sock.sendall((cmd + "\n").encode())
        except Exception:
            self.set_disconnected()

    def try_connect(self):
        def connect():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(3)
                self.sock.connect((HOST, PORT))
                self.sock.settimeout(None)
                self.connected = True
                self.root.after(0, self.set_connected)
                self.listen_thread()
            except Exception:
                self.root.after(0, self.set_disconnected)
                # Retry after 3 seconds
                self.root.after(3000, self.try_connect)

        threading.Thread(target=connect, daemon=True).start()

    def listen_thread(self):
        def listen():
            try:
                buffer = ""
                while self.connected:
                    data = self.sock.recv(4096).decode()
                    if not data:
                        break
                    buffer += data
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        self.process_response(line.strip())
            except Exception:
                pass
            self.root.after(0, self.set_disconnected)

        threading.Thread(target=listen, daemon=True).start()

    def process_response(self, line):
        if line.startswith("STATUS "):
            data = line[7:]
            for pair in data.split(","):
                pair = pair.strip()
                if "=" in pair:
                    mod_id, val = pair.split("=", 1)
                    active = val == "1"
                    self.root.after(0, lambda m=mod_id, a=active: self.update_module_ui(m, a))

    def set_connected(self):
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 9, 9, fill=ACCENT_GREEN, outline="")
        self.status_label.configure(text="Minecraft'a baglandi", fg=ACCENT_GREEN)
        self.reconnect_btn.configure(text="")

    def set_disconnected(self):
        self.connected = False
        self.sock = None
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 9, 9, fill=ACCENT_RED, outline="")
        self.status_label.configure(text="Baglanti yok - MC'yi ac", fg=TEXT_SECONDARY)
        self.reconnect_btn.configure(text="[Tekrar Dene]")
        for mod_id in self.module_states:
            self.root.after(0, lambda m=mod_id: self.update_module_ui(m, False))

    def on_close(self):
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    MCHelperApp()
