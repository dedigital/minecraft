# MC Helper v2.1

> Premium Minecraft helper tool — Fabric mod with radar system and remote control panel

![Version](https://img.shields.io/badge/version-2.1.0-00d4ff?style=flat-square)
![MC](https://img.shields.io/badge/Minecraft-26.1+-green?style=flat-square)
![Modules](https://img.shields.io/badge/modules-15-purple?style=flat-square)

---

## ⚡ Modules (15 total)

### ⚔ Combat
| Module | Key | Description |
|--------|-----|-------------|
| **Kill Aura** | `R` | Auto-attack nearest hostile mob (configurable range) |
| **Anti-Knockback** | `B` | Reduce knockback by 90% |
| **Criticals** | `F` | Jump before attack for critical hit damage |

### 🏃 Movement
| Module | Key | Description |
|--------|-----|-------------|
| **Fly** | `H` | Creative flight mode |
| **Speed** | `J` | Velocity multiplier (configurable 1.0x-5.0x) |
| **Auto-Sprint** | `K` | Automatic sprinting |
| **No Fall** | `N` | No fall damage (client + server) |
| **Step Assist** | `V` | Walk up 1.5 block surfaces |

### 👁 Visual
| Module | Key | Description |
|--------|-----|-------------|
| **Fullbright** | `G` | See in complete darkness |
| **Radar** | `U` | 2D radar showing entities + ores in GUI |
| **Anti-Blind** | `O` | Remove blindness/darkness effects |
| **No Weather** | `Y` | Clear rain and thunder |
| **Zoom** | `C` | Hold to zoom (configurable FOV) |

### ♥ Player
| Module | Key | Description |
|--------|-----|-------------|
| **No Hunger** | `P` | Keep hunger full (singleplayer) |
| **Auto-Tool** | `T` | Auto-select best tool when mining |
| **Fast Break** | `I` | 2x mining speed |

**In-Game Menu:** Press `M`

---

## 🛰 Radar System (NEW in v2.1)

The Radar tab in the control panel shows a live 2D map:

- **300x300 circular radar** with range rings (8/16/24/32 blocks)
- **Entities**: Hostile (red), Passive (green), Players (blue)
- **Ores**: Diamond (cyan), Iron (white), Gold (yellow), Emerald (green), Lapis (blue), Redstone (red), and more
- **Chests & Spawners** highlighted
- **Rotates with player facing** — forward is always up
- **Wallhack alternative** — see ores through blocks on the radar

---

## 🖥 Remote Control Panel

Premium Python GUI with:
- Dark gaming theme with animated toggle switches
- Custom sliders for Speed, Kill Aura range, Zoom FOV
- Live HP/Food bars, Armor, Coordinates, FPS
- Category tabs + Radar tab with 2D map
- Bidirectional sync with in-game keybinds

---

## 📦 Installation

### Requirements
- Minecraft 26.1+ with Fabric Loader
- Fabric API
- Java 25+
- Python 3.x (for control panel)

### Quick Start
```bash
# Build
cd fabric-mod && ./gradlew build

# Install
copy build/libs/*.jar %APPDATA%/.minecraft/mods/

# Launch control panel (optional)
cd controller && python mchelper_gui.py
```

---

## 📋 Changelog

### v2.1.0
- ✅ 6 new modules (Criticals, Radar, Anti-Blind, No Weather, Auto-Tool, Fast Break)
- ✅ 2D Radar system — entities and ores on a live rotating map
- ✅ 13 ore types detected (diamond through spawner)
- ✅ Radar tab in GUI with range rings, cardinal directions, legend
- ✅ Total 15 modules across 4 categories

### v2.0.0
- ✅ Complete rewrite with remote control panel
- ✅ Kill Aura, Anti-Knockback, Step Assist, No Hunger
- ✅ TCP socket control (port 25567)
- ✅ Premium dark-themed GUI with sliders and live stats

### v1.0.0
- Initial release: Fullbright, Fly, Speed, Sprint, No Fall, Zoom

---

## ⚠ Disclaimer
Bu araç sadece arkadaşlar arası yarışma ve single-player eğitim amaçlıdır.
