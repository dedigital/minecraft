"""
Minecraft Helper Tool - Main Entry Point
=========================================
Arkadaslar arasi yarisma icin hazirlanan single-player Minecraft helper tool.

Kisayollar:
    F1  - Menu ac/kapa
    F2  - X-Ray toggle
    F3  - Auto-Mine toggle
    F4  - ESP toggle
    F5  - Auto-Fish toggle
    F6  - Hepsini kapat
    ESC - Programdan cik
"""

import sys
import threading
import time

from modules.xray import XRayModule
from modules.auto_mine import AutoMineModule
from modules.esp import ESPModule
from modules.auto_fish import AutoFishModule


BANNER = r"""
  __  __ _                            __ _     _   _      _
 |  \/  (_)_ __   ___  ___ _ __ __ _ / _| |_  | | | | ___| |_ __   ___ _ __
 | |\/| | | '_ \ / _ \/ __| '__/ _` | |_| __| | |_| |/ _ \ | '_ \ / _ \ '__|
 | |  | | | | | |  __/ (__| | | (_| |  _| |_  |  _  |  __/ | |_) |  __/ |
 |_|  |_|_|_| |_|\___|\___|_|  \__,_|_|  \__| |_| |_|\___|_| .__/ \___|_|
                                                              |_|
                    v1.0 - Yarisma Edition
"""

HELP_TEXT = """
Kisayollar:
  F1  - Ayarlar menusunu ac/kapa
  F2  - X-Ray Vision (cevher goruntuleyici)
  F3  - Auto-Mine (otomatik kazi)
  F4  - ESP (mob takip)
  F5  - Auto-Fish (otomatik balik)
  F6  - Tum modulleri kapat
  ESC - Programdan cik

Komutlar (konsola yazin):
  status  - Tum modullerin durumunu goster
  xray    - X-Ray istatistikleri
  mine    - Auto-Mine istatistikleri
  esp     - ESP istatistikleri
  fish    - Auto-Fish istatistikleri
  help    - Bu yardim mesajini goster
  quit    - Programdan cik
"""


class MinecraftHelper:
    """Main application controller."""

    def __init__(self):
        self.modules = {}
        self.running = False
        self.gui_mode = False
        self._setup_modules()

    def _setup_modules(self):
        """Initialize all modules."""
        self.modules["xray"] = XRayModule()
        self.modules["auto_mine"] = AutoMineModule()
        self.modules["esp"] = ESPModule()
        self.modules["auto_fish"] = AutoFishModule()

    def start(self):
        """Start the helper tool."""
        self.running = True
        print(BANNER)
        print("Minecraft Helper Tool baslatildi!")
        print("'help' yazarak komutlari gorebilirsiniz.\n")

        # Try to start GUI mode
        try:
            self._start_gui()
        except Exception:
            print("[!] GUI baslatilamadi, konsol modunda devam ediliyor...")
            self._start_console()

    def _start_gui(self):
        """Start with GUI overlay."""
        from gui.overlay import OverlayWindow
        from gui.menu import MenuWindow

        self.gui_mode = True

        # Start console input thread
        console_thread = threading.Thread(target=self._console_loop, daemon=True)
        console_thread.start()

        # Start keyboard listener thread
        keyboard_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        keyboard_thread.start()

        # Start overlay update thread
        update_thread = threading.Thread(target=self._update_loop, daemon=True)
        update_thread.start()

        # Create and run overlay (must be on main thread for tkinter)
        self.overlay = OverlayWindow()
        self.overlay.create()

        self.menu = MenuWindow(self.modules)
        self.menu.create()

        # Start tkinter main loop
        self.overlay.run()

    def _start_console(self):
        """Start in console-only mode."""
        self._console_loop()

    def _keyboard_listener(self):
        """Listen for hotkey presses."""
        try:
            import keyboard

            keyboard.on_press_key("f1", lambda _: self._on_f1())
            keyboard.on_press_key("f2", lambda _: self.modules["xray"].toggle())
            keyboard.on_press_key("f3", lambda _: self.modules["auto_mine"].toggle())
            keyboard.on_press_key("f4", lambda _: self.modules["esp"].toggle())
            keyboard.on_press_key("f5", lambda _: self.modules["auto_fish"].toggle())
            keyboard.on_press_key("f6", lambda _: self._disable_all())
            keyboard.on_press_key("esc", lambda _: self.stop())

            while self.running:
                time.sleep(0.1)
        except ImportError:
            print("[!] 'keyboard' modulu bulunamadi. Kisayollar devre disi.")
            print("[!] Kurmak icin: pip install keyboard")

    def _on_f1(self):
        """Handle F1 press - toggle menu."""
        if self.gui_mode and hasattr(self, "menu"):
            self.menu.toggle()

    def _update_loop(self):
        """Periodically update the overlay display."""
        while self.running:
            if self.gui_mode and hasattr(self, "overlay"):
                try:
                    statuses = [m.get_status() for m in self.modules.values()]

                    # Gather extra info from active modules
                    extra_lines = []
                    if self.modules["xray"].enabled:
                        extra_lines.append(self.modules["xray"].get_ore_summary())
                    if self.modules["auto_mine"].enabled:
                        extra_lines.append(self.modules["auto_mine"].get_stats_summary())
                    if self.modules["esp"].enabled:
                        extra_lines.append(self.modules["esp"].get_entity_summary())
                    if self.modules["auto_fish"].enabled:
                        extra_lines.append(self.modules["auto_fish"].get_stats_summary())

                    extra = "\n\n".join(extra_lines)

                    self.overlay.root.after(
                        0, self.overlay.update_display, statuses, extra
                    )
                except Exception:
                    pass

            time.sleep(1)

    def _console_loop(self):
        """Handle console input."""
        while self.running:
            try:
                cmd = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                self.stop()
                break

            if not cmd:
                continue

            if cmd == "help":
                print(HELP_TEXT)
            elif cmd == "status":
                self._print_status()
            elif cmd == "xray":
                self.modules["xray"].toggle()
                if self.modules["xray"].enabled:
                    print(self.modules["xray"].get_ore_summary())
            elif cmd == "mine":
                self.modules["auto_mine"].toggle()
                if self.modules["auto_mine"].enabled:
                    print(self.modules["auto_mine"].get_stats_summary())
            elif cmd == "esp":
                self.modules["esp"].toggle()
                if self.modules["esp"].enabled:
                    print(self.modules["esp"].get_entity_summary())
            elif cmd == "fish":
                self.modules["auto_fish"].toggle()
                if self.modules["auto_fish"].enabled:
                    print(self.modules["auto_fish"].get_stats_summary())
            elif cmd == "stats":
                self._print_all_stats()
            elif cmd in ("quit", "exit", "q"):
                self.stop()
                break
            elif cmd == "f2":
                self.modules["xray"].toggle()
            elif cmd == "f3":
                self.modules["auto_mine"].toggle()
            elif cmd == "f4":
                self.modules["esp"].toggle()
            elif cmd == "f5":
                self.modules["auto_fish"].toggle()
            elif cmd == "f6":
                self._disable_all()
            else:
                print(f"Bilinmeyen komut: '{cmd}'. 'help' yazin.")

    def _print_status(self):
        """Print status of all modules."""
        print("\n=== Modul Durumlari ===")
        for module in self.modules.values():
            print(f"  {module.get_status()}")

    def _print_all_stats(self):
        """Print stats from all active modules."""
        has_active = False
        for module in self.modules.values():
            if module.enabled:
                has_active = True
                if hasattr(module, "get_stats_summary"):
                    print(f"\n{module.get_stats_summary()}")
                elif hasattr(module, "get_ore_summary"):
                    print(f"\n{module.get_ore_summary()}")
                elif hasattr(module, "get_entity_summary"):
                    print(f"\n{module.get_entity_summary()}")

        if not has_active:
            print("Aktif modul yok. Bir modulu acmak icin komut yazin.")

    def _disable_all(self):
        """Disable all modules."""
        for module in self.modules.values():
            if module.enabled:
                module.disable()
        print("[!] Tum moduller kapatildi.")

    def stop(self):
        """Stop the helper tool."""
        print("\nMinecraft Helper Tool kapatiliyor...")
        self.running = False
        self._disable_all()

        if self.gui_mode:
            try:
                if hasattr(self, "menu"):
                    self.menu.destroy()
                if hasattr(self, "overlay"):
                    self.overlay.root.after(0, self.overlay.destroy)
            except Exception:
                pass

        print("Gorusuruz! Iyi oyunlar!")
        sys.exit(0)


def main():
    """Entry point."""
    app = MinecraftHelper()
    app.start()


if __name__ == "__main__":
    main()
