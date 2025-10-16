# 🧠 GDK Behavior Metadata Specification (Draft)

> *Extending GDK JSON from visual intent to behavioral logic.*

---

## 🎯 Purpose

The **Behavior Metadata** extension allows GDK assets (sprites, levels, and scenes) to define *how* an entity behaves, not just *how it looks*.

It bridges static asset data (e.g. sprite frames, palettes) with runtime game logic (movement, gravity, collisions, and states).

---

## 🧩 Concept

Each sprite or scene entity may include a `behavior` block inside its JSON definition. This block contains declarative values describing physics, motion, and state machine behavior.

Example:

```json
"behavior": {
  "gravity": 0.35,
  "jump_force": -8.5,
  "max_fall_speed": 12,
  "collision": true,
  "states": {
    "idle": 0,
    "flap": [1, 2, 3],
    "dead": 4
  }
}
```

---

## ⚙️ Supported Fields

| Key | Type | Description |
|-----|------|-------------|
| `gravity` | float | Downward acceleration per frame (pixels/frame²). |
| `jump_force` | float | Upward velocity when jump triggered. |
| `max_fall_speed` | float | Maximum vertical speed under gravity. |
| `collision` | bool | Enables collision detection against level geometry. |
| `velocity` | object | `{ "x": 0, "y": 0 }` default per-axis speed. |
| `acceleration` | float | Optional per-frame speed change. |
| `friction` | float | Deceleration rate when movement stops. |
| `states` | object | Maps named states to frame indices or frame lists. |
| `loop` | bool | Overrides global loop setting for animations. |

---

## 🎮 Example: Flappy Bird Behavior

```json
{
  "name": "Bird",
  "width": 16,
  "height": 16,
  "fps": 10,
  "loop": true,
  "palette": [...],
  "frames": [...],
  "behavior": {
    "gravity": 0.35,
    "jump_force": -8.5,
    "max_fall_speed": 12,
    "collision": true,
    "states": {
      "idle": 0,
      "flap": [1, 2, 3],
      "dead": 4
    }
  }
}
```

At runtime:
- Gravity applies continuously.
- Spacebar applies `jump_force`.
- Animation switches between state frames.
- Collision toggles with map boundaries.

---

## 🧠 Runtime Integration

A minimal implementation in the runtime could:
- Parse `behavior` into a `BehaviorComponent` object.
- Apply gravity each frame if defined.
- Limit vertical speed by `max_fall_speed`.
- Switch animations based on state.
- Automatically trigger transitions (e.g. `flap → idle`).

```python
if behavior.gravity:
    velocity.y += behavior.gravity
    velocity.y = min(velocity.y, behavior.max_fall_speed)
```

---

## 🚀 Future Extensions

| Category | Ideas |
|-----------|--------|
| Physics | Bounce factor, drag, rotation |
| AI | Patrol paths, aggression radius, idle timers |
| Audio | State-based sound triggers |
| Events | Custom behavior hooks (onJump, onDeath, etc.) |
| Input | Map key bindings to states |

---

### 💡 Vision

This system turns static JSON into **living gameplay definitions**. You’ll be able to load a scene and run it directly, where objects behave according to their metadata — no extra scripting required.

> **From pixels to physics, all inside the GDK JSON.**

