"""Auto-Mine Module - Automated mining patterns and helpers."""

import time
import random
from modules.base_module import BaseModule


class MiningPattern:
    """Defines a mining pattern strategy."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def get_moves(self):
        raise NotImplementedError


class StripMinePattern(MiningPattern):
    """Classic strip mining - dig forward at Y=11 with branches."""

    def __init__(self):
        super().__init__("Strip Mine", "Y=-59 seviyesinde duz kazi")
        self.branch_spacing = 3
        self.branch_length = 20
        self.tunnel_length = 100

    def get_moves(self):
        moves = []
        for i in range(self.tunnel_length):
            moves.append({"action": "dig_forward", "blocks": 1})
            if i % self.branch_spacing == 0:
                # Branch left
                for _ in range(self.branch_length):
                    moves.append({"action": "dig_left", "blocks": 1})
                moves.append({"action": "return_to_tunnel"})
                # Branch right
                for _ in range(self.branch_length):
                    moves.append({"action": "dig_right", "blocks": 1})
                moves.append({"action": "return_to_tunnel"})
        return moves


class BranchMinePattern(MiningPattern):
    """Branch mining with optimal spacing for diamond finding."""

    def __init__(self):
        super().__init__("Branch Mine", "Elmas icin optimize edilmis dal kazisi")
        self.main_tunnel_length = 50
        self.branch_length = 30
        self.branch_spacing = 4  # optimal for diamonds

    def get_moves(self):
        moves = []
        for i in range(self.main_tunnel_length):
            moves.append({"action": "dig_forward", "blocks": 2})  # 2 high tunnel
            if i % self.branch_spacing == 0:
                for side in ["left", "right"]:
                    for _ in range(self.branch_length):
                        moves.append({"action": f"dig_{side}", "blocks": 2})
                    moves.append({"action": "return_to_tunnel"})
        return moves


class StaircasePattern(MiningPattern):
    """Staircase mining - dig down in a staircase pattern."""

    def __init__(self):
        super().__init__("Merdiven Kazi", "Merdiven seklinde asagi kazi")
        self.depth = 64

    def get_moves(self):
        moves = []
        for _ in range(self.depth):
            moves.append({"action": "dig_forward", "blocks": 1})
            moves.append({"action": "dig_down", "blocks": 1})
        return moves


MINING_PATTERNS = {
    "strip": StripMinePattern,
    "branch": BranchMinePattern,
    "staircase": StaircasePattern,
}


class AutoMineModule(BaseModule):
    """Automated mining helper with various patterns."""

    def __init__(self):
        super().__init__(
            name="Auto-Mine",
            description="Otomatik kazi yardimcisi",
            hotkey="F3",
        )
        self.current_pattern = None
        self.pattern_name = "branch"
        self.moves_queue = []
        self.move_index = 0
        self.blocks_mined = 0
        self.ores_found = 0
        self.mining_speed = 0.5  # seconds per action
        self.auto_torch = True
        self.torch_interval = 8  # place torch every N blocks
        self.auto_eat = True
        self.avoid_lava = True
        self.stats = {
            "total_blocks": 0,
            "diamonds_found": 0,
            "iron_found": 0,
            "gold_found": 0,
            "coal_found": 0,
            "redstone_found": 0,
            "lapis_found": 0,
            "emerald_found": 0,
            "session_start": None,
        }

    def set_pattern(self, pattern_name: str):
        """Set the mining pattern."""
        if pattern_name in MINING_PATTERNS:
            self.pattern_name = pattern_name
            self.current_pattern = MINING_PATTERNS[pattern_name]()
            self.moves_queue = self.current_pattern.get_moves()
            self.move_index = 0
            print(f"[Auto-Mine] Desen ayarlandi: {self.current_pattern.name}")
        else:
            print(f"[Auto-Mine] Bilinmeyen desen: {pattern_name}")
            print(f"[Auto-Mine] Mevcut desenler: {', '.join(MINING_PATTERNS.keys())}")

    def enable(self):
        if self.current_pattern is None:
            self.set_pattern(self.pattern_name)
        self.stats["session_start"] = time.time()
        super().enable()

    @property
    def tick_interval(self) -> float:
        return self.mining_speed

    def _tick(self):
        """Execute next mining move."""
        if not self.moves_queue or self.move_index >= len(self.moves_queue):
            print("[Auto-Mine] Kazi deseni tamamlandi!")
            self.disable()
            return

        move = self.moves_queue[self.move_index]
        self._execute_move(move)
        self.move_index += 1

        # Auto torch placement
        if self.auto_torch and self.blocks_mined % self.torch_interval == 0:
            self._place_torch()

        # Simulate finding ores
        self._check_for_ores()

    def _execute_move(self, move: dict):
        """Simulate executing a mining move."""
        action = move["action"]
        blocks = move.get("blocks", 1)

        if action == "return_to_tunnel":
            return

        self.blocks_mined += blocks
        self.stats["total_blocks"] += blocks

    def _place_torch(self):
        """Simulate placing a torch."""
        pass  # In real implementation, would send key press

    def _check_for_ores(self):
        """Simulate checking for ores while mining."""
        ore_chances = {
            "coal_found": 0.08,
            "iron_found": 0.05,
            "gold_found": 0.02,
            "redstone_found": 0.03,
            "lapis_found": 0.015,
            "diamonds_found": 0.008,
            "emerald_found": 0.003,
        }

        for ore, chance in ore_chances.items():
            if random.random() < chance:
                self.stats[ore] = self.stats.get(ore, 0) + 1
                self.ores_found += 1

    def get_stats_summary(self) -> str:
        """Get mining statistics summary."""
        elapsed = 0
        if self.stats["session_start"]:
            elapsed = time.time() - self.stats["session_start"]

        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        lines = [
            "=== Auto-Mine Istatistikleri ===",
            f"  Sure: {minutes}dk {seconds}sn",
            f"  Kazilan Blok: {self.stats['total_blocks']}",
            f"  Bulunan Cevher: {self.ores_found}",
            f"  ---",
            f"  Elmas: {self.stats['diamonds_found']}",
            f"  Zumrut: {self.stats['emerald_found']}",
            f"  Altin: {self.stats['gold_found']}",
            f"  Demir: {self.stats['iron_found']}",
            f"  Lapis: {self.stats['lapis_found']}",
            f"  Kiziltas: {self.stats['redstone_found']}",
            f"  Komur: {self.stats['coal_found']}",
            f"  ---",
            f"  Desen: {self.pattern_name}",
            f"  Ilerleme: {self.move_index}/{len(self.moves_queue)}",
        ]
        return "\n".join(lines)

    def get_progress(self) -> float:
        """Get mining progress as a percentage."""
        if not self.moves_queue:
            return 0.0
        return (self.move_index / len(self.moves_queue)) * 100
