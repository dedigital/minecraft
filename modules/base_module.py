"""Base module class for all helper modules."""

import threading
import time


class BaseModule:
    """Base class that all helper modules inherit from."""

    def __init__(self, name: str, description: str, hotkey: str):
        self.name = name
        self.description = description
        self.hotkey = hotkey
        self.enabled = False
        self._thread = None
        self._stop_event = threading.Event()

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def enable(self):
        self.enabled = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print(f"[+] {self.name} AÇILDI")

    def disable(self):
        self.enabled = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None
        print(f"[-] {self.name} KAPANDI")

    def _run_loop(self):
        """Override this in subclasses for continuous behavior."""
        while not self._stop_event.is_set():
            if self.enabled:
                self._tick()
            self._stop_event.wait(timeout=self.tick_interval)

    @property
    def tick_interval(self) -> float:
        return 0.1

    def _tick(self):
        """Override this in subclasses. Called each tick while enabled."""
        pass

    def get_status(self) -> str:
        status = "AÇIK ✓" if self.enabled else "KAPALI ✗"
        return f"{self.name} [{self.hotkey}]: {status}"
