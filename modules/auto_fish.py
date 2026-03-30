"""Auto-Fish Module - Automated fishing helper."""

import time
import random
from modules.base_module import BaseModule


# Minecraft fishing loot tables
FISH_LOOT = {
    "common": {
        "cod": {"chance": 0.50, "label": "Morina", "xp": 1},
        "salmon": {"chance": 0.25, "label": "Somon", "xp": 1},
        "pufferfish": {"chance": 0.13, "label": "Balon Baligi", "xp": 1},
        "tropical_fish": {"chance": 0.12, "label": "Tropikal Balik", "xp": 1},
    },
    "treasure": {
        "enchanted_book": {"chance": 0.30, "label": "Buyulu Kitap", "xp": 5},
        "bow": {"chance": 0.15, "label": "Yay", "xp": 3},
        "fishing_rod": {"chance": 0.15, "label": "Olta", "xp": 3},
        "name_tag": {"chance": 0.15, "label": "Isim Etiketi", "xp": 3},
        "nautilus_shell": {"chance": 0.15, "label": "Nautilus Kabubu", "xp": 3},
        "saddle": {"chance": 0.10, "label": "Eyer", "xp": 3},
    },
    "junk": {
        "lily_pad": {"chance": 0.15, "label": "Nilüfer", "xp": 1},
        "bowl": {"chance": 0.10, "label": "Kase", "xp": 1},
        "leather": {"chance": 0.10, "label": "Deri", "xp": 1},
        "leather_boots": {"chance": 0.10, "label": "Deri Bot", "xp": 1},
        "rotten_flesh": {"chance": 0.10, "label": "Curuk Et", "xp": 1},
        "stick": {"chance": 0.10, "label": "Cubuk", "xp": 1},
        "string": {"chance": 0.10, "label": "Ip", "xp": 1},
        "water_bottle": {"chance": 0.10, "label": "Su Sisesi", "xp": 1},
        "bone": {"chance": 0.08, "label": "Kemik", "xp": 1},
        "ink_sac": {"chance": 0.07, "label": "Murekkep", "xp": 1},
    },
}

# Base chances for each category
CATEGORY_CHANCES = {
    "common": 0.85,
    "treasure": 0.05,
    "junk": 0.10,
}


class AutoFishModule(BaseModule):
    """Automated fishing module with loot tracking."""

    def __init__(self):
        super().__init__(
            name="Auto-Fish",
            description="Otomatik balik tutma",
            hotkey="F5",
        )
        self.total_catches = 0
        self.total_xp = 0
        self.loot_history = []
        self.loot_counts = {}
        self.category_counts = {"common": 0, "treasure": 0, "junk": 0}
        self.fishing_speed = 3.0  # average seconds per catch
        self.luck_of_the_sea = 0  # enchantment level (0-3)
        self.lure_level = 0  # enchantment level (0-3)
        self.session_start = None
        self.auto_recast = True
        self.rain_bonus = False

    def enable(self):
        self.session_start = time.time()
        super().enable()

    @property
    def tick_interval(self) -> float:
        # Lure reduces wait time
        base_time = self.fishing_speed
        lure_reduction = self.lure_level * 0.5
        return max(1.0, base_time - lure_reduction)

    def _tick(self):
        """Attempt to catch a fish."""
        self._simulate_catch()

    def _simulate_catch(self):
        """Simulate a fishing catch with loot table."""
        # Determine category (luck of the sea improves treasure chance)
        treasure_bonus = self.luck_of_the_sea * 0.02
        rain_bonus = 0.01 if self.rain_bonus else 0

        chances = {
            "treasure": CATEGORY_CHANCES["treasure"] + treasure_bonus + rain_bonus,
            "junk": max(0.01, CATEGORY_CHANCES["junk"] - treasure_bonus),
        }
        chances["common"] = 1.0 - chances["treasure"] - chances["junk"]

        # Roll for category
        roll = random.random()
        cumulative = 0
        category = "common"
        for cat, chance in chances.items():
            cumulative += chance
            if roll <= cumulative:
                category = cat
                break

        # Roll for specific item within category
        loot_table = FISH_LOOT[category]
        item_roll = random.random()
        cumulative = 0
        caught_item = None

        for item_id, item_info in loot_table.items():
            cumulative += item_info["chance"]
            if item_roll <= cumulative:
                caught_item = {"id": item_id, **item_info, "category": category}
                break

        if caught_item is None:
            # Fallback to first item in category
            first_id = list(loot_table.keys())[0]
            caught_item = {"id": first_id, **loot_table[first_id], "category": category}

        # Record catch
        self.total_catches += 1
        self.total_xp += caught_item["xp"]
        self.loot_history.append(caught_item)
        self.loot_counts[caught_item["id"]] = self.loot_counts.get(caught_item["id"], 0) + 1
        self.category_counts[category] += 1

        # Keep history manageable
        if len(self.loot_history) > 100:
            self.loot_history = self.loot_history[-50:]

    def get_stats_summary(self) -> str:
        """Get fishing statistics summary."""
        elapsed = 0
        if self.session_start:
            elapsed = time.time() - self.session_start

        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        catches_per_min = self.total_catches / max(1, elapsed / 60)

        lines = [
            "=== Auto-Fish Istatistikleri ===",
            f"  Sure: {minutes}dk {seconds}sn",
            f"  Toplam Yakalama: {self.total_catches}",
            f"  Toplam XP: {self.total_xp}",
            f"  Hiz: {catches_per_min:.1f} yakalama/dk",
            f"  ---",
            f"  Balik: {self.category_counts['common']}",
            f"  Hazine: {self.category_counts['treasure']}",
            f"  Cop: {self.category_counts['junk']}",
            f"  ---",
            f"  Luck of the Sea: {self.luck_of_the_sea}",
            f"  Lure: {self.lure_level}",
        ]

        # Show last 5 catches
        if self.loot_history:
            lines.append(f"  ---")
            lines.append(f"  Son Yakalananlar:")
            for item in self.loot_history[-5:]:
                cat_icon = {"common": "🐟", "treasure": "💎", "junk": "🗑️"}.get(item["category"], "?")
                lines.append(f"    {cat_icon} {item['label']}")

        return "\n".join(lines)

    def get_loot_breakdown(self) -> str:
        """Get detailed loot breakdown."""
        lines = ["=== Loot Dagilimi ==="]

        for category, items in FISH_LOOT.items():
            cat_label = {"common": "Balik", "treasure": "Hazine", "junk": "Cop"}[category]
            lines.append(f"\n  [{cat_label}]")
            for item_id, item_info in items.items():
                count = self.loot_counts.get(item_id, 0)
                if count > 0:
                    lines.append(f"    {item_info['label']}: {count}x")

        return "\n".join(lines)

    def set_enchantments(self, luck: int = 0, lure: int = 0):
        """Set fishing rod enchantment levels."""
        self.luck_of_the_sea = max(0, min(3, luck))
        self.lure_level = max(0, min(3, lure))
        print(f"[Auto-Fish] Luck of the Sea: {self.luck_of_the_sea}, Lure: {self.lure_level}")

    def get_treasure_rate(self) -> float:
        """Get current treasure catch rate percentage."""
        if self.total_catches == 0:
            return 0.0
        return (self.category_counts["treasure"] / self.total_catches) * 100
