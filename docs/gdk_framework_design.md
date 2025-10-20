# 🎮 ProtoX GDK Framework Vision

> *A modular, data-driven foundation for rapidly bootstrapping 2D games.*

---

## 🧭 Overview

ProtoX GDK isn’t meant to be a full-fledged drag-and-drop game maker. Instead, it’s a **framework generator** — a tool that builds the *foundation* of a 2D game project, complete with:

- Project management and structured folders
- JSON-based sprite, level, and scene editors
- Data-driven runtime bootstrap
- Modular exports (`.gdkimg`, `.gdklvl`, `.gdkproj`)

This lets creators jump from *idea → working prototype* in minutes, while still writing real, extendable Python code.

---

## 🧩 Philosophy: Framework, not Builder

Unlike game builders that trap users inside their GUI, ProtoX GDK generates **transparent source code and data**. Developers can start inside the editor, then extend their game externally with full control.

**Editor responsibilities:**
- Create structured data (sprites, levels, metadata)
- Maintain project structure and references
- Verify runtime readiness (has player, level, controls)

**Runtime responsibilities:**
- Load data from JSON or packaged formats
- Interpret level, sprite, and project metadata
- Provide basic gameplay primitives (collision, gravity, events)

---

## 🧱 Core Components

| Component | Description |
|------------|-------------|
| **Sprite Editor** | Creates sprite sheets, animation frames, and color palettes (JSON-based) |
| **Level Editor** | Defines background and collision layers |
| **Scene Editor** | Manages entity placement, layering, and triggers |
| **Project Panel** | Manages project metadata, game type, and default paths |
| **Runtime** | A lightweight game loop that runs generated data |

---

## 🚀 Data Structure Example

**Project folder layout:**
```text
MyGame/
 ├─ main.py
 ├─ project.gdkproj
 ├─ assets/
 │   ├─ sprites/
 │   │   └─ player.json
 │   ├─ levels/
 │   │   └─ level1.json
 │   └─ scenes/
 │       └─ intro_scene.json
 └─ exports/
```

**project.gdkproj:**
```json
{
  "name": "MyGame",
  "type": "platformer",
  "controls": {"left": "a", "right": "d", "jump": "space"},
  "entry_level": "assets/levels/level1.json"
}
```

**player.json:**
```json
{
  "sprite": "player_idle.png",
  "animations": {"idle": [0], "run": [1, 2, 3]},
  "properties": {"gravity": 0.5, "speed": 3, "jump_force": 8}
}
```

**level1.json:**
```json
{
  "background": "bg_forest.png",
  "collision_layer": "solids",
  "tiles": [[0,0,1,1,1,0], [0,0,0,0,0,0]],
  "player_start": [50, 180]
}
```

---

## 🧩 Runtime Prototype

```python
# main.py – auto-generated runtime stub
from gdk_runtime import Game, Level, Sprite

class Game:
    def __init__(self, window_size=(800, 600)):
        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode(window_size)
        self.clock = pygame.time.Clock()
        self.entities = []
        self.level = None

    def add(self, obj):
        self.entities.append(obj)

    def set_level(self, level):
        self.level = level

    def run(self):
        import pygame
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            for e in self.entities:
                e.update(keys, self.level)

            self.screen.fill((0, 0, 0))
            if self.level:
                self.level.draw(self.screen)
            for e in self.entities:
                e.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

class Level:
    @staticmethod
    def load(path):
        import json, pygame
        data = json.load(open(path))
        surf = pygame.image.load(data["background"]).convert()
        lvl = Level()
        lvl.surface = surf
        lvl.tiles = data["tiles"]
        lvl.player_start = data["player_start"]
        return lvl

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))

class Sprite:
    @staticmethod
    def load(path):
        import json, pygame
        data = json.load(open(path))
        spr = Sprite()
        spr.image = pygame.image.load(data["sprite"]).convert_alpha()
        spr.rect = spr.image.get_rect()
        spr.rect.topleft = (50, 180)
        spr.vel_y = 0
        spr.gravity = data["properties"].get("gravity", 0.5)
        spr.speed = data["properties"].get("speed", 3)
        spr.jump_force = data["properties"].get("jump_force", 8)
        return spr

    def update(self, keys, level):
        if keys[ord('a')]: self.rect.x -= self.speed
        if keys[ord('d')]: self.rect.x += self.speed
        if keys[ord(' ')]: self.vel_y = -self.jump_force
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        # basic ground check
        if self.rect.bottom > 400:
            self.rect.bottom = 400
            self.vel_y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

if __name__ == "__main__":
    game = Game()
    level = Level.load("assets/levels/level1.json")
    player = Sprite.load("assets/sprites/player.json")
    game.set_level(level)
    game.add(player)
    game.run()
```

This runtime can already run any GDK-exported project with a single click.

---

## 🎮 The Future

| Feature | Description |
|----------|--------------|
| **Game Type Presets** | Platformer, top-down, or shooter logic defined in project metadata |
| **Event System** | JSON-driven triggers and actions (spawn, damage, open door, etc.) |
| **Runtime Editor Bridge** | Play directly inside the GDK editor window |
| **Asset Packaging** | `.gdk` bundles with compressed or embedded data |
| **Behavior Templates** | Drop-in enemy and NPC AI scripts |

---

## 🧠 Key Takeaways

- You’re not replacing programming — you’re **accelerating creation**.
- Data-driven design means **you can scale indefinitely**.
- Every exported game remains a **real Python project** — open, hackable, and future-proof.

> “ProtoX GDK isn’t here to make games *for* you. It’s here to make games *possible faster.*”

