#!/usr/bin/env python3
"""
MC Helper v2.0 - Premium GUI Controller
Connects to MC Helper Minecraft mod via TCP socket on localhost:25567.
Built with pure tkinter - no external dependencies.
"""

import tkinter as tk
import socket
import threading
import time
import sys

# ─── Color Palette ───────────────────────────────────────────────────────────

BG_MAIN       = "#0a0e17"
BG_SIDEBAR    = "#0f1520"
BG_CARD       = "#141c2b"
BG_CARD_HOVER = "#1a2438"
ACCENT        = "#00d4ff"
ACCENT_GREEN  = "#00ff88"
ACCENT_RED    = "#ff4757"
ACCENT_ORANGE = "#ffa502"
ACCENT_PURPLE = "#a855f7"
TEXT_WHITE     = "#e8edf5"
TEXT_GRAY      = "#6b7b8d"
TEXT_DIM       = "#3a4553"
BORDER         = "#1e2a3a"
HP_RED         = "#ff4757"
FOOD_ORANGE    = "#ff9f43"
ARMOR_BLUE     = "#54a0ff"
BORDER_ACTIVE  = "#00d4ff"

FONT = "Segoe UI"
FONT_MONO = "Consolas"

HOST = "127.0.0.1"
PORT = 25567

# ─── Module Definitions ─────────────────────────────────────────────────────

MODULES = {
    "combat": [
        {"id": "killaura",      "name": "Kill Aura",      "key": "R",
         "desc": "Yakin dusmanlari otomatik vur",
         "slider": {"param": "aura_range", "min": 2.0, "max": 6.0, "default": 4.0, "label": "Mesafe"}},
        {"id": "antiknockback", "name": "Anti-Knockback",  "key": "B",
         "desc": "Geri itilmeyi engelle"},
    ],
    "movement": [
        {"id": "fly",        "name": "Fly",         "key": "H", "desc": "Ucma modu"},
        {"id": "speed",      "name": "Speed",       "key": "J", "desc": "Hizli hareket",
         "slider": {"param": "speed_mult", "min": 1.0, "max": 5.0, "default": 1.8, "label": "Carpan"}},
        {"id": "autosprint", "name": "Auto-Sprint", "key": "K", "desc": "Otomatik kosma"},
        {"id": "nofall",     "name": "No Fall",     "key": "N", "desc": "Dusme hasari yok"},
        {"id": "step",       "name": "Step Assist", "key": "V", "desc": "Bloklarin uzerinden yuru"},
    ],
    "visual": [
        {"id": "fullbright", "name": "Fullbright", "key": "G", "desc": "Karanlikta gorme"},
        {"id": "zoom_info",  "name": "Zoom",       "key": "C", "desc": "Basili tut - yakinlastir",
         "info_only": True},
    ],
    "player": [
        {"id": "nohunger", "name": "No Hunger", "key": "P", "desc": "Aclik yok"},
    ],
}

CATEGORY_META = [
    ("combat",   "\u2694", "Combat"),
    ("movement", "\u26A1", "Movement"),
    ("visual",   "\u25C9", "Visual"),
    ("player",   "\u2665", "Player"),
]


# ─── Toggle Switch (Canvas) ─────────────────────────────────────────────────

class ToggleSwitch(tk.Canvas):
    """Animated pill-shaped toggle drawn entirely on a Canvas."""

    W, H = 46, 24
    PAD = 3
    STEPS = 7
    DELAY = 18

    def __init__(self, master, command=None, **kw):
        super().__init__(master, width=self.W, height=self.H,
                         bg=BG_CARD, highlightthickness=0, cursor="hand2", **kw)
        self.state = False
        self.command = command
        self._pos = 0.0          # 0..1
        self._anim_id = None
        self._draw()
        self.bind("<Button-1>", self._click)

    @staticmethod
    def _lerp(c1, c2, t):
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self):
        self.delete("all")
        w, h, p = self.W, self.H, self.PAD
        r = h // 2
        bg = self._lerp(TEXT_DIM, ACCENT_GREEN, self._pos)
        # pill body
        self.create_oval(0, 0, h, h, fill=bg, outline="")
        self.create_oval(w - h, 0, w, h, fill=bg, outline="")
        self.create_rectangle(r, 0, w - r, h, fill=bg, outline="")
        # knob
        travel = w - h
        cx = r + travel * self._pos
        cy = h // 2
        kr = r - p
        self.create_oval(cx - kr, cy - kr, cx + kr, cy + kr, fill="#ffffff", outline="")

    def _click(self, _e=None):
        self.set_state(not self.state, from_user=True)

    def set_state(self, on, from_user=False):
        if on == self.state:
            return
        self.state = on
        self._animate(1.0 if on else 0.0)
        if from_user and self.command:
            self.command(on)

    def _animate(self, target):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        delta = (target - self._pos) / self.STEPS
        self._step(delta, self.STEPS)

    def _step(self, delta, remaining):
        if remaining <= 0:
            self._pos = 1.0 if self.state else 0.0
            self._draw()
            return
        self._pos += delta
        self._draw()
        self._anim_id = self.after(self.DELAY, self._step, delta, remaining - 1)

    def set_bg(self, color):
        self.configure(bg=color)


# ─── Custom Slider (Canvas) ─────────────────────────────────────────────────

class CustomSlider(tk.Canvas):
    """Draggable slider with accent-colored track."""

    TRACK_H = 4
    KNOB_R = 7
    H = 26

    def __init__(self, master, width=200, min_val=0, max_val=1,
                 default=0.5, command=None, **kw):
        super().__init__(master, width=width, height=self.H,
                         bg=BG_CARD, highlightthickness=0, cursor="hand2", **kw)
        self.sw = width
        self.min_val = min_val
        self.max_val = max_val
        self.value = default
        self.command = command
        self._dragging = False
        self._draw()
        self.bind("<Button-1>",        self._press)
        self.bind("<B1-Motion>",       self._drag)
        self.bind("<ButtonRelease-1>", self._release)

    def _val_to_x(self, v):
        pad = self.KNOB_R + 4
        usable = self.sw - 2 * pad
        ratio = (v - self.min_val) / max(self.max_val - self.min_val, 0.001)
        return pad + ratio * usable

    def _x_to_val(self, x):
        pad = self.KNOB_R + 4
        usable = self.sw - 2 * pad
        ratio = max(0.0, min(1.0, (x - pad) / max(usable, 1)))
        return round(self.min_val + ratio * (self.max_val - self.min_val), 1)

    def _draw(self):
        self.delete("all")
        y = self.H // 2
        pad = self.KNOB_R + 4
        end = self.sw - pad
        # track bg
        self.create_line(pad, y, end, y, fill=TEXT_DIM, width=self.TRACK_H, capstyle="round")
        # filled
        cx = self._val_to_x(self.value)
        self.create_line(pad, y, cx, y, fill=ACCENT, width=self.TRACK_H, capstyle="round")
        # knob
        r = self.KNOB_R
        self.create_oval(cx - r, y - r, cx + r, y + r, fill=ACCENT, outline="#ffffff", width=2)

    def _press(self, e):
        self._dragging = True
        self.value = self._x_to_val(e.x)
        self._draw()

    def _drag(self, e):
        if self._dragging:
            self.value = self._x_to_val(e.x)
            self._draw()

    def _release(self, e):
        self._dragging = False
        self.value = self._x_to_val(e.x)
        self._draw()
        if self.command:
            self.command(self.value)

    def set_value(self, v):
        self.value = max(self.min_val, min(self.max_val, round(v, 1)))
        self._draw()

    def set_bg(self, color):
        self.configure(bg=color)


# ─── Module Card ─────────────────────────────────────────────────────────────

class ModuleCard(tk.Frame):
    """Dark card with module info, toggle, optional slider."""

    def __init__(self, master, mod, toggle_cb, slider_cb=None, **kw):
        super().__init__(master, bg=BG_CARD, highlightbackground=BORDER,
                         highlightthickness=1, **kw)
        self.mod = mod
        self.info_only = mod.get("info_only", False)
        self._bg = BG_CARD

        inner = tk.Frame(self, bg=BG_CARD)
        inner.pack(fill="x", padx=14, pady=(10, 8))

        # ── top row ──
        top = tk.Frame(inner, bg=BG_CARD)
        top.pack(fill="x")

        self.name_lbl = tk.Label(top, text=mod["name"], font=(FONT, 12, "bold"),
                                 fg=TEXT_WHITE, bg=BG_CARD, anchor="w")
        self.name_lbl.pack(side="left")

        # keybind badge
        self.badge_frame = tk.Frame(top, bg=TEXT_DIM, padx=5, pady=1)
        self.badge_frame.pack(side="left", padx=(8, 0))
        self.badge_lbl = tk.Label(self.badge_frame, text=mod["key"],
                                  font=(FONT_MONO, 8, "bold"), fg=TEXT_GRAY, bg=TEXT_DIM)
        self.badge_lbl.pack()

        # toggle or info label
        self.toggle = None
        if self.info_only:
            self.info_lbl = tk.Label(top, text="Basili tut", font=(FONT, 9),
                                     fg=TEXT_GRAY, bg=BG_CARD)
            self.info_lbl.pack(side="right")
        else:
            self.toggle = ToggleSwitch(top, command=lambda on, m=mod["id"]: toggle_cb(m, on))
            self.toggle.pack(side="right")

        # description
        self.desc_lbl = tk.Label(inner, text=mod["desc"], font=(FONT, 9),
                                 fg=TEXT_GRAY, bg=BG_CARD, anchor="w")
        self.desc_lbl.pack(fill="x", pady=(4, 0))

        # optional slider
        self.slider = None
        self.val_label = None
        if "slider" in mod:
            s = mod["slider"]
            sf = tk.Frame(inner, bg=BG_CARD)
            sf.pack(fill="x", pady=(6, 0))
            self.slider_label = tk.Label(sf, text=s["label"] + ":",
                                         font=(FONT, 9), fg=TEXT_GRAY, bg=BG_CARD)
            self.slider_label.pack(side="left")
            self.val_label = tk.Label(sf, text=f'{s["default"]:.1f}',
                                      font=(FONT, 9, "bold"), fg=ACCENT, bg=BG_CARD)
            self.val_label.pack(side="right")
            self.slider = CustomSlider(inner, width=420, min_val=s["min"],
                                       max_val=s["max"], default=s["default"],
                                       command=lambda v, p=s["param"]: self._on_slide(v, p, slider_cb))
            self.slider.pack(fill="x", pady=(2, 0))

        # hover
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        for w in self._descendants(self):
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)

    def _on_slide(self, val, param, cb):
        if self.val_label:
            self.val_label.config(text=f"{val:.1f}")
        if cb:
            cb(param, val)

    def _descendants(self, w):
        out = []
        for c in w.winfo_children():
            out.append(c)
            out.extend(self._descendants(c))
        return out

    def _set_bg(self, bg):
        self._bg = bg
        self.config(bg=bg)
        for w in self._descendants(self):
            try:
                cur = str(w.cget("bg"))
                if cur in (BG_CARD, BG_CARD_HOVER):
                    w.config(bg=bg)
            except Exception:
                pass
        if self.toggle:
            self.toggle.set_bg(bg)
        if self.slider:
            self.slider.set_bg(bg)

    def _enter(self, _e):
        if self._bg != BG_CARD_HOVER:
            self._set_bg(BG_CARD_HOVER)

    def _leave(self, _e):
        if self._bg != BG_CARD:
            self._set_bg(BG_CARD)

    def set_toggle(self, on):
        if self.toggle:
            self.toggle.set_state(on, from_user=False)
        # glow border when active
        self.config(highlightbackground=BORDER_ACTIVE if on else BORDER)

    def set_slider_value(self, v):
        if self.slider:
            self.slider.set_value(v)
        if self.val_label:
            self.val_label.config(text=f"{v:.1f}")


# ─── Status Bar ──────────────────────────────────────────────────────────────

class StatusBar(tk.Frame):
    """Bottom bar: health, food, armor, coords, FPS."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG_SIDEBAR, **kw)
        self.hp = 20.0
        self.maxhp = 20.0
        self.food = 20
        self.armor = 0
        self.fps = 0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        # bars row
        self.bar_cv = tk.Canvas(self, height=20, bg=BG_SIDEBAR, highlightthickness=0)
        self.bar_cv.pack(fill="x", padx=16, pady=(8, 0))

        # stats row
        row = tk.Frame(self, bg=BG_SIDEBAR)
        row.pack(fill="x", padx=16, pady=(4, 8))

        self.armor_lbl = tk.Label(row, text="\u229E Armor: 0", font=(FONT, 9),
                                  fg=ARMOR_BLUE, bg=BG_SIDEBAR)
        self.armor_lbl.pack(side="left")
        self.fps_lbl = tk.Label(row, text="\u26A1 FPS: 0", font=(FONT, 9),
                                fg=ACCENT_GREEN, bg=BG_SIDEBAR)
        self.fps_lbl.pack(side="left", padx=(16, 0))
        self.coord_lbl = tk.Label(row, text="\u2316 0.0 / 0.0 / 0.0",
                                  font=(FONT_MONO, 9), fg=ACCENT, bg=BG_SIDEBAR)
        self.coord_lbl.pack(side="right")

        self.after(100, self._draw_bars)

    def _draw_bars(self):
        c = self.bar_cv
        c.delete("all")
        w = c.winfo_width() or 460
        mid = w // 2 - 10

        # health
        hp_r = self.hp / max(self.maxhp, 1)
        c.create_text(4, 10, text="\u2665", fill=HP_RED, font=(FONT, 10), anchor="w")
        bx, bw = 20, mid - 68
        c.create_rectangle(bx, 3, bx + bw, 17, fill="#1a0a0a", outline="")
        c.create_rectangle(bx, 3, bx + bw * hp_r, 17, fill=HP_RED, outline="")
        c.create_text(bx + bw + 6, 10, text=f"{self.hp:.0f}/{self.maxhp:.0f}",
                      fill=TEXT_WHITE, font=(FONT, 9, "bold"), anchor="w")

        # food
        food_r = self.food / 20
        fx = mid + 20
        c.create_text(fx, 10, text="\u2617", fill=FOOD_ORANGE, font=(FONT, 10), anchor="w")
        fbx, fbw = fx + 16, mid - 68
        c.create_rectangle(fbx, 3, fbx + fbw, 17, fill="#1a0f00", outline="")
        c.create_rectangle(fbx, 3, fbx + fbw * food_r, 17, fill=FOOD_ORANGE, outline="")
        c.create_text(fbx + fbw + 6, 10, text=f"{self.food}",
                      fill=TEXT_WHITE, font=(FONT, 9, "bold"), anchor="w")

    def update_info(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        self.armor_lbl.config(text=f"\u229E Armor: {self.armor}")
        self.fps_lbl.config(text=f"\u26A1 FPS: {self.fps}")
        self.coord_lbl.config(text=f"\u2316 {self.x:.1f} / {self.y:.1f} / {self.z:.1f}")
        self._draw_bars()


# ─── Main Application ───────────────────────────────────────────────────────

class MCHelperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MC Helper v2.0")
        self.root.geometry("500x720")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)
        try:
            self.root.iconbitmap("")
        except Exception:
            pass

        self.sock = None
        self.connected = False
        self.recv_buffer = ""
        self.module_states = {}
        self.config_values = {}
        self.cards = {}
        self.current_category = "combat"

        self._build_ui()
        self._start_network()
        self.root.after(150, self.status_bar._draw_bars)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── title bar ────────────────────────────────────────────────────
        title = tk.Frame(self.root, bg=BG_SIDEBAR, height=50)
        title.pack(fill="x")
        title.pack_propagate(False)

        lf = tk.Frame(title, bg=BG_SIDEBAR)
        lf.pack(side="left", padx=(16, 0), pady=10)
        tk.Label(lf, text="MC", font=(FONT, 16, "bold"),
                 fg=ACCENT, bg=BG_SIDEBAR).pack(side="left")
        tk.Label(lf, text="HELPER", font=(FONT, 16, "bold"),
                 fg=TEXT_WHITE, bg=BG_SIDEBAR).pack(side="left", padx=(5, 0))
        tk.Label(lf, text="v2.0", font=(FONT, 9),
                 fg=TEXT_GRAY, bg=BG_SIDEBAR).pack(side="left", padx=(8, 0), pady=(4, 0))

        rf = tk.Frame(title, bg=BG_SIDEBAR)
        rf.pack(side="right", padx=(0, 16), pady=10)
        self.conn_dot = tk.Canvas(rf, width=10, height=10, bg=BG_SIDEBAR, highlightthickness=0)
        self.conn_dot.pack(side="left", padx=(0, 6))
        self.conn_dot.create_oval(1, 1, 9, 9, fill=ACCENT_RED, outline="", tags="dot")
        self.conn_label = tk.Label(rf, text="Baglanti bekleniyor...",
                                   font=(FONT, 9), fg=TEXT_GRAY, bg=BG_SIDEBAR)
        self.conn_label.pack(side="left")

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # ── category tabs ────────────────────────────────────────────────
        tab_bar = tk.Frame(self.root, bg=BG_SIDEBAR, height=40)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        self.tab_btns = {}
        self.tab_inds = {}
        for cat_id, icon, label in CATEGORY_META:
            col = tk.Frame(tab_bar, bg=BG_SIDEBAR)
            col.pack(side="left", fill="both", expand=True)
            btn = tk.Label(col, text=f"{icon}  {label}", font=(FONT, 10),
                           fg=TEXT_GRAY, bg=BG_SIDEBAR, cursor="hand2", anchor="center")
            btn.pack(fill="both", expand=True)
            btn.bind("<Button-1>", lambda e, c=cat_id: self._switch_tab(c))
            ind = tk.Frame(col, bg=BG_SIDEBAR, height=2)
            ind.pack(fill="x", side="bottom")
            self.tab_btns[cat_id] = btn
            self.tab_inds[cat_id] = ind

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # ── content ──────────────────────────────────────────────────────
        content = tk.Frame(self.root, bg=BG_MAIN)
        content.pack(fill="both", expand=True)

        # controls row
        ctrl = tk.Frame(content, bg=BG_MAIN)
        ctrl.pack(fill="x", padx=16, pady=(8, 2))

        self.cat_title = tk.Label(ctrl, text="", font=(FONT, 10, "bold"),
                                  fg=TEXT_GRAY, bg=BG_MAIN)
        self.cat_title.pack(side="left")

        off_btn = tk.Label(ctrl, text="  ALL OFF  ", font=(FONT, 8, "bold"),
                           fg=ACCENT_RED, bg=BG_CARD, cursor="hand2")
        off_btn.pack(side="right", padx=(4, 0))
        off_btn.bind("<Button-1>", lambda e: self._set_all(False))

        on_btn = tk.Label(ctrl, text="  ALL ON  ", font=(FONT, 8, "bold"),
                          fg=ACCENT_GREEN, bg=BG_CARD, cursor="hand2")
        on_btn.pack(side="right")
        on_btn.bind("<Button-1>", lambda e: self._set_all(True))

        # scrollable card area
        self.canvas = tk.Canvas(content, bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, side="left")

        self.card_frame = tk.Frame(self.canvas, bg=BG_MAIN)
        self.canvas_win = self.canvas.create_window((0, 0), window=self.card_frame,
                                                     anchor="nw", width=486)
        self.card_frame.bind("<Configure>",
                             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # ── separator + status ───────────────────────────────────────────
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill="x")

        # ── keybind footer ───────────────────────────────────────────────
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")
        keys = ("R Aura  |  B Anti-KB  |  H Fly  |  J Speed  |  K Sprint  |  "
                "N NoFall  |  V Step  |  G Bright  |  C Zoom  |  P NoHunger")
        tk.Label(self.root, text=keys, font=(FONT_MONO, 7), fg=TEXT_DIM,
                 bg=BG_SIDEBAR, pady=5).pack(fill="x")

        # initial category
        self._switch_tab("combat")
        self._pulse_dot()

    def _switch_tab(self, cat_id):
        self.current_category = cat_id
        for cid, btn in self.tab_btns.items():
            active = cid == cat_id
            btn.config(fg=ACCENT if active else TEXT_GRAY)
            self.tab_inds[cid].config(bg=ACCENT if active else BG_SIDEBAR)

        meta = dict((c[0], c) for c in CATEGORY_META)
        _, icon, label = meta[cat_id]
        self.cat_title.config(text=f"{icon}  {label}")

        # rebuild cards
        for w in self.card_frame.winfo_children():
            w.destroy()
        self.cards = {}

        for mod in MODULES.get(cat_id, []):
            card = ModuleCard(self.card_frame, mod,
                              toggle_cb=self._on_toggle, slider_cb=self._on_slider)
            card.pack(fill="x", padx=10, pady=(5, 0))
            self.cards[mod["id"]] = card
            if mod["id"] in self.module_states:
                card.set_toggle(self.module_states[mod["id"]])
            if "slider" in mod and mod["slider"]["param"] in self.config_values:
                card.set_slider_value(self.config_values[mod["slider"]["param"]])

        tk.Frame(self.card_frame, bg=BG_MAIN, height=6).pack()

    def _set_all(self, on):
        for mod in MODULES.get(self.current_category, []):
            if mod.get("info_only"):
                continue
            mid = mod["id"]
            self.module_states[mid] = on
            if mid in self.cards:
                self.cards[mid].set_toggle(on)
            self._send("enable " + mid if on else "disable " + mid)

    def _pulse_dot(self):
        if self.connected:
            self.conn_dot.itemconfig("dot", fill=ACCENT_GREEN)
        else:
            cur = self.conn_dot.itemcget("dot", "fill")
            self.conn_dot.itemconfig("dot", fill=ACCENT_RED if cur == TEXT_DIM else TEXT_DIM)
        self.root.after(700, self._pulse_dot)

    # ── callbacks ────────────────────────────────────────────────────────

    def _on_toggle(self, mod_id, on):
        self.module_states[mod_id] = on
        if mod_id in self.cards:
            self.cards[mod_id].config(
                highlightbackground=BORDER_ACTIVE if on else BORDER)
        self._send(("enable " if on else "disable ") + mod_id)

    def _on_slider(self, param, value):
        self.config_values[param] = value
        self._send(f"set {param} {value:.1f}")

    # ── networking ───────────────────────────────────────────────────────

    def _start_network(self):
        threading.Thread(target=self._net_loop, daemon=True).start()

    def _net_loop(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((HOST, PORT))
                s.settimeout(None)
                self.sock = s
                self.connected = True
                self.root.after(0, self._ui_connected)
                self._send("status")
                self._recv_loop()
            except Exception:
                pass
            finally:
                self.connected = False
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
                self.root.after(0, self._ui_disconnected)
            time.sleep(3)

    def _recv_loop(self):
        buf = ""
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            buf += data.decode("utf-8", errors="replace")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if line:
                    self.root.after(0, self._handle, line)

    def _send(self, msg):
        if self.sock and self.connected:
            try:
                self.sock.sendall((msg + "\n").encode("utf-8"))
            except Exception:
                pass

    def _ui_connected(self):
        self.conn_label.config(text="Minecraft'a baglandi", fg=ACCENT_GREEN)

    def _ui_disconnected(self):
        self.conn_label.config(text="Baglanti bekleniyor...", fg=TEXT_GRAY)
        # reset all toggles visually
        for mid in list(self.module_states):
            self.module_states[mid] = False
            if mid in self.cards:
                self.cards[mid].set_toggle(False)

    # ── message parsing ──────────────────────────────────────────────────

    def _handle(self, line):
        if line.startswith("CONNECTED"):
            pass
        elif line.startswith("STATUS "):
            self._parse_status(line[7:])
        elif line.startswith("INFO "):
            self._parse_info(line[5:])
        elif line.startswith("CONFIG "):
            self._parse_config(line[7:])

    def _parse_status(self, data):
        for pair in data.split(","):
            if "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            k = k.strip()
            on = v.strip() == "1"
            self.module_states[k] = on
            if k in self.cards:
                self.cards[k].set_toggle(on)

    def _parse_info(self, data):
        info = {}
        for pair in data.split(","):
            if "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            try:
                info[k.strip()] = float(v.strip())
            except ValueError:
                pass
        self.status_bar.update_info(
            hp=info.get("hp", 20), maxhp=info.get("maxhp", 20),
            food=int(info.get("food", 20)), armor=int(info.get("armor", 0)),
            fps=int(info.get("fps", 0)),
            x=info.get("x", 0), y=info.get("y", 0), z=info.get("z", 0),
        )

    def _parse_config(self, data):
        for pair in data.split(","):
            if "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            try:
                val = float(v.strip())
                self.config_values[k.strip()] = val
                for cat_mods in MODULES.values():
                    for mod in cat_mods:
                        if "slider" in mod and mod["slider"]["param"] == k.strip():
                            if mod["id"] in self.cards:
                                self.cards[mod["id"]].set_slider_value(val)
            except ValueError:
                pass

    # ── cleanup ──────────────────────────────────────────────────────────

    def _on_close(self):
        self.connected = False
        try:
            self.sock.close()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    def run(self):
        self.root.mainloop()


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = MCHelperApp()
    app.run()
