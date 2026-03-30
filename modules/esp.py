"""ESP Module - Entity/Mob tracking and visualization."""

import math
import random
import time
from modules.base_module import BaseModule


# Minecraft entity types with categories
ENTITY_TYPES = {
    # Hostile mobs
    "zombie": {"category": "hostile", "color": (0, 128, 0), "label": "Zombi", "health": 20},
    "skeleton": {"category": "hostile", "color": (200, 200, 200), "label": "Iskelet", "health": 20},
    "creeper": {"category": "hostile", "color": (0, 255, 0), "label": "Creeper", "health": 20},
    "spider": {"category": "hostile", "color": (100, 50, 50), "label": "Orumcek", "health": 16},
    "enderman": {"category": "hostile", "color": (128, 0, 128), "label": "Enderman", "health": 40},
    "witch": {"category": "hostile", "color": (75, 0, 130), "label": "Cadi", "health": 26},
    "blaze": {"category": "hostile", "color": (255, 165, 0), "label": "Blaze", "health": 20},
    "ghast": {"category": "hostile", "color": (255, 255, 255), "label": "Ghast", "health": 10},
    "wither_skeleton": {"category": "hostile", "color": (50, 50, 50), "label": "Wither Iskelet", "health": 20},
    "warden": {"category": "hostile", "color": (0, 50, 80), "label": "Warden", "health": 500},
    "phantom": {"category": "hostile", "color": (70, 70, 150), "label": "Phantom", "health": 20},
    "drowned": {"category": "hostile", "color": (0, 100, 100), "label": "Bogulmus", "health": 20},

    # Passive mobs
    "cow": {"category": "passive", "color": (139, 90, 43), "label": "Inek", "health": 10},
    "sheep": {"category": "passive", "color": (240, 240, 240), "label": "Koyun", "health": 8},
    "pig": {"category": "passive", "color": (255, 182, 193), "label": "Domuz", "health": 10},
    "chicken": {"category": "passive", "color": (255, 255, 255), "label": "Tavuk", "health": 4},
    "horse": {"category": "passive", "color": (160, 82, 45), "label": "At", "health": 30},
    "villager": {"category": "passive", "color": (139, 119, 101), "label": "Koylu", "health": 20},
    "iron_golem": {"category": "passive", "color": (192, 192, 192), "label": "Demir Golem", "health": 100},

    # Boss mobs
    "ender_dragon": {"category": "boss", "color": (148, 0, 211), "label": "Ender Ejder", "health": 200},
    "wither": {"category": "boss", "color": (50, 50, 50), "label": "Wither", "health": 300},

    # Players
    "player": {"category": "player", "color": (255, 255, 0), "label": "Oyuncu", "health": 20},

    # Items
    "item": {"category": "item", "color": (255, 215, 0), "label": "Esya", "health": 0},
    "experience_orb": {"category": "item", "color": (0, 255, 100), "label": "XP", "health": 0},
}

CATEGORY_COLORS = {
    "hostile": (255, 50, 50),
    "passive": (50, 255, 50),
    "boss": (255, 0, 255),
    "player": (255, 255, 0),
    "item": (255, 215, 0),
}


class TrackedEntity:
    """Represents a tracked entity in the world."""

    def __init__(self, entity_id: int, entity_type: str, pos: tuple, health: float):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.pos = pos
        self.health = health
        self.max_health = ENTITY_TYPES.get(entity_type, {}).get("health", 20)
        self.info = ENTITY_TYPES.get(entity_type, {})
        self.last_seen = time.time()
        self.distance = 0.0
        self.velocity = (0, 0, 0)

    @property
    def label(self):
        return self.info.get("label", self.entity_type)

    @property
    def category(self):
        return self.info.get("category", "unknown")

    @property
    def color(self):
        return self.info.get("color", (255, 255, 255))

    @property
    def health_percentage(self):
        if self.max_health <= 0:
            return 0
        return (self.health / self.max_health) * 100

    def get_display_text(self):
        """Get formatted display text for overlay."""
        health_bar = self._health_bar()
        return f"{self.label} {health_bar} ({self.distance:.1f}m)"

    def _health_bar(self):
        """Generate a text-based health bar."""
        if self.max_health <= 0:
            return ""
        filled = int((self.health / self.max_health) * 10)
        empty = 10 - filled
        return f"[{'|' * filled}{'.' * empty}] {self.health:.0f}/{self.max_health}"


class ESPModule(BaseModule):
    """Entity ESP - tracks and displays nearby entities."""

    def __init__(self):
        super().__init__(
            name="ESP",
            description="Mob ve entity takip sistemi",
            hotkey="F4",
        )
        self.tracked_entities = {}
        self.scan_range = 64
        self.show_hostile = True
        self.show_passive = True
        self.show_players = True
        self.show_items = False
        self.show_boss = True
        self.show_health_bars = True
        self.show_distance = True
        self.show_tracers = True  # lines from crosshair to entity
        self.alert_on_hostile = True
        self.alert_range = 16
        self._next_entity_id = 1
        self.alerts = []

    @property
    def tick_interval(self) -> float:
        return 0.5

    def _tick(self):
        """Scan for entities and update tracking."""
        self._simulate_entity_scan()
        self._cleanup_old_entities()
        self._check_alerts()

    def _simulate_entity_scan(self):
        """Simulate scanning for nearby entities."""
        # Simulate entity spawning/movement
        if random.random() < 0.2:
            entity_types = list(ENTITY_TYPES.keys())
            entity_type = random.choice(entity_types)
            info = ENTITY_TYPES[entity_type]

            x = random.uniform(-self.scan_range, self.scan_range)
            y = random.uniform(0, 256)
            z = random.uniform(-self.scan_range, self.scan_range)
            health = info["health"] * random.uniform(0.3, 1.0)

            entity = TrackedEntity(
                entity_id=self._next_entity_id,
                entity_type=entity_type,
                pos=(x, y, z),
                health=health,
            )
            entity.distance = math.sqrt(x**2 + y**2 + z**2)

            self.tracked_entities[self._next_entity_id] = entity
            self._next_entity_id += 1

        # Update distances for existing entities (simulate movement)
        for entity in self.tracked_entities.values():
            dx = random.uniform(-1, 1)
            dz = random.uniform(-1, 1)
            x, y, z = entity.pos
            entity.pos = (x + dx, y, z + dz)
            entity.distance = math.sqrt(entity.pos[0]**2 + entity.pos[1]**2 + entity.pos[2]**2)

    def _cleanup_old_entities(self):
        """Remove entities that haven't been seen recently."""
        now = time.time()
        to_remove = [
            eid for eid, e in self.tracked_entities.items()
            if now - e.last_seen > 10 or e.distance > self.scan_range * 1.5
        ]
        for eid in to_remove:
            del self.tracked_entities[eid]

    def _check_alerts(self):
        """Check for hostile mobs within alert range."""
        if not self.alert_on_hostile:
            return

        for entity in self.tracked_entities.values():
            if entity.category == "hostile" and entity.distance <= self.alert_range:
                alert_msg = f"DIKKAT! {entity.label} {entity.distance:.1f}m uzaklikta!"
                if alert_msg not in self.alerts[-5:] if self.alerts else True:
                    self.alerts.append(alert_msg)

    def get_entities_by_category(self, category: str):
        """Get all tracked entities of a specific category."""
        return [
            e for e in self.tracked_entities.values()
            if e.category == category
        ]

    def get_visible_entities(self):
        """Get all entities that should be displayed based on filters."""
        entities = []
        for entity in self.tracked_entities.values():
            if entity.category == "hostile" and not self.show_hostile:
                continue
            if entity.category == "passive" and not self.show_passive:
                continue
            if entity.category == "player" and not self.show_players:
                continue
            if entity.category == "item" and not self.show_items:
                continue
            if entity.category == "boss" and not self.show_boss:
                continue
            entities.append(entity)

        entities.sort(key=lambda e: e.distance)
        return entities

    def get_entity_summary(self) -> str:
        """Get summary of tracked entities."""
        categories = {}
        for entity in self.tracked_entities.values():
            cat = entity.category
            categories[cat] = categories.get(cat, 0) + 1

        lines = ["=== ESP Entity Ozeti ==="]
        total = len(self.tracked_entities)
        lines.append(f"  Toplam: {total} varlik")
        lines.append(f"  ---")

        category_labels = {
            "hostile": "Dusman",
            "passive": "Pasif",
            "boss": "Boss",
            "player": "Oyuncu",
            "item": "Esya",
        }

        for cat, label in category_labels.items():
            count = categories.get(cat, 0)
            if count > 0:
                lines.append(f"  {label}: {count}")

        if self.alerts:
            lines.append(f"  ---")
            lines.append(f"  Son Uyari: {self.alerts[-1] if self.alerts else 'Yok'}")

        return "\n".join(lines)

    def get_closest_hostile(self):
        """Get the closest hostile entity."""
        hostiles = self.get_entities_by_category("hostile")
        if not hostiles:
            return None
        return min(hostiles, key=lambda e: e.distance)

    def get_render_data(self):
        """Get data for overlay rendering."""
        render_items = []
        for entity in self.get_visible_entities():
            render_items.append({
                "pos": entity.pos,
                "color": entity.color,
                "label": entity.get_display_text(),
                "category": entity.category,
                "show_tracer": self.show_tracers,
                "health_pct": entity.health_percentage,
            })
        return render_items
