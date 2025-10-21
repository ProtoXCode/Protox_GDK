# 🧩 ProtoX Game Developer Kit (GDK) -> Alpha <-

> **“Pixel-perfect control meets intent-driven design.”**\
> A modular retro-style game creation kit built in **Python**, featuring
> integrated editors for sprites, levels, and scenes — all sharing a unified,
> human-readable JSON format.

---

## Disclaimer

> This project started as a *easy project to re-create some old Amiga game* to
> avoid burning out on the other projects as they are kinda difficult at times,
> especially as I work full time in a factory doing factory stuff as I'm not a
> professional programmer, or work with software development.\
> **Currently** 🍺 Here's to hoping .
> 
> Therefore this disclaimer, things here **will** change and I make stuff up as
> I go along, but I got a clear goal in mind, and I try to keep it tidy.

---

## 🚀 Overview
> 🚧 Heavy construction ahead, W.I.P. 🚧

**ProtoX GDK** is an experimental toolkit for designing 2D games the smart way
— with clean data, modular structure, and zero bloat.

Each editor is its own creative module:

| Editor                   | Purpose                                                                                                                                 | Output                         |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| 💾 **Projects Editor**   | Set up projects in an environment settings, base game settings and export game package and runnable framework with binary file formats. | `.gdkimg`, `.gdklvl`           |
| 🎨 **Sprite Editor**     | Draw and animate sprites using a palette-based grid.                                                                                    | `.sprite.json`, `.png`, `.gif` |
| 🧱 **Level Editor**      | Arrange tiles and props into maps or stages.                                                                                            | `.level.json`                  |
| 🎮 **Scene Editor**      | Combine levels and sprites into storyboards, cutscenes, or gameplay sequences.                                                          | `.scene.json`                  |

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
  "properties": {
    "collision": true,
    "static": false,
    "background": false,
    "player": true
  },
  "palette_name": "ProtoX 64",
  "palette": [
    [ 0, 0, 0, 0 ], ...],
  "frames": [
    [[0,1,1,0],[1,2,2,1],[0,1,1,0], ...]
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

| Feature                                       | Status       |
|-----------------------------------------------| ------------ |
| Sprite animation → GIF export                 | ✅ Done      |
| Level editor drag-drop interface              | 🚧 Planned   |
| Scene editor with keyframe timeline           | 🚧 Planned   |
| Asset browser / palette folders               | 🧩 Concept   |
| Pygame runtime loader for `.sprite.json`      | 🧠 Research  |
| Music events, make music control gameplay     | 🧠 Research  |
| Binary `.gdkimg, .gdklvl` format (compressed) | 🧪 Prototype |
| Multi-tool workspace saving                   | 🔜 Future    |


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
├─ main.py
├─ gdk/
│  ├─ palette.py
│  ├─ protox_tools.py
│  └─ config_loader.py
├─ gui/
│  ├─ level_editor/
│  │  ├─ __init__.py
│  │  ├─ level_core.py 
│  │  └─ level_editor.py
│  ├─ project_editor/ 
│  │  ├─ __init__.py
│  │  ├─ project_core.py
│  │  └─ project_editor.py
│  ├─ scene_editor/ 
│  │  ├─ __init__.py 
│  │  ├─ scene_core.py    
│  │  └─ scene_editor.py  
│  ├─ settings/ 
│  │  ├─ __init__.py
│  │  ├─ about.py
│  │  ├─ help.py
│  │  ├─ options.py
│  │  ├─ settings_editor.py   
│  │  └─ sub_menu.py       
│  ├─ sprite_editor/ 
│  │  ├─ __init__.py
│  │  ├─ canvas_view.py
│  │  ├─ core.py
│  │  ├─ editor.py
│  │  ├─ io_manager.py    
│  │  └─ metadata.py  
│  ├─ main_window.py
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

License: **MIT** (free to use, modify, and build upon)

---

> *“All I wanted to do was to remake an old Amiga game with PyGame...”*
