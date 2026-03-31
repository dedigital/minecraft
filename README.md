# MC Helper v2.0

> Premium Minecraft helper tool for MC 26.1 — Fabric mod with remote control panel

![Version](https://img.shields.io/badge/version-2.0.0-00d4ff?style=flat-square)
![MC](https://img.shields.io/badge/Minecraft-26.1-green?style=flat-square)
![Fabric](https://img.shields.io/badge/Fabric-0.18.2-yellow?style=flat-square)

---

## ⚡ Modules (10 total)

### ⚔ Combat
| Module | Key | Description |
|--------|-----|-------------|
| **Kill Aura** | `R` | Auto-attack nearest hostile mob (configurable range 2.0-6.0) |
| **Anti-Knockback** | `B` | Reduce knockback by 90% when hit |

### 🏃 Movement
| Module | Key | Description |
|--------|-----|-------------|
| **Fly** | `H` | Creative flight mode |
| **Speed** | `J` | Velocity multiplier (configurable 1.0x-5.0x) |
| **Auto-Sprint** | `K` | Automatic sprinting when moving |
| **No Fall** | `N` | No fall damage (client + server side) |
| **Step Assist** | `V` | Walk up 1.5 block surfaces |

### 👁 Visual
| Module | Key | Description |
|--------|-----|-------------|
| **Fullbright** | `G` | See in complete darkness |
| **Zoom** | `C` | Hold to zoom (configurable FOV) |

### ♥ Player
| Module | Key | Description |
|--------|-----|-------------|
| **No Hunger** | `P` | Keep hunger full (singleplayer) |

**In-Game Menu:** Press `M` to open the GUI menu

---

## 🖥 Remote Control Panel

Premium Python GUI controller with:
- 🎮 Dark gaming theme with cyan accents
- 🔄 Animated toggle switches
- 📊 Custom sliders for configurable values
- ❤️ Live player stats (HP, food, armor, coordinates, FPS)
- 📁 Category tabs (Combat, Movement, Visual, Player)
- 🔗 Bidirectional sync — toggle in-game or from panel

---

## 📦 Installation

### Requirements
- Minecraft 26.1
- Fabric Loader 0.18.2+
- Fabric API
- Java 25+
- Python 3.x (for control panel)

### Steps

**1. Build the mod:**
```bash
cd fabric-mod
./gradlew build
```

**2. Install the mod:**
```bash
copy build/libs/mchelper-2.0.0.jar %APPDATA%/.minecraft/mods/
```

**3. Launch Minecraft, enter a world**

**4. Launch control panel:**
```bash
cd controller
python mchelper_gui.py
```

---

## 📋 Changelog

### v2.0.0 (2026-03-31)
**Complete rewrite — Premium release**
- ✅ 10 modules across 4 categories
- ✅ Kill Aura with attack cooldown and configurable range
- ✅ Anti-Knockback (90% reduction)
- ✅ Step Assist via entity attributes
- ✅ No Hunger (server-side food manipulation)
- ✅ Remote control panel with TCP socket (port 25567)
- ✅ Premium dark-themed Python GUI
- ✅ Animated toggles, custom sliders, live stats
- ✅ Bidirectional sync (keyboard ↔ GUI)
- ✅ Configurable speed, zoom FOV, aura range
- ✅ Player info reporting (HP, food, armor, coords, FPS)

### v1.0.0
- Initial release
- Fullbright, Fly, Speed, Auto-Sprint, No Fall, Zoom
- Basic in-game GUI menu

---

## ⚠ Disclaimer
Bu araç sadece arkadaşlar arası yarışma ve single-player eğitim amaçlıdır.
