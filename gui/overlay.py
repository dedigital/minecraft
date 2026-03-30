"""Overlay GUI - Transparent overlay window for displaying module info."""

import tkinter as tk
import threading


class OverlayWindow:
    """Transparent overlay that displays module status and information."""

    def __init__(self):
        self.root = None
        self.canvas = None
        self.visible = True
        self.width = 300
        self.height = 600
        self.x_pos = 10
        self.y_pos = 100
        self._texts = []
        self._update_callback = None

    def create(self):
        """Create the overlay window."""
        self.root = tk.Tk()
        self.root.title("MC Helper")
        self.root.geometry(f"{self.width}x{self.height}+{self.x_pos}+{self.y_pos}")
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)

        try:
            self.root.attributes("-alpha", 0.85)
        except tk.TclError:
            pass

        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Title
        self._draw_title()

    def _draw_title(self):
        """Draw the title header."""
        self.canvas.create_text(
            self.width // 2, 20,
            text="MINECRAFT HELPER TOOL",
            fill="#00ff00",
            font=("Consolas", 14, "bold"),
            anchor="center",
        )
        self.canvas.create_line(
            10, 40, self.width - 10, 40,
            fill="#00ff00", width=2,
        )

    def update_display(self, module_statuses: list, extra_info: str = ""):
        """Update the overlay display with current module statuses."""
        if not self.canvas:
            return

        # Clear previous text (keep title)
        self.canvas.delete("dynamic")

        y_offset = 60

        # Module statuses
        for status in module_statuses:
            color = "#00ff00" if "ACIK" in status else "#ff4444"
            self.canvas.create_text(
                15, y_offset,
                text=status,
                fill=color,
                font=("Consolas", 10),
                anchor="w",
                tags="dynamic",
            )
            y_offset += 25

        # Separator
        y_offset += 10
        self.canvas.create_line(
            10, y_offset, self.width - 10, y_offset,
            fill="#444444", width=1, tags="dynamic",
        )
        y_offset += 15

        # Extra info (stats, alerts, etc.)
        if extra_info:
            for line in extra_info.split("\n"):
                color = "#ffffff"
                if "===" in line:
                    color = "#00ccff"
                elif "DIKKAT" in line:
                    color = "#ff0000"
                elif "Elmas" in line or "Hazine" in line:
                    color = "#00ffff"

                self.canvas.create_text(
                    15, y_offset,
                    text=line,
                    fill=color,
                    font=("Consolas", 9),
                    anchor="w",
                    tags="dynamic",
                )
                y_offset += 18

        # Footer
        self.canvas.create_text(
            self.width // 2, self.height - 20,
            text="F1: Menu | F6: Hepsini Kapat | ESC: Cikis",
            fill="#666666",
            font=("Consolas", 8),
            anchor="center",
            tags="dynamic",
        )

    def toggle_visibility(self):
        """Toggle overlay visibility."""
        if self.visible:
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.visible = not self.visible

    def destroy(self):
        """Destroy the overlay window."""
        if self.root:
            self.root.destroy()

    def run(self):
        """Start the overlay main loop."""
        if self.root:
            self.root.mainloop()
