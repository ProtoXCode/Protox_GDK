# 🧩 ProtoX Game Developer Kit (GDK)

> **“Pixel-perfect control meets intent-driven design.”**\
> A modular retro-style game creation kit built in **Python**, featuring
> integrated editors for sprites, levels, and scenes — all sharing a unified,
> human-readable JSON format.

---

## 🚀 Overview

**ProtoX GDK** is an experimental toolkit for designing 2D games the smart way
— with clean data, modular structure, and zero bloat.

Each editor is its own creative module:

| Editor               | Purpose                                                                        | Output                         |
| -------------------- | ------------------------------------------------------------------------------ | ------------------------------ |
| 🎨 **Sprite Editor** | Draw and animate sprites using a palette-based grid.                           | `.sprite.json`, `.png`, `.gif` |
| 🧱 **Level Editor**  | Arrange tiles and props into maps or stages.                                   | `.level.json`                  |
| 🎮 **Scene Editor**  | Combine levels and sprites into storyboards, cutscenes, or gameplay sequences. | `.scene.json`                  |

All editors share a **common data philosophy** — small JSON files storing visual
intent, animation data, and metadata.\
This design makes them perfect for future integration with engines like **pygame**
or my own **ProtoX runtime**.

---

## 🧠 Data Model Overview

### 🎨 Sprite Format — `.sprite.json`

Minimal, editable, and reusable across editors.

```json
{
  "name": "player_idle",
  "width": 16,
  "height": 16,
  "fps": 12,
  "loop": true,
  "author": "ProtoX",
  "tags": ["player", "idle"],
  "palette": [
    [0, 0, 0, 0],
    [255, 255, 255, 255],
    [255, 0, 0, 255]
  ],
  "frames": [
    [[0,1,1,0],[1,2,2,1],[0,1,1,0]]
  ]
}
```

- ✅ Editable in any text editor
- ✅ Self-contained palette and animation logic
- ✅ Ideal for AI-assisted or procedural sprite generation later

---

### 🧱 Level Format — `.level.json`

Tile-based grid that references sprite assets.

```json
{
  "name": "forest_path",
  "width": 64,
  "height": 32,
  "tile_size": 16,
  "author": "ProtoX",
  "tilesets": ["tiles/ground.json", "tiles/foliage.json"],
  "layers": [
    {
      "name": "background",
      "visible": true,
      "data": [
        [0,0,1,1,1,0,0],
        [0,1,2,2,2,1,0]
      ]
    },
    {
      "name": "objects",
      "data": [
        {"x": 5, "y": 6, "sprite": "sprites/apple.json"},
        {"x": 10, "y": 4, "sprite": "sprites/rock.json"}
      ]
    }
  ]
}
```

- 🔲 Grid-based for consistent blitting
- 🧩 Layers for depth, collisions, and decorations
- 🔗 References sprites and tiles by path

---

### 🎮 Scene Format — `.scene.json`

For storyboards, sequences, or game logic.

```json
{
  "name": "intro_scene",
  "levels": ["levels/forest_path.json"],
  "actors": [
    {"id": "player", "sprite": "sprites/player_idle.json", "x": 5, "y": 8},
    {"id": "bird", "sprite": "sprites/bird.json", "x": 12, "y": 4}
  ],
  "keyframes": [
    {"time": 0, "action": "show", "actor": "player"},
    {"time": 1000, "action": "move", "actor": "bird", "to": [15, 3]},
    {"time": 2500, "action": "say", "actor": "player", "text": "Where am I?"}
  ],
  "music": "audio/intro_theme.mod"
}
```

- 🎞️ Timeline-based keyframes
- 🧠 Declarative logic for movement, dialogue, and triggers
- ♻️ Fully composable — reuse levels and sprites seamlessly

---

## 🧪 Current Features

- CustomTkinter GUI with modular windowing
- Sprite Editor with palette, onion skin, and frame controls
- JSON import/export with metadata sync
- PNG and animated GIF export
- Scrollable, zoomable canvas
- Dynamic sub-menu for metadata and editor-specific tools
- Basic testing framework (pytest)

---

## 🔮 Roadmap

| Feature                                  | Status       |
| ---------------------------------------- | ------------ |
| Sprite animation → GIF export            | ✅ Done      |
| Level editor drag-drop interface         | 🚧 Planned   |
| Scene editor with keyframe timeline      | 🚧 Planned   |
| Asset browser / palette folders          | 🧩 Concept   |
| Pygame runtime loader for `.sprite.json` | 🧠 Research  |
| Music events, make music control gameplay| 🧠 Research  |
| Binary `.gdkimg` format (compressed)     | 🧪 Prototype |
| Multi-tool workspace saving              | 🔜 Future    |


---

## 🧑‍💻 Philosophy

ProtoX GDK is built around **clarity, modularity, and intent**.\
Every editor produces open, structured data instead of opaque binaries.\
That makes it ideal for:

- educational use,
- AI/ML-assisted creative workflows,
- procedural or agentic game development,
- or just good old retro fun.

---

## 📂 Project Structure

```
ProtoX_GDK/
├─ gdk/
│  ├─ palette.py
│  ├─ protox_tools.py
│  └─ config_loader.py
├─ gui/
│  ├─ main_window.py
│  ├─ view_sprite.py
│  ├─ view_level.py
│  ├─ view_scene.py
│  └─ view_splash.py
├─ assets/
│  ├─ icons/
│  └─ images/
├─ tools/
│  └─ nuitka_build.cmd
└─ tests/
```

---

## 🧠 Credits & License

Created with ❤️ by **ProtoX**\
License: **MIT** (free to use, modify, and build upon)

---

> *“The old Amiga spirit never died — it just learned Python.”*
