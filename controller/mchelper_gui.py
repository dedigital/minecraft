#!/usr/bin/env python3
"""
MC Helper - Python GUI Controller v2.1
Fabric mod companion controller with module management and radar display.
Uses only tkinter (no external dependencies).
"""

import tkinter as tk
from tkinter import ttk
import socket
import threading
import math
import time

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
VERSION = "2.1"

# ---------------------------------------------------------------------------
# Module definitions
# ---------------------------------------------------------------------------
MODULES = [
    # Combat
    {"id": "killaura",      "name": "Kill Aura",       "cat": "combat",   "key": "R", "desc": "Yakindaki dusmanlari otomatik vur"},
    {"id": "antiknockback", "name": "Anti-Knockback",  "cat": "combat",   "key": "B", "desc": "Geri itilmeyi azalt"},
    {"id": "criticals",     "name": "Criticals",       "cat": "combat",   "key": "F", "desc": "Kill Aura ile kritik vurus"},

    # Movement
    {"id": "fly",        "name": "Fly",          "cat": "movement",  "key": "H", "desc": "Ucma modu"},
    {"id": "speed",      "name": "Speed",        "cat": "movement",  "key": "J", "desc": "Hizli hareket (1.8x)"},
    {"id": "autosprint", "name": "Auto-Sprint",  "cat": "movement",  "key": "K", "desc": "Otomatik kosma"},
    {"id": "nofall",     "name": "No Fall",      "cat": "movement",  "key": "N", "desc": "Dusme hasari yok"},
    {"id": "step",       "name": "Step Assist",  "cat": "movement",  "key": "V", "desc": "1.5 blok yuksekligine cik"},

    # Visual
    {"id": "fullbright", "name": "Fullbright",  "cat": "visual",    "key": "G", "desc": "Karanlikta gorme"},
    {"id": "radar",      "name": "Radar",       "cat": "visual",    "key": "U", "desc": "Yakindaki varliklari/cevherleri goster"},
    {"id": "antiblind",  "name": "Anti-Blind",  "cat": "visual",    "key": "O", "desc": "Korluk efektini kaldir"},
    {"id": "noweather",  "name": "No Weather",  "cat": "visual",    "key": "Y", "desc": "Yagmuru/firtinayi kaldir"},

    # Player
    {"id": "nohunger",  "name": "No Hunger",   "cat": "player",   "key": "P", "desc": "Aclik dolsun (singleplayer)"},
    {"id": "autotool",  "name": "Auto-Tool",   "cat": "player",   "key": "T", "desc": "En iyi aleti otomatik sec"},
    {"id": "fastbreak", "name": "Fast Break",  "cat": "player",   "key": "I", "desc": "2x hizli kazma"},
]

# Categories (tabs)
CATEGORIES = [
    {"id": "combat",    "name": "Combat",    "icon": "⚔"},
    {"id": "movement",  "name": "Movement",  "icon": "➤"},
    {"id": "visual",    "name": "Visual",    "icon": "◉"},
    {"id": "player",    "name": "Player",    "icon": "☺"},
    {"id": "radar_tab", "name": "Radar",     "icon": "⊕"},
]

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
COLORS = {
    "bg":           "#0e1621",
    "bg_card":      "#182533",
    "bg_card_on":   "#1a3a2f",
    "bg_header":    "#0a1018",
    "bg_status":    "#0a1018",
    "accent":       "#00ff88",
    "accent_dim":   "#007744",
    "text":         "#e8edf5",
    "text_dim":     "#6b7b8d",
    "text_off":     "#4a5568",
    "red":          "#ff4757",
    "blue":         "#54a0ff",
    "yellow":       "#ffd700",
    "toggle_on":    "#00ff88",
    "toggle_off":   "#2d3a4a",
    "tab_bg":       "#131d2a",
    "tab_sel":      "#1a3a2f",
    "border":       "#1e2d3d",
    "slider_bg":    "#1e2d3d",
    "slider_fill":  "#00ff88",
    "radar_bg":     "#0a1020",
    "radar_ring":   "#162030",
    "radar_grid":   "#1a2535",
}

# Radar entity colors
ENTITY_COLORS = {
    "hostile": "#ff4757",
    "passive": "#00ff88",
    "player":  "#54a0ff",
    "other":   "#6b7b8d",
}
ENTITY_SIZES = {
    "hostile": 6,
    "passive": 5,
    "player":  7,
    "other":   4,
}

# Radar ore colors
ORE_COLORS = {
    "diamond":  "#00d4ff",
    "iron":     "#e8edf5",
    "gold":     "#ffd700",
    "emerald":  "#00ff88",
    "lapis":    "#4169e1",
    "redstone": "#ff4757",
    "copper":   "#cd7f32",
    "coal":     "#555555",
    "ancient":  "#8b4513",
    "quartz":   "#ffffff",
    "chest":    "#fbbf24",
    "spawner":  "#a855f7",
}
ORE_SIZE = 4


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
class MCHelperGUI:
    """Main GUI controller for MC Helper fabric mod."""

    HOST = "127.0.0.1"
    PORT = 25567
    RECONNECT_INTERVAL = 5  # seconds

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"MC Helper v{VERSION}")
        self.root.geometry("500x750")
        self.root.minsize(480, 700)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        # State
        self.module_states = {m["id"]: False for m in MODULES}
        self.module_sliders = {}       # id -> (tk.DoubleVar, label_widget)
        self.module_card_widgets = {}  # id -> dict of widgets
        self.current_category = "combat"
        self.connected = False
        self.sock = None
        self.sock_lock = threading.Lock()
        self.running = True

        # Radar state
        self.player_yaw = 0.0
        self.entities = []
        self.ores = []
        self.show_entities = tk.BooleanVar(value=True)
        self.show_ores = tk.BooleanVar(value=True)

        # Build UI
        self._build_header()
        self._build_tabs()
        self._build_content_area()
        self._build_status_bar()

        # Show default category
        self._select_category("combat")

        # Start connection thread
        self._start_connection()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS["bg_header"], height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header, text=f"◆ MC Helper v{VERSION}",
            bg=COLORS["bg_header"], fg=COLORS["accent"],
            font=("Consolas", 14, "bold"),
        )
        title.pack(side="left", padx=14, pady=10)

        self.conn_label = tk.Label(
            header, text="● Disconnected",
            bg=COLORS["bg_header"], fg=COLORS["red"],
            font=("Consolas", 10),
        )
        self.conn_label.pack(side="right", padx=14)

    def _build_tabs(self):
        self.tab_frame = tk.Frame(self.root, bg=COLORS["bg"], height=40)
        self.tab_frame.pack(fill="x", padx=6, pady=(6, 0))
        self.tab_frame.pack_propagate(False)

        self.tab_buttons = {}
        for cat in CATEGORIES:
            btn = tk.Label(
                self.tab_frame,
                text=f" {cat['icon']} {cat['name']} ",
                bg=COLORS["tab_bg"], fg=COLORS["text_dim"],
                font=("Consolas", 10, "bold"),
                cursor="hand2",
                padx=6, pady=6,
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, cid=cat["id"]: self._select_category(cid))
            self.tab_buttons[cat["id"]] = btn

    def _build_content_area(self):
        """Create the scrollable content frame for module cards AND the radar frame."""
        # Container that holds either module cards or radar
        self.content_container = tk.Frame(self.root, bg=COLORS["bg"])
        self.content_container.pack(fill="both", expand=True, padx=6, pady=6)

        # --- Module cards (scrollable) ---
        self.cards_outer = tk.Frame(self.content_container, bg=COLORS["bg"])
        self.cards_canvas = tk.Canvas(
            self.cards_outer, bg=COLORS["bg"],
            highlightthickness=0, borderwidth=0,
        )
        self.cards_scroll = ttk.Scrollbar(
            self.cards_outer, orient="vertical",
            command=self.cards_canvas.yview,
        )
        self.cards_inner = tk.Frame(self.cards_canvas, bg=COLORS["bg"])

        self.cards_inner.bind(
            "<Configure>",
            lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all")),
        )
        self.cards_canvas.create_window((0, 0), window=self.cards_inner, anchor="nw")
        self.cards_canvas.configure(yscrollcommand=self.cards_scroll.set)

        self.cards_canvas.pack(side="left", fill="both", expand=True)
        self.cards_scroll.pack(side="right", fill="y")

        # Mouse-wheel scrolling
        self.cards_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.cards_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )
        self.cards_canvas.bind_all(
            "<Button-4>",
            lambda e: self.cards_canvas.yview_scroll(-1, "units"),
        )
        self.cards_canvas.bind_all(
            "<Button-5>",
            lambda e: self.cards_canvas.yview_scroll(1, "units"),
        )

        # --- Radar frame ---
        self.radar_frame = tk.Frame(self.content_container, bg=COLORS["bg"])
        self._build_radar_widget()

    def _build_radar_widget(self):
        """Build the radar display inside self.radar_frame."""
        self.radar_size = 300

        # Title
        tk.Label(
            self.radar_frame, text="⊕ RADAR DISPLAY",
            bg=COLORS["bg"], fg=COLORS["accent"],
            font=("Consolas", 12, "bold"),
        ).pack(pady=(4, 6))

        # Canvas with border
        canvas_frame = tk.Frame(self.radar_frame, bg=COLORS["border"], padx=1, pady=1)
        canvas_frame.pack()
        self.radar_canvas = tk.Canvas(
            canvas_frame,
            width=self.radar_size, height=self.radar_size,
            bg=COLORS["radar_bg"], highlightthickness=0,
        )
        self.radar_canvas.pack()

        # Controls row
        ctrl_frame = tk.Frame(self.radar_frame, bg=COLORS["bg"])
        ctrl_frame.pack(pady=(8, 4))

        ent_cb = tk.Checkbutton(
            ctrl_frame, text="Entities", variable=self.show_entities,
            bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["bg_card"],
            activebackground=COLORS["bg"], activeforeground=COLORS["text"],
            font=("Consolas", 10),
            command=self._on_radar_toggle,
        )
        ent_cb.pack(side="left", padx=12)

        ore_cb = tk.Checkbutton(
            ctrl_frame, text="Ores", variable=self.show_ores,
            bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["bg_card"],
            activebackground=COLORS["bg"], activeforeground=COLORS["text"],
            font=("Consolas", 10),
            command=self._on_radar_toggle,
        )
        ore_cb.pack(side="left", padx=12)

        # Counts label
        self.radar_counts_label = tk.Label(
            self.radar_frame, text="Entities: 0 | Ores: 0",
            bg=COLORS["bg"], fg=COLORS["text_dim"],
            font=("Consolas", 10),
        )
        self.radar_counts_label.pack(pady=(2, 6))

        # Legend
        self._build_radar_legend()

        # Initial draw
        self.draw_radar()

    def _build_radar_legend(self):
        """Build a compact color legend below the radar."""
        legend_outer = tk.Frame(self.radar_frame, bg=COLORS["bg"])
        legend_outer.pack(pady=(2, 4), fill="x")

        # Entity legend
        ent_title = tk.Label(
            legend_outer, text="Entities:",
            bg=COLORS["bg"], fg=COLORS["text_dim"],
            font=("Consolas", 9, "bold"),
        )
        ent_title.grid(row=0, column=0, sticky="w", padx=(10, 4))
        col = 1
        for etype, color in ENTITY_COLORS.items():
            dot = tk.Canvas(legend_outer, width=10, height=10,
                            bg=COLORS["bg"], highlightthickness=0)
            dot.create_oval(1, 1, 9, 9, fill=color, outline="")
            dot.grid(row=0, column=col, padx=(4, 0))
            col += 1
            lbl = tk.Label(
                legend_outer, text=etype,
                bg=COLORS["bg"], fg=COLORS["text_dim"],
                font=("Consolas", 8),
            )
            lbl.grid(row=0, column=col, padx=(0, 6))
            col += 1

        # Ore legend (two rows for space)
        ore_items = list(ORE_COLORS.items())
        half = (len(ore_items) + 1) // 2
        for row_idx, items in enumerate([ore_items[:half], ore_items[half:]]):
            ore_label = tk.Label(
                legend_outer,
                text="Ores:" if row_idx == 0 else "",
                bg=COLORS["bg"], fg=COLORS["text_dim"],
                font=("Consolas", 9, "bold"),
            )
            ore_label.grid(row=1 + row_idx, column=0, sticky="w", padx=(10, 4))
            c = 1
            for otype, color in items:
                dot = tk.Canvas(legend_outer, width=10, height=10,
                                bg=COLORS["bg"], highlightthickness=0)
                dot.create_oval(1, 1, 9, 9, fill=color, outline="")
                dot.grid(row=1 + row_idx, column=c, padx=(4, 0))
                c += 1
                lbl = tk.Label(
                    legend_outer, text=otype,
                    bg=COLORS["bg"], fg=COLORS["text_dim"],
                    font=("Consolas", 8),
                )
                lbl.grid(row=1 + row_idx, column=c, padx=(0, 4))
                c += 1

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=COLORS["bg_status"], height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status_label = tk.Label(
            bar, text="Ready",
            bg=COLORS["bg_status"], fg=COLORS["text_dim"],
            font=("Consolas", 9),
        )
        self.status_label.pack(side="left", padx=10)

        self.ping_label = tk.Label(
            bar, text="",
            bg=COLORS["bg_status"], fg=COLORS["text_dim"],
            font=("Consolas", 9),
        )
        self.ping_label.pack(side="right", padx=10)

    # ------------------------------------------------------------------
    # Tab / Category selection
    # ------------------------------------------------------------------
    def _select_category(self, cat_id):
        self.current_category = cat_id

        # Update tab visuals
        for cid, btn in self.tab_buttons.items():
            if cid == cat_id:
                btn.configure(bg=COLORS["tab_sel"], fg=COLORS["accent"])
            else:
                btn.configure(bg=COLORS["tab_bg"], fg=COLORS["text_dim"])

        if cat_id == "radar_tab":
            self.cards_outer.pack_forget()
            self.radar_frame.pack(fill="both", expand=True)
            self.draw_radar()
        else:
            self.radar_frame.pack_forget()
            self.cards_outer.pack(fill="both", expand=True)
            self._populate_cards(cat_id)

    def _populate_cards(self, cat_id):
        """Populate module cards for the given category."""
        for w in self.cards_inner.winfo_children():
            w.destroy()
        self.module_card_widgets.clear()
        self.module_sliders.clear()

        mods = [m for m in MODULES if m["cat"] == cat_id]
        for m in mods:
            self._create_module_card(m)

    def _create_module_card(self, mod):
        mid = mod["id"]
        is_on = self.module_states.get(mid, False)
        card_bg = COLORS["bg_card_on"] if is_on else COLORS["bg_card"]

        card = tk.Frame(
            self.cards_inner, bg=card_bg,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        card.pack(fill="x", padx=4, pady=3)

        # Top row: name + key + toggle
        top = tk.Frame(card, bg=card_bg)
        top.pack(fill="x", padx=10, pady=(8, 2))

        name_lbl = tk.Label(
            top, text=mod["name"],
            bg=card_bg, fg=COLORS["accent"] if is_on else COLORS["text"],
            font=("Consolas", 12, "bold"),
        )
        name_lbl.pack(side="left")

        key_lbl = tk.Label(
            top, text=f"[{mod['key']}]",
            bg=card_bg, fg=COLORS["text_dim"],
            font=("Consolas", 9),
        )
        key_lbl.pack(side="left", padx=(8, 0))

        # Toggle button
        toggle_text = " ON " if is_on else " OFF "
        toggle_fg = COLORS["bg"] if is_on else COLORS["text_dim"]
        toggle_bg = COLORS["toggle_on"] if is_on else COLORS["toggle_off"]
        toggle_btn = tk.Label(
            top, text=toggle_text,
            bg=toggle_bg, fg=toggle_fg,
            font=("Consolas", 9, "bold"),
            cursor="hand2", padx=6, pady=1,
        )
        toggle_btn.pack(side="right")
        toggle_btn.bind("<Button-1>", lambda e, m=mid: self._toggle_module(m))

        # Description
        desc_lbl = tk.Label(
            card, text=mod["desc"],
            bg=card_bg, fg=COLORS["text_dim"],
            font=("Consolas", 9),
            anchor="w",
        )
        desc_lbl.pack(fill="x", padx=10, pady=(0, 2))

        # Slider (for modules that support intensity)
        slider_mods = {"killaura", "reach", "speed", "fly", "fastbreak"}
        if mid in slider_mods:
            self._create_slider(card, mid, card_bg)

        # Padding at bottom
        tk.Frame(card, bg=card_bg, height=6).pack()

        # Store references
        self.module_card_widgets[mid] = {
            "card": card,
            "name": name_lbl,
            "toggle": toggle_btn,
            "desc": desc_lbl,
            "top": top,
        }

    def _create_slider(self, parent, mid, card_bg):
        """Create a value slider for a module."""
        frame = tk.Frame(parent, bg=card_bg)
        frame.pack(fill="x", padx=10, pady=(2, 2))

        lbl = tk.Label(
            frame, text="Value:",
            bg=card_bg, fg=COLORS["text_dim"],
            font=("Consolas", 9),
        )
        lbl.pack(side="left")

        var = tk.DoubleVar(value=1.0)
        slider = tk.Scale(
            frame,
            from_=0.1, to=10.0, resolution=0.1,
            orient="horizontal", variable=var,
            bg=COLORS["slider_bg"], fg=COLORS["text"],
            troughcolor=COLORS["slider_bg"],
            highlightthickness=0, borderwidth=0,
            font=("Consolas", 8),
            activebackground=COLORS["slider_fill"],
            length=200,
            command=lambda val, m=mid: self._on_slider_change(m, val),
        )
        slider.pack(side="left", padx=(6, 0), fill="x", expand=True)

        val_lbl = tk.Label(
            frame, text="1.0",
            bg=card_bg, fg=COLORS["accent"],
            font=("Consolas", 9, "bold"), width=5,
        )
        val_lbl.pack(side="right")

        self.module_sliders[mid] = (var, val_lbl)

    # ------------------------------------------------------------------
    # Module actions
    # ------------------------------------------------------------------
    def _toggle_module(self, mid):
        new_state = not self.module_states.get(mid, False)
        self.module_states[mid] = new_state
        self._send_command(f"TOGGLE {mid} {'ON' if new_state else 'OFF'}")
        self._set_status(f"{mid} {'enabled' if new_state else 'disabled'}")

        # Re-render current category to reflect state
        if self.current_category != "radar_tab":
            self._populate_cards(self.current_category)

    def _on_slider_change(self, mid, val):
        val = float(val)
        if mid in self.module_sliders:
            _, val_lbl = self.module_sliders[mid]
            val_lbl.configure(text=f"{val:.1f}")
        self._send_command(f"SET {mid} {val:.1f}")

    def _on_radar_toggle(self):
        """Called when entities/ores checkboxes change."""
        self.draw_radar()

    # ------------------------------------------------------------------
    # Radar drawing
    # ------------------------------------------------------------------
    def world_to_radar(self, rel_x, rel_z, yaw, radar_cx, radar_cy, scale=4.0):
        """Convert relative world coords to radar canvas coords."""
        angle = math.radians(-yaw)
        rx = rel_x * math.cos(angle) - rel_z * math.sin(angle)
        ry = rel_x * math.sin(angle) + rel_z * math.cos(angle)

        sx = radar_cx + rx * scale
        sy = radar_cy - ry * scale  # negative because canvas Y is inverted
        return sx, sy

    def draw_radar(self):
        """Redraw the entire radar canvas."""
        c = self.radar_canvas
        c.delete("all")

        size = self.radar_size
        cx = size / 2
        cy = size / 2
        radius = size / 2 - 10
        scale = radius / 36  # 36 blocks fits in the radius

        # Clip region: draw a dark circle
        c.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            fill=COLORS["radar_bg"], outline=COLORS["border"], width=1,
        )

        # Range rings (every 8 blocks)
        for dist_blocks in (8, 16, 24, 32):
            r = dist_blocks * scale
            if r > radius:
                continue
            c.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=COLORS["radar_ring"], width=1,
            )
            # Distance label
            c.create_text(
                cx + 3, cy - r + 8,
                text=f"{dist_blocks}b", fill=COLORS["text_dim"],
                font=("Consolas", 7), anchor="w",
            )

        # Cross-hairs
        c.create_line(cx - radius, cy, cx + radius, cy,
                       fill=COLORS["radar_grid"], width=1)
        c.create_line(cx, cy - radius, cx, cy + radius,
                       fill=COLORS["radar_grid"], width=1)

        # Cardinal directions (rotated by player yaw)
        for label, angle_offset in [("N", 0), ("E", 90), ("S", 180), ("W", 270)]:
            raw_angle = math.radians(angle_offset - self.player_yaw)
            dx = math.sin(raw_angle) * (radius + 1)
            dy = -math.cos(raw_angle) * (radius + 1)
            nx = cx + dx
            ny = cy + dy
            # Clip to visible area
            if 5 <= nx <= size - 5 and 5 <= ny <= size - 5:
                fg = COLORS["accent"] if label == "N" else COLORS["text_dim"]
                c.create_text(nx, ny, text=label, fill=fg,
                              font=("Consolas", 9, "bold"))

        # Player arrow at center (pointing up = forward)
        arrow_len = 8
        c.create_polygon(
            cx, cy - arrow_len,
            cx - 5, cy + 4,
            cx + 5, cy + 4,
            fill=COLORS["accent"], outline="",
        )

        # Draw entities
        if self.show_entities.get():
            for ent in self.entities:
                sx, sy = self.world_to_radar(
                    ent["x"], ent["z"], self.player_yaw, cx, cy, scale)
                # Clip: only draw inside circle
                dist = math.sqrt((sx - cx) ** 2 + (sy - cy) ** 2)
                if dist > radius - 2:
                    continue
                color = ENTITY_COLORS.get(ent["type"], ENTITY_COLORS["other"])
                sz = ENTITY_SIZES.get(ent["type"], ENTITY_SIZES["other"])
                half = sz / 2
                c.create_oval(
                    sx - half, sy - half, sx + half, sy + half,
                    fill=color, outline="",
                )

        # Draw ores
        if self.show_ores.get():
            for ore in self.ores:
                sx, sy = self.world_to_radar(
                    ore["x"], ore["z"], self.player_yaw, cx, cy, scale)
                dist = math.sqrt((sx - cx) ** 2 + (sy - cy) ** 2)
                if dist > radius - 2:
                    continue
                color = ORE_COLORS.get(ore["type"], "#888888")
                half = ORE_SIZE / 2
                c.create_rectangle(
                    sx - half, sy - half, sx + half, sy + half,
                    fill=color, outline="",
                )

        # Update counts
        ent_count = len(self.entities)
        ore_count = len(self.ores)
        self.radar_counts_label.configure(
            text=f"Entities: {ent_count} | Ores: {ore_count}")

    # ------------------------------------------------------------------
    # Networking
    # ------------------------------------------------------------------
    def _start_connection(self):
        t = threading.Thread(target=self._connection_loop, daemon=True)
        t.start()

    def _connection_loop(self):
        """Auto-reconnect loop."""
        while self.running:
            try:
                self._set_status("Connecting...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.HOST, self.PORT))
                sock.settimeout(None)

                with self.sock_lock:
                    self.sock = sock
                    self.connected = True

                self.root.after(0, self._update_connection_ui, True)
                self._set_status("Connected")

                # Send version handshake
                self._send_command(f"HELLO v{VERSION}")

                # Read loop
                buf = ""
                while self.running:
                    data = sock.recv(4096)
                    if not data:
                        break
                    buf += data.decode("utf-8", errors="replace")
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        line = line.strip()
                        if line:
                            self._handle_message(line)

            except (ConnectionRefusedError, ConnectionResetError, OSError):
                pass
            finally:
                with self.sock_lock:
                    self.connected = False
                    if self.sock:
                        try:
                            self.sock.close()
                        except OSError:
                            pass
                        self.sock = None

                self.root.after(0, self._update_connection_ui, False)
                self._set_status("Disconnected - retrying...")

            # Wait before reconnect
            for _ in range(self.RECONNECT_INTERVAL * 10):
                if not self.running:
                    return
                time.sleep(0.1)

    def _send_command(self, cmd):
        """Send a command string to the mod."""
        with self.sock_lock:
            if self.connected and self.sock:
                try:
                    self.sock.sendall((cmd + "\n").encode("utf-8"))
                except OSError:
                    pass

    def _handle_message(self, line):
        """Parse incoming message from the mod."""
        if line.startswith("STATE "):
            # Parse: STATE killaura=ON,fly=OFF,...
            for pair in line[6:].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if k in self.module_states:
                        self.module_states[k] = (v.upper() == "ON")
            # Refresh cards
            if self.current_category != "radar_tab":
                self.root.after(0, self._populate_cards, self.current_category)

        elif line.startswith("PING "):
            # Parse: PING 42ms
            ping_text = line[5:].strip()
            self.root.after(0, self.ping_label.configure, {"text": f"Ping: {ping_text}"})

        elif line.startswith("ROTATION "):
            # Parse: ROTATION yaw=90.5
            for pair in line[9:].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    if k.strip() == "yaw":
                        self.player_yaw = float(v.strip())

        elif line.startswith("ENTITIES "):
            # Parse: ENTITIES hostile,-5.0,0.0,10.0;passive,8.0,-2.0,3.0;
            self.entities = []
            for entry in line[9:].split(";"):
                parts = entry.strip().split(",")
                if len(parts) >= 4:
                    self.entities.append({
                        "type": parts[0],
                        "x": float(parts[1]),
                        "y": float(parts[2]),
                        "z": float(parts[3]),
                    })
            self.root.after(0, self.draw_radar)

        elif line.startswith("ORES "):
            # Parse: ORES diamond,-3,5,-8;iron,2,0,5;
            self.ores = []
            for entry in line[5:].split(";"):
                parts = entry.strip().split(",")
                if len(parts) >= 4:
                    self.ores.append({
                        "type": parts[0],
                        "x": float(parts[1]) if '.' in parts[1] else int(parts[1]),
                        "y": float(parts[2]) if '.' in parts[2] else int(parts[2]),
                        "z": float(parts[3]) if '.' in parts[3] else int(parts[3]),
                    })
            self.root.after(0, self.draw_radar)

        elif line.startswith("MSG "):
            # Generic status message from mod
            msg = line[4:].strip()
            self._set_status(msg)

    # ------------------------------------------------------------------
    # UI Helpers
    # ------------------------------------------------------------------
    def _update_connection_ui(self, is_connected):
        if is_connected:
            self.conn_label.configure(text="● Connected", fg=COLORS["accent"])
        else:
            self.conn_label.configure(text="● Disconnected", fg=COLORS["red"])
            self.ping_label.configure(text="")

    def _set_status(self, text):
        self.root.after(0, self.status_label.configure, {"text": text})

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def _on_close(self):
        self.running = False
        self._send_command("BYE")
        with self.sock_lock:
            if self.sock:
                try:
                    self.sock.close()
                except OSError:
                    pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = MCHelperGUI()
    app.run()
