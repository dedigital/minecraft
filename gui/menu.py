"""Menu GUI - Main settings and control menu."""

import tkinter as tk
from tkinter import ttk


class MenuWindow:
    """Settings menu window for configuring modules."""

    def __init__(self, modules: dict, on_close=None):
        self.modules = modules
        self.on_close = on_close
        self.root = None
        self.visible = False

    def create(self):
        """Create the menu window."""
        self.root = tk.Toplevel()
        self.root.title("MC Helper - Ayarlar")
        self.root.geometry("450x550")
        self.root.configure(bg="#1a1a2e")
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.toggle)
        self.root.withdraw()

        self._build_ui()

    def _build_ui(self):
        """Build the menu UI."""
        # Title Frame
        title_frame = tk.Frame(self.root, bg="#16213e", pady=10)
        title_frame.pack(fill=tk.X)

        tk.Label(
            title_frame,
            text="MINECRAFT HELPER TOOL",
            font=("Consolas", 16, "bold"),
            fg="#00ff41",
            bg="#16213e",
        ).pack()

        tk.Label(
            title_frame,
            text="v1.0 - Yarisma Edition",
            font=("Consolas", 10),
            fg="#888888",
            bg="#16213e",
        ).pack()

        # Notebook for tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#1a1a2e")
        style.configure("TNotebook.Tab", background="#16213e", foreground="white",
                        padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#0f3460")])

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Modules tab
        modules_frame = tk.Frame(notebook, bg="#1a1a2e")
        notebook.add(modules_frame, text="Moduller")
        self._build_modules_tab(modules_frame)

        # X-Ray settings tab
        xray_frame = tk.Frame(notebook, bg="#1a1a2e")
        notebook.add(xray_frame, text="X-Ray")
        self._build_xray_tab(xray_frame)

        # Auto-Mine settings tab
        mine_frame = tk.Frame(notebook, bg="#1a1a2e")
        notebook.add(mine_frame, text="Auto-Mine")
        self._build_mine_tab(mine_frame)

        # ESP settings tab
        esp_frame = tk.Frame(notebook, bg="#1a1a2e")
        notebook.add(esp_frame, text="ESP")
        self._build_esp_tab(esp_frame)

        # Auto-Fish settings tab
        fish_frame = tk.Frame(notebook, bg="#1a1a2e")
        notebook.add(fish_frame, text="Auto-Fish")
        self._build_fish_tab(fish_frame)

    def _build_modules_tab(self, parent):
        """Build the modules overview tab."""
        tk.Label(
            parent, text="Modul Kontrol Paneli",
            font=("Consolas", 12, "bold"), fg="#00ccff", bg="#1a1a2e",
        ).pack(pady=10)

        for name, module in self.modules.items():
            frame = tk.Frame(parent, bg="#16213e", pady=5, padx=10)
            frame.pack(fill=tk.X, padx=10, pady=3)

            tk.Label(
                frame, text=f"{module.name}",
                font=("Consolas", 11, "bold"), fg="white", bg="#16213e",
                width=15, anchor="w",
            ).pack(side=tk.LEFT)

            tk.Label(
                frame, text=f"[{module.hotkey}]",
                font=("Consolas", 9), fg="#888888", bg="#16213e",
            ).pack(side=tk.LEFT, padx=5)

            btn = tk.Button(
                frame,
                text="ACIK" if module.enabled else "KAPALI",
                font=("Consolas", 9, "bold"),
                fg="white",
                bg="#00aa00" if module.enabled else "#aa0000",
                activebackground="#00cc00" if module.enabled else "#cc0000",
                width=8,
                relief=tk.FLAT,
                command=lambda m=module: self._toggle_module(m),
            )
            btn.pack(side=tk.RIGHT)

        # Kill all button
        tk.Button(
            parent,
            text="HEPSINI KAPAT [F6]",
            font=("Consolas", 11, "bold"),
            fg="white", bg="#cc0000",
            activebackground="#ff0000",
            relief=tk.FLAT,
            command=self._disable_all,
            pady=8,
        ).pack(fill=tk.X, padx=10, pady=15)

    def _build_xray_tab(self, parent):
        """Build X-Ray settings tab."""
        tk.Label(
            parent, text="X-Ray Ayarlari",
            font=("Consolas", 12, "bold"), fg="#00ffff", bg="#1a1a2e",
        ).pack(pady=10)

        settings = [
            ("Tarama Yaricapi", "scan_radius", 1, 32),
            ("Min Oncelik (1=Elmas, 6=Hepsi)", "min_priority", 1, 6),
        ]

        xray = self.modules.get("xray")
        if xray:
            for label, attr, min_val, max_val in settings:
                frame = tk.Frame(parent, bg="#1a1a2e")
                frame.pack(fill=tk.X, padx=15, pady=5)

                tk.Label(
                    frame, text=label,
                    font=("Consolas", 10), fg="white", bg="#1a1a2e",
                ).pack(anchor="w")

                scale = tk.Scale(
                    frame, from_=min_val, to=max_val,
                    orient=tk.HORIZONTAL, bg="#16213e", fg="white",
                    highlightthickness=0, troughcolor="#0f3460",
                    font=("Consolas", 9),
                )
                scale.set(getattr(xray, attr))
                scale.pack(fill=tk.X)

            # Checkboxes
            for label, attr in [("Cevherleri Goster", "show_ores"), ("Ozel Bloklari Goster", "show_special")]:
                var = tk.BooleanVar(value=getattr(xray, attr))
                cb = tk.Checkbutton(
                    parent, text=label, variable=var,
                    font=("Consolas", 10), fg="white", bg="#1a1a2e",
                    selectcolor="#16213e", activebackground="#1a1a2e",
                    activeforeground="white",
                )
                cb.pack(anchor="w", padx=15, pady=3)

    def _build_mine_tab(self, parent):
        """Build Auto-Mine settings tab."""
        tk.Label(
            parent, text="Auto-Mine Ayarlari",
            font=("Consolas", 12, "bold"), fg="#ffaa00", bg="#1a1a2e",
        ).pack(pady=10)

        auto_mine = self.modules.get("auto_mine")
        if auto_mine:
            # Pattern selection
            tk.Label(
                parent, text="Kazi Deseni:",
                font=("Consolas", 10), fg="white", bg="#1a1a2e",
            ).pack(anchor="w", padx=15, pady=(10, 0))

            patterns = [
                ("Strip Mine - Duz kazi", "strip"),
                ("Branch Mine - Elmas optimizasyonu", "branch"),
                ("Merdiven - Asagi kazi", "staircase"),
            ]

            pattern_var = tk.StringVar(value=auto_mine.pattern_name)
            for label, value in patterns:
                rb = tk.Radiobutton(
                    parent, text=label, variable=pattern_var, value=value,
                    font=("Consolas", 10), fg="white", bg="#1a1a2e",
                    selectcolor="#16213e", activebackground="#1a1a2e",
                    activeforeground="white",
                    command=lambda v=value: auto_mine.set_pattern(v),
                )
                rb.pack(anchor="w", padx=25, pady=2)

            # Speed slider
            tk.Label(
                parent, text="Kazi Hizi (saniye/blok):",
                font=("Consolas", 10), fg="white", bg="#1a1a2e",
            ).pack(anchor="w", padx=15, pady=(15, 0))

            speed_scale = tk.Scale(
                parent, from_=0.1, to=2.0, resolution=0.1,
                orient=tk.HORIZONTAL, bg="#16213e", fg="white",
                highlightthickness=0, troughcolor="#0f3460",
                font=("Consolas", 9),
            )
            speed_scale.set(auto_mine.mining_speed)
            speed_scale.pack(fill=tk.X, padx=15)

            # Checkboxes
            for label, attr in [
                ("Otomatik Mesale", "auto_torch"),
                ("Otomatik Yemek", "auto_eat"),
                ("Lavdan Kacin", "avoid_lava"),
            ]:
                var = tk.BooleanVar(value=getattr(auto_mine, attr))
                cb = tk.Checkbutton(
                    parent, text=label, variable=var,
                    font=("Consolas", 10), fg="white", bg="#1a1a2e",
                    selectcolor="#16213e", activebackground="#1a1a2e",
                    activeforeground="white",
                )
                cb.pack(anchor="w", padx=15, pady=3)

    def _build_esp_tab(self, parent):
        """Build ESP settings tab."""
        tk.Label(
            parent, text="ESP Ayarlari",
            font=("Consolas", 12, "bold"), fg="#ff00ff", bg="#1a1a2e",
        ).pack(pady=10)

        esp = self.modules.get("esp")
        if esp:
            # Entity filter checkboxes
            tk.Label(
                parent, text="Entity Filtreleri:",
                font=("Consolas", 10), fg="white", bg="#1a1a2e",
            ).pack(anchor="w", padx=15, pady=(10, 0))

            filters = [
                ("Dusman Moblar", "show_hostile"),
                ("Pasif Moblar", "show_passive"),
                ("Oyuncular", "show_players"),
                ("Boss Moblar", "show_boss"),
                ("Esyalar", "show_items"),
            ]

            for label, attr in filters:
                var = tk.BooleanVar(value=getattr(esp, attr))
                cb = tk.Checkbutton(
                    parent, text=label, variable=var,
                    font=("Consolas", 10), fg="white", bg="#1a1a2e",
                    selectcolor="#16213e", activebackground="#1a1a2e",
                    activeforeground="white",
                )
                cb.pack(anchor="w", padx=25, pady=2)

            # Display options
            tk.Label(
                parent, text="Gosterim Ayarlari:",
                font=("Consolas", 10), fg="white", bg="#1a1a2e",
            ).pack(anchor="w", padx=15, pady=(15, 0))

            display_opts = [
                ("Can Cubugu", "show_health_bars"),
                ("Mesafe", "show_distance"),
                ("Tracer Cizgileri", "show_tracers"),
                ("Dusman Uyarisi", "alert_on_hostile"),
            ]

            for label, attr in display_opts:
                var = tk.BooleanVar(value=getattr(esp, attr))
                cb = tk.Checkbutton(
                    parent, text=label, variable=var,
                    font=("Consolas", 10), fg="white", bg="#1a1a2e",
                    selectcolor="#16213e", activebackground="#1a1a2e",
                    activeforeground="white",
                )
                cb.pack(anchor="w", padx=25, pady=2)

            # Scan range
            tk.Label(
                parent, text="Tarama Mesafesi:",
                font=("Consolas", 10), fg="white", bg="#1a1a2e",
            ).pack(anchor="w", padx=15, pady=(15, 0))

            range_scale = tk.Scale(
                parent, from_=16, to=128,
                orient=tk.HORIZONTAL, bg="#16213e", fg="white",
                highlightthickness=0, troughcolor="#0f3460",
                font=("Consolas", 9),
            )
            range_scale.set(esp.scan_range)
            range_scale.pack(fill=tk.X, padx=15)

    def _build_fish_tab(self, parent):
        """Build Auto-Fish settings tab."""
        tk.Label(
            parent, text="Auto-Fish Ayarlari",
            font=("Consolas", 12, "bold"), fg="#00ffaa", bg="#1a1a2e",
        ).pack(pady=10)

        fish = self.modules.get("auto_fish")
        if fish:
            # Enchantment sliders
            tk.Label(
                parent, text="Luck of the Sea Seviyesi:",
                font=("Consolas", 10), fg="white", bg="#1a1a2e",
            ).pack(anchor="w", padx=15, pady=(10, 0))

            luck_scale = tk.Scale(
                parent, from_=0, to=3,
                orient=tk.HORIZONTAL, bg="#16213e", fg="white",
                highlightthickness=0, troughcolor="#0f3460",
                font=("Consolas", 9),
            )
            luck_scale.set(fish.luck_of_the_sea)
            luck_scale.pack(fill=tk.X, padx=15)

            tk.Label(
                parent, text="Lure Seviyesi:",
                font=("Consolas", 10), fg="white", bg="#1a1a2e",
            ).pack(anchor="w", padx=15, pady=(10, 0))

            lure_scale = tk.Scale(
                parent, from_=0, to=3,
                orient=tk.HORIZONTAL, bg="#16213e", fg="white",
                highlightthickness=0, troughcolor="#0f3460",
                font=("Consolas", 9),
            )
            lure_scale.set(fish.lure_level)
            lure_scale.pack(fill=tk.X, padx=15)

            # Checkboxes
            for label, attr in [
                ("Otomatik Tekrar At", "auto_recast"),
                ("Yagmur Bonusu", "rain_bonus"),
            ]:
                var = tk.BooleanVar(value=getattr(fish, attr))
                cb = tk.Checkbutton(
                    parent, text=label, variable=var,
                    font=("Consolas", 10), fg="white", bg="#1a1a2e",
                    selectcolor="#16213e", activebackground="#1a1a2e",
                    activeforeground="white",
                )
                cb.pack(anchor="w", padx=15, pady=3)

    def _toggle_module(self, module):
        """Toggle a module on/off and refresh UI."""
        module.toggle()
        self._refresh()

    def _disable_all(self):
        """Disable all modules."""
        for module in self.modules.values():
            if module.enabled:
                module.disable()
        self._refresh()

    def _refresh(self):
        """Refresh the menu UI."""
        if self.root and self.visible:
            # Rebuild modules tab
            for widget in self.root.winfo_children():
                widget.destroy()
            self._build_ui()

    def toggle(self):
        """Toggle menu visibility."""
        if self.visible:
            self.root.withdraw()
            self.visible = False
        else:
            self.root.deiconify()
            self.visible = True

    def destroy(self):
        """Destroy the menu window."""
        if self.root:
            self.root.destroy()
