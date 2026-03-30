"""X-Ray Vision Module - Highlights valuable ores and blocks."""

import json
import os
from modules.base_module import BaseModule


# Minecraft ore block IDs and their display colors (RGB)
ORE_REGISTRY = {
    "diamond_ore": {"color": (0, 255, 255), "priority": 1, "label": "Elmas"},
    "deepslate_diamond_ore": {"color": (0, 200, 255), "priority": 1, "label": "Derin Elmas"},
    "ancient_debris": {"color": (139, 69, 19), "priority": 1, "label": "Netherite"},
    "emerald_ore": {"color": (0, 255, 0), "priority": 2, "label": "Zumrut"},
    "deepslate_emerald_ore": {"color": (0, 200, 0), "priority": 2, "label": "Derin Zumrut"},
    "gold_ore": {"color": (255, 215, 0), "priority": 3, "label": "Altin"},
    "deepslate_gold_ore": {"color": (200, 170, 0), "priority": 3, "label": "Derin Altin"},
    "nether_gold_ore": {"color": (255, 200, 0), "priority": 3, "label": "Nether Altin"},
    "iron_ore": {"color": (210, 180, 140), "priority": 4, "label": "Demir"},
    "deepslate_iron_ore": {"color": (180, 150, 110), "priority": 4, "label": "Derin Demir"},
    "lapis_ore": {"color": (0, 0, 200), "priority": 4, "label": "Lapis"},
    "deepslate_lapis_ore": {"color": (0, 0, 160), "priority": 4, "label": "Derin Lapis"},
    "redstone_ore": {"color": (255, 0, 0), "priority": 5, "label": "Kiziltas"},
    "deepslate_redstone_ore": {"color": (200, 0, 0), "priority": 5, "label": "Derin Kiziltas"},
    "copper_ore": {"color": (184, 115, 51), "priority": 5, "label": "Bakir"},
    "deepslate_copper_ore": {"color": (150, 90, 40), "priority": 5, "label": "Derin Bakir"},
    "coal_ore": {"color": (50, 50, 50), "priority": 6, "label": "Komur"},
    "deepslate_coal_ore": {"color": (30, 30, 30), "priority": 6, "label": "Derin Komur"},
    "nether_quartz_ore": {"color": (230, 230, 230), "priority": 5, "label": "Kuvars"},
}

# Special blocks to highlight
SPECIAL_BLOCKS = {
    "spawner": {"color": (128, 0, 128), "priority": 1, "label": "Spawner"},
    "chest": {"color": (139, 90, 43), "priority": 2, "label": "Sandik"},
    "ender_chest": {"color": (75, 0, 130), "priority": 1, "label": "Ender Sandik"},
    "shulker_box": {"color": (180, 100, 200), "priority": 2, "label": "Shulker"},
    "enchanting_table": {"color": (100, 0, 200), "priority": 3, "label": "Buyu Masasi"},
}


class XRayModule(BaseModule):
    """X-Ray vision module that tracks and displays ore locations."""

    def __init__(self):
        super().__init__(
            name="X-Ray Vision",
            description="Cevherleri ve onemli bloklari isaretler",
            hotkey="F2",
        )
        self.tracked_ores = {}
        self.scan_radius = 16  # chunk radius
        self.show_ores = True
        self.show_special = True
        self.min_priority = 6  # show all by default
        self.ore_count = {}
        self._config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "xray_config.json"
        )
        self._load_config()

    def _load_config(self):
        """Load X-Ray configuration from file."""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, "r") as f:
                    config = json.load(f)
                self.scan_radius = config.get("scan_radius", 16)
                self.show_ores = config.get("show_ores", True)
                self.show_special = config.get("show_special", True)
                self.min_priority = config.get("min_priority", 6)
        except (json.JSONDecodeError, IOError):
            pass

    def save_config(self):
        """Save current configuration to file."""
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        config = {
            "scan_radius": self.scan_radius,
            "show_ores": self.show_ores,
            "show_special": self.show_special,
            "min_priority": self.min_priority,
        }
        with open(self._config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _tick(self):
        """Scan for ores in the area (simulated)."""
        self._simulate_scan()

    @property
    def tick_interval(self) -> float:
        return 1.0  # scan every second

    def _simulate_scan(self):
        """Simulate an ore scan and update tracked ores."""
        import random

        # Simulate finding ores at random positions within scan radius
        if random.random() < 0.3:  # 30% chance each tick
            ore_types = list(ORE_REGISTRY.keys())
            ore = random.choice(ore_types)
            info = ORE_REGISTRY[ore]

            if info["priority"] <= self.min_priority:
                x = random.randint(-self.scan_radius * 16, self.scan_radius * 16)
                y = random.randint(-64, 320)
                z = random.randint(-self.scan_radius * 16, self.scan_radius * 16)
                pos_key = f"{x},{y},{z}"

                self.tracked_ores[pos_key] = {
                    "type": ore,
                    "label": info["label"],
                    "color": info["color"],
                    "priority": info["priority"],
                    "pos": (x, y, z),
                }

                self.ore_count[ore] = self.ore_count.get(ore, 0) + 1

    def get_nearby_ores(self, max_distance=None):
        """Get all tracked ores, optionally filtered by distance."""
        ores = list(self.tracked_ores.values())
        ores.sort(key=lambda o: o["priority"])
        return ores

    def get_ore_summary(self) -> str:
        """Get a summary of found ores."""
        if not self.ore_count:
            return "Henuz cevher bulunamadi..."

        lines = ["=== X-Ray Tarama Sonuclari ==="]
        for ore, count in sorted(self.ore_count.items(), key=lambda x: ORE_REGISTRY.get(x[0], {}).get("priority", 99)):
            info = ORE_REGISTRY.get(ore, {})
            label = info.get("label", ore)
            lines.append(f"  {label}: {count} adet")
        lines.append(f"  Toplam: {sum(self.ore_count.values())} cevher")
        return "\n".join(lines)

    def clear_tracked(self):
        """Clear all tracked ores."""
        self.tracked_ores.clear()
        self.ore_count.clear()
        print("[X-Ray] Takip edilen cevherler temizlendi")

    def set_filter(self, max_priority: int):
        """Set priority filter (1=only diamonds, 6=show all)."""
        self.min_priority = max(1, min(6, max_priority))
        print(f"[X-Ray] Filtre ayarlandi: oncelik <= {self.min_priority}")

    def get_render_data(self):
        """Get data needed to render ore highlights on overlay."""
        render_items = []
        for pos_key, ore_data in self.tracked_ores.items():
            if ore_data["priority"] <= self.min_priority:
                render_items.append({
                    "pos": ore_data["pos"],
                    "color": ore_data["color"],
                    "label": ore_data["label"],
                    "priority": ore_data["priority"],
                })
        return render_items
