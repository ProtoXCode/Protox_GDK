# 🧩 GDK Sprite JSON v2 Specification

> *A stateful, data-driven format for modular animation control in the GDK ecosystem.*

---

## 🎯 Overview

The **GDK Sprite JSON v2** format extends the original single-animation design into a **multi-state animation system**, enabling complex characters (like UGH! cavemen or spaceships) to express multiple behaviors — idle, walk, talk, jump, etc. — in a single declarative file.

This format is fully **backward-compatible** with v1.

---

## 📜 Example JSON

```jsonc
{
  "name": "Cave Man",
  "author": "Tom",
  "width": 16,
  "height": 16,
  "fps": 10,           // global fallback
  "loop": true,         // global fallback
  "tags": ["player", "npc", "animated"],
  "palette": [
    [0, 0, 0, 0],
    [255, 255, 255, 255],
    [64, 64, 64, 255]
  ],

  // --- Stateful animation definitions ---
  "animations": {
    "idle": {
      "frames": [0],               // frame indices
      "fps": 4,                    // optional override
      "loop": true                 // optional override
    },
    "walk": {
      "frames": [1, 2, 3, 4],
      "fps": 8,
      "loop": true
    },
    "talk": {
      "frames": [5, 6, 7, 8],
      "fps": 12,
      "loop": true
    },
    "jump": {
      "frames": [9, 10, 11, 12],
      "fps": 10,
      "loop": false                // one-shot animation
    }
  },

  // --- Core image data ---
  "frames": [
    [[-1, -1, 1, 1, -1], ...],     // frame 0
    [[-1,  1,  1,  1, -1], ...],   // frame 1
    [[ 1,  1,  1,  1,  1], ...]    // frame 2
  ]
}
```

---

## ⚙️ Backward Compatibility

If `animations` is not present, GDK Runtime will default to the legacy behavior:

```python
frames = data["frames"]
loop = data.get("loop", True)
fps = data.get("fps", 10)
```

✅ Works seamlessly with v1 sprite JSONs.

---

## 🧠 Runtime Example

Once loaded via the new `SpriteLoader`, developers can trigger animations by state name:

```python
caveman = SpriteLoader("caveman.json")

caveman.play("idle")      # plays single frame in loop
caveman.play("walk")      # plays frames [1,2,3,4]
caveman.play("jump")      # plays frames [9..12] once
```

The loader automatically applies per-animation `fps` and `loop` overrides.

---

## 🧩 Optional Future Extensions

| Key | Description |
|-----|--------------|
| `hitbox` | Defines collision rectangle for each frame. |
| `pivot` | Origin point for rotation or placement (useful for attaching weapons or effects). |
| `offset` | Rendering offset relative to logical position (for fine-tuning walk cycles). |
| `sound` | Trigger sound effect when the animation starts. |
| `event` | Runtime trigger hook (e.g., call a function when a frame is reached). |

Example:
```json
"walk": {
  "frames": [1, 2, 3, 4],
  "fps": 8,
  "loop": true,
  "sound": "step.wav",
  "hitbox": [2, 10, 12, 4],
  "event": "on_step"
}
```

---

## 🧩 Design Benefits

- 🧠 **Declarative animation control** — no frame management in code.
- 🧱 **Data-driven** — easy to modify without touching Python.
- 🎬 **Multiple animation states** per sprite.
- ⚙️ **Customizable playback** (loop, fps, one-shot).
- 🧩 **Expandable metadata** — future-proof for AI agents, collisions, or sound triggers.
- 🕹️ **Fully Git-friendly** — plain JSON diff.

---

## 🔮 Summary

| Concept | Purpose |
|----------|----------|
| `animations` | Named animation sets for state control |
| `frames` | Pixel data per frame |
| `palette` | Shared RGBA palette |
| `fps`, `loop` | Global or per-animation timing |
| `extensions` | Optional hitbox, pivot, offset, sound, events |

**GDK Sprite JSON v2** transforms sprites from simple bitmaps into structured animation blueprints — portable, editable, and runtime-ready for Python, Pygame, and beyond.

---

> 📦 *Reserved for implementation in the UGH! editor pipeline and the upcoming GDK Runtime v0.2 release.*

