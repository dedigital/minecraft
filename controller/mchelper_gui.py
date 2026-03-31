"""
MC Helper v2.0 - Premium Control Panel
Remote controller for MC Helper Fabric Mod
"""

import tkinter as tk
from tkinter import font as tkfont
import socket
import threading
import sys
import time

HOST = "127.0.0.1"
PORT = 25567

# ══════════════════ COLORS ══════════════════
BG_MAIN     = "#0a0e17"
BG_HEADER   = "#070b12"
BG_CARD     = "#111827"
BG_CARD_ON  = "#0c1a2e"
BG_TAB      = "#0f1520"
BG_TAB_ACT  = "#141c2b"
BG_STAT     = "#0d1220"

ACCENT      = "#00d4ff"
GREEN       = "#00ff88"
RED         = "#ff4757"
ORANGE      = "#ffa502"
PURPLE      = "#a855f7"
YELLOW      = "#fbbf24"

TXT         = "#e8edf5"
TXT2        = "#7b8a9e"
TXT3        = "#3a4f65"
BORDER      = "#1a2535"
BORDER_ON   = "#00d4ff"


# ══════════════════ MODULE DATA ══════════════════
CATEGORIES = [
    {"id": "combat",   "name": "Combat",   "icon": "\u2694"},
    {"id": "movement", "name": "Movement", "icon": "\u26A1"},
    {"id": "visual",   "name": "Visual",   "icon": "\u25C9"},
    {"id": "player",   "name": "Player",   "icon": "\u2665"},
]

MODULES = [
    {"id": "killaura",      "name": "Kill Aura",       "cat": "combat",   "key": "R", "desc": "Yakin dusmanlari otomatik vur",  "slider": ("aura_range", 2.0, 6.0, 4.0)},
    {"id": "antiknockback", "name": "Anti-Knockback",   "cat": "combat",   "key": "B", "desc": "Geri itilmeyi engelle"},
    {"id": "fly",           "name": "Fly",              "cat": "movement", "key": "H", "desc": "Ucma modu"},
    {"id": "speed",         "name": "Speed",            "cat": "movement", "key": "J", "desc": "Hizli hareket",                 "slider": ("speed_mult", 1.0, 5.0, 1.8)},
    {"id": "autosprint",    "name": "Auto-Sprint",      "cat": "movement", "key": "K", "desc": "Otomatik kosma"},
    {"id": "nofall",        "name": "No Fall",          "cat": "movement", "key": "N", "desc": "Dusme hasari yok"},
    {"id": "step",          "name": "Step Assist",      "cat": "movement", "key": "V", "desc": "Bloklarin uzerinden yuru"},
    {"id": "fullbright",    "name": "Fullbright",       "cat": "visual",   "key": "G", "desc": "Karanlikta gorme"},
    {"id": "nohunger",      "name": "No Hunger",        "cat": "player",   "key": "P", "desc": "Aclik yok (singleplayer)"},
]


class ToggleSwitch:
    """Animated pill-shaped toggle switch."""
    def __init__(self, parent, width=48, height=24, command=None):
        self.width = width
        self.height = height
        self.command = command
        self.active = False
        self.anim_pos = 0.0  # 0=off, 1=on

        self.canvas = tk.Canvas(parent, width=width, height=height,
                                bg=BG_CARD, highlightthickness=0, cursor="hand2")
        self.canvas.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.canvas.delete("all")
        w, h = self.width, self.height
        r = h // 2

        # Background pill
        bg = self._lerp_color("#2a3444", GREEN, self.anim_pos)
        self.canvas.create_oval(1, 1, h - 1, h - 1, fill=bg, outline="")
        self.canvas.create_oval(w - h + 1, 1, w - 1, h - 1, fill=bg, outline="")
        self.canvas.create_rectangle(r, 1, w - r, h - 1, fill=bg, outline="")

        # Circle
        cx = r + (w - h) * self.anim_pos
        cr = r - 3
        self.canvas.create_oval(cx - cr, h // 2 - cr, cx + cr, h // 2 + cr,
                                fill="white", outline="")

    def _lerp_color(self, c1, c2, t):
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _on_click(self, event=None):
        if self.command:
            self.command()

    def set_state(self, active, animate=True):
        self.active = active
        if animate:
            self._animate(1.0 if active else 0.0)
        else:
            self.anim_pos = 1.0 if active else 0.0
            self._draw()

    def _animate(self, target):
        step = 0.15
        if abs(self.anim_pos - target) < step:
            self.anim_pos = target
            self._draw()
            return
        self.anim_pos += step if target > self.anim_pos else -step
        self._draw()
        self.canvas.after(16, lambda: self._animate(target))

    def update_bg(self, bg):
        self.canvas.configure(bg=bg)


class CustomSlider:
    """Canvas-based slider with drag interaction."""
    def __init__(self, parent, min_val, max_val, default, label, on_change=None):
        self.min_val = min_val
        self.max_val = max_val
        self.value = default
        self.label = label
        self.on_change = on_change
        self.dragging = False

        self.frame = tk.Frame(parent, bg=BG_CARD)
        self.val_label = tk.Label(self.frame, text=f"{label}: {default:.1f}",
                                   font=("Segoe UI", 8), fg=TXT2, bg=BG_CARD)
        self.val_label.pack(anchor="w", padx=(0, 0))

        self.canvas = tk.Canvas(self.frame, width=200, height=16,
                                bg=BG_CARD, highlightthickness=0, cursor="hand2")
        self.canvas.pack(fill="x", pady=(2, 0))
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self._draw()

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 200
        h = 16
        track_y = h // 2
        pct = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_x = int(10 + (w - 20) * pct)

        # Track background
        self.canvas.create_line(10, track_y, w - 10, track_y, fill=TXT3, width=3, capstyle="round")
        # Filled portion
        if fill_x > 10:
            self.canvas.create_line(10, track_y, fill_x, track_y, fill=ACCENT, width=3, capstyle="round")
        # Handle
        self.canvas.create_oval(fill_x - 6, track_y - 6, fill_x + 6, track_y + 6,
                                fill=ACCENT, outline="white", width=1)

        self.val_label.configure(text=f"{self.label}: {self.value:.1f}")

    def _pos_to_val(self, x):
        w = self.canvas.winfo_width() or 200
        pct = max(0, min(1, (x - 10) / (w - 20)))
        return self.min_val + (self.max_val - self.min_val) * pct

    def _on_press(self, event):
        self.dragging = True
        self.value = round(self._pos_to_val(event.x), 1)
        self._draw()

    def _on_drag(self, event):
        if self.dragging:
            self.value = round(self._pos_to_val(event.x), 1)
            self._draw()

    def _on_release(self, event):
        self.dragging = False
        self.value = round(self._pos_to_val(event.x), 1)
        self._draw()
        if self.on_change:
            self.on_change(self.value)

    def set_value(self, val):
        self.value = val
        self._draw()


class MCHelperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MC Helper v2.0")
        self.root.geometry("480x700")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)

        # Try to set dark title bar on Windows
        try:
            from ctypes import windll
            self.root.update()
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, byref(c_int(1)), 4)
        except Exception:
            pass

        self.sock = None
        self.connected = False
        self.current_cat = "combat"
        self.module_states = {m["id"]: False for m in MODULES}
        self.toggles = {}
        self.sliders = {}
        self.card_frames = {}
        self.player_info = {"x": 0, "y": 0, "z": 0, "hp": 20, "maxhp": 20,
                            "food": 20, "armor": 0, "fps": 0}

        self._build_header()
        self._build_tabs()
        self._build_content()
        self._build_statusbar()
        self._build_footer()

        self.show_category("combat")
        self.try_connect()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    # ══════════ HEADER ══════════
    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_HEADER, pady=12)
        header.pack(fill="x")

        left = tk.Frame(header, bg=BG_HEADER)
        left.pack(side="left", padx=20)

        tk.Label(left, text="MC", font=("Segoe UI", 22, "bold"),
                 fg=ACCENT, bg=BG_HEADER).pack(side="left")
        tk.Label(left, text="HELPER", font=("Segoe UI", 22, "bold"),
                 fg=TXT, bg=BG_HEADER).pack(side="left", padx=(4, 0))
        tk.Label(left, text="v2.0", font=("Segoe UI", 10),
                 fg=TXT2, bg=BG_HEADER).pack(side="left", padx=(8, 0), pady=(8, 0))

        right = tk.Frame(header, bg=BG_HEADER)
        right.pack(side="right", padx=20)

        self.conn_dot = tk.Canvas(right, width=10, height=10, bg=BG_HEADER, highlightthickness=0)
        self.conn_dot.pack(side="left", padx=(0, 6))
        self.conn_dot.create_oval(1, 1, 9, 9, fill=RED, outline="", tags="dot")

        self.conn_label = tk.Label(right, text="Baglanti yok", font=("Segoe UI", 9),
                                    fg=TXT2, bg=BG_HEADER)
        self.conn_label.pack(side="left")

    # ══════════ TABS ══════════
    def _build_tabs(self):
        self.tab_frame = tk.Frame(self.root, bg=BG_TAB, pady=2)
        self.tab_frame.pack(fill="x")

        self.tab_buttons = {}
        self.tab_indicators = {}

        for cat in CATEGORIES:
            btn_frame = tk.Frame(self.tab_frame, bg=BG_TAB)
            btn_frame.pack(side="left", expand=True, fill="x")

            btn = tk.Label(btn_frame, text=f"{cat['icon']} {cat['name']}",
                           font=("Segoe UI", 10), fg=TXT2, bg=BG_TAB,
                           pady=8, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, c=cat["id"]: self.show_category(c))

            indicator = tk.Frame(btn_frame, bg=BG_TAB, height=2)
            indicator.pack(fill="x")

            self.tab_buttons[cat["id"]] = btn
            self.tab_indicators[cat["id"]] = indicator

    def show_category(self, cat_id):
        self.current_cat = cat_id
        for cid, btn in self.tab_buttons.items():
            if cid == cat_id:
                btn.configure(fg=ACCENT, bg=BG_TAB_ACT)
                self.tab_indicators[cid].configure(bg=ACCENT)
            else:
                btn.configure(fg=TXT2, bg=BG_TAB)
                self.tab_indicators[cid].configure(bg=BG_TAB)

        for mid, frame in self.card_frames.items():
            mod = next(m for m in MODULES if m["id"] == mid)
            if mod["cat"] == cat_id:
                frame.pack(fill="x", padx=16, pady=4)
            else:
                frame.pack_forget()

    # ══════════ CONTENT ══════════
    def _build_content(self):
        self.content = tk.Frame(self.root, bg=BG_MAIN)
        self.content.pack(fill="both", expand=True, pady=(8, 0))

        for mod in MODULES:
            self._build_card(mod)

    def _build_card(self, mod):
        card = tk.Frame(self.content, bg=BG_CARD, padx=14, pady=10,
                        highlightbackground=BORDER, highlightthickness=1)

        # Top row
        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill="x")

        # Name
        tk.Label(top, text=mod["name"], font=("Segoe UI", 12, "bold"),
                 fg=TXT, bg=BG_CARD).pack(side="left")

        # Key badge
        badge = tk.Label(top, text=f" {mod['key']} ", font=("Consolas", 9),
                         fg=TXT2, bg="#1a2535", padx=4)
        badge.pack(side="left", padx=(8, 0))

        # Toggle
        toggle = ToggleSwitch(top, command=lambda m=mod["id"]: self.toggle_module(m))
        toggle.canvas.pack(side="right")
        self.toggles[mod["id"]] = toggle

        # Description
        tk.Label(card, text=mod["desc"], font=("Segoe UI", 9),
                 fg=TXT2, bg=BG_CARD, anchor="w").pack(fill="x", pady=(4, 0))

        # Slider if applicable
        if "slider" in mod:
            param, min_v, max_v, default = mod["slider"]
            slider = CustomSlider(card, min_v, max_v, default,
                                   param.replace("_", " ").title(),
                                   on_change=lambda v, p=param: self.on_slider_change(p, v))
            slider.frame.pack(fill="x", pady=(6, 0))
            self.sliders[param] = slider

        self.card_frames[mod["id"]] = card

    # ══════════ STATUS BAR ══════════
    def _build_statusbar(self):
        sep = tk.Frame(self.root, bg=BORDER, height=1)
        sep.pack(fill="x", padx=16)

        bar = tk.Frame(self.root, bg=BG_STAT, pady=10, padx=16)
        bar.pack(fill="x")

        # Health bar row
        hp_row = tk.Frame(bar, bg=BG_STAT)
        hp_row.pack(fill="x", pady=(0, 4))

        tk.Label(hp_row, text="\u2665", font=("Segoe UI", 11), fg=RED,
                 bg=BG_STAT).pack(side="left")

        self.hp_canvas = tk.Canvas(hp_row, width=180, height=14, bg=BG_STAT, highlightthickness=0)
        self.hp_canvas.pack(side="left", padx=(6, 8))

        self.hp_label = tk.Label(hp_row, text="20/20", font=("Segoe UI", 9),
                                  fg=TXT2, bg=BG_STAT)
        self.hp_label.pack(side="left")

        # Food
        tk.Label(hp_row, text="  \u2617", font=("Segoe UI", 11), fg=ORANGE,
                 bg=BG_STAT).pack(side="left", padx=(12, 0))

        self.food_canvas = tk.Canvas(hp_row, width=100, height=14, bg=BG_STAT, highlightthickness=0)
        self.food_canvas.pack(side="left", padx=(6, 8))

        self.food_label = tk.Label(hp_row, text="20", font=("Segoe UI", 9),
                                    fg=TXT2, bg=BG_STAT)
        self.food_label.pack(side="left")

        # Info row
        info_row = tk.Frame(bar, bg=BG_STAT)
        info_row.pack(fill="x")

        self.coord_label = tk.Label(info_row, text="\u2316  0.0 / 0.0 / 0.0",
                                     font=("Consolas", 10), fg=ACCENT, bg=BG_STAT)
        self.coord_label.pack(side="left")

        self.fps_label = tk.Label(info_row, text="FPS: --",
                                   font=("Segoe UI", 9), fg=TXT2, bg=BG_STAT)
        self.fps_label.pack(side="right")

        self.armor_label = tk.Label(info_row, text="\u229E Armor: 0",
                                     font=("Segoe UI", 9), fg="#54a0ff", bg=BG_STAT)
        self.armor_label.pack(side="right", padx=(0, 16))

        self._draw_bars()

    def _draw_bars(self):
        # Health bar
        self.hp_canvas.delete("all")
        w = 180
        hp = self.player_info["hp"]
        maxhp = self.player_info["maxhp"]
        pct = min(1, hp / maxhp) if maxhp > 0 else 0
        self.hp_canvas.create_rectangle(0, 2, w, 12, fill="#1a0a0a", outline="")
        if pct > 0:
            self.hp_canvas.create_rectangle(0, 2, w * pct, 12, fill=RED, outline="")
        self.hp_label.configure(text=f"{int(hp)}/{int(maxhp)}")

        # Food bar
        self.food_canvas.delete("all")
        fw = 100
        food_pct = min(1, self.player_info["food"] / 20)
        self.food_canvas.create_rectangle(0, 2, fw, 12, fill="#1a0f00", outline="")
        if food_pct > 0:
            self.food_canvas.create_rectangle(0, 2, fw * food_pct, 12, fill=ORANGE, outline="")
        self.food_label.configure(text=str(self.player_info["food"]))

    # ══════════ FOOTER ══════════
    def _build_footer(self):
        footer = tk.Frame(self.root, bg=BG_MAIN, pady=6)
        footer.pack(fill="x")

        keys = "G=Fullbright  H=Fly  J=Speed  K=Sprint  N=NoFall  R=Aura  B=AntiKB  V=Step  P=NoHunger  C=Zoom  M=Menu"
        tk.Label(footer, text=keys, font=("Consolas", 7), fg=TXT3, bg=BG_MAIN,
                 wraplength=460).pack()

    # ══════════ MODULE CONTROL ══════════
    def toggle_module(self, mod_id):
        if not self.connected:
            self.try_connect()
            return
        self.send(f"toggle {mod_id}")

    def on_slider_change(self, param, value):
        if not self.connected:
            return
        self.send(f"set {param} {value:.1f}")

    def update_module(self, mod_id, active):
        self.module_states[mod_id] = active
        if mod_id in self.toggles:
            self.toggles[mod_id].set_state(active)
        if mod_id in self.card_frames:
            border = BORDER_ON if active else BORDER
            self.card_frames[mod_id].configure(highlightbackground=border)
            bg = BG_CARD_ON if active else BG_CARD
            self.card_frames[mod_id].configure(bg=bg)
            for w in self.card_frames[mod_id].winfo_children():
                try:
                    w.configure(bg=bg)
                    for c in w.winfo_children():
                        try:
                            c.configure(bg=bg)
                        except Exception:
                            pass
                except Exception:
                    pass

    def update_info(self, data):
        self.player_info.update(data)
        self.coord_label.configure(
            text=f"\u2316  {data.get('x', 0):.1f} / {data.get('y', 0):.1f} / {data.get('z', 0):.1f}")
        self.fps_label.configure(text=f"FPS: {int(data.get('fps', 0))}")
        self.armor_label.configure(text=f"\u229E Armor: {int(data.get('armor', 0))}")
        self._draw_bars()

    def update_config(self, data):
        for key, val in data.items():
            if key in self.sliders:
                self.sliders[key].set_value(float(val))

    # ══════════ NETWORKING ══════════
    def send(self, msg):
        try:
            if self.sock:
                self.sock.sendall((msg + "\n").encode())
        except Exception:
            self.set_disconnected()

    def try_connect(self):
        def connect():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((HOST, PORT))
                s.settimeout(None)
                self.sock = s
                self.connected = True
                self.root.after(0, self.set_connected)
                self._listen()
            except Exception:
                self.root.after(0, self.set_disconnected)
                time.sleep(3)
                if not self.connected:
                    self.root.after(0, self.try_connect)

        threading.Thread(target=connect, daemon=True).start()

    def _listen(self):
        def run():
            buf = ""
            try:
                while self.connected:
                    data = self.sock.recv(4096).decode()
                    if not data:
                        break
                    buf += data
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        self._process(line.strip())
            except Exception:
                pass
            self.root.after(0, self.set_disconnected)

        threading.Thread(target=run, daemon=True).start()

    def _process(self, line):
        if line.startswith("STATUS "):
            for pair in line[7:].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    k = k.strip()
                    active = v.strip() == "1"
                    self.root.after(0, lambda m=k, a=active: self.update_module(m, a))

        elif line.startswith("INFO "):
            info = {}
            for pair in line[5:].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    try:
                        info[k.strip()] = float(v.strip())
                    except ValueError:
                        info[k.strip()] = v.strip()
            self.root.after(0, lambda d=info: self.update_info(d))

        elif line.startswith("CONFIG "):
            cfg = {}
            for pair in line[7:].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    cfg[k.strip()] = v.strip()
            self.root.after(0, lambda d=cfg: self.update_config(d))

    def set_connected(self):
        self.conn_dot.delete("dot")
        self.conn_dot.create_oval(1, 1, 9, 9, fill=GREEN, outline="", tags="dot")
        self.conn_label.configure(text="Baglandi", fg=GREEN)

    def set_disconnected(self):
        self.connected = False
        try:
            self.sock.close()
        except Exception:
            pass
        self.sock = None
        self.conn_dot.delete("dot")
        self.conn_dot.create_oval(1, 1, 9, 9, fill=RED, outline="", tags="dot")
        self.conn_label.configure(text="Baglanti yok", fg=TXT2)
        for mid in self.module_states:
            self.root.after(0, lambda m=mid: self.update_module(m, False))

    def on_close(self):
        self.connected = False
        try:
            self.sock.close()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    MCHelperApp()
