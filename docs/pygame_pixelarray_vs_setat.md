# ⚙️ Pygame Pixel Writing Performance — `set_at()` vs `PixelArray`

> *"When rendering from structured data like your GDK JSON sprites, performance matters — but context matters more."*

---

## 🧩 Overview

Pygame offers multiple ways to modify pixels on a `Surface`. For small sprites, `Surface.set_at()` is fine. For bulk image construction (like from JSON data), you might benefit from `PixelArray` or NumPy buffers.

---

## 🧠 Method Comparison

| Method | Speed | Alpha Support | Best Use |
|--------|-------|----------------|-----------|
| `Surface.set_at()` | 🐢 Slow | ✅ Full RGBA | Tiny sprites, infrequent writes |
| `pygame.PixelArray` | ⚡ Fast | ❌ RGB only | Batch RGB fills, surface generation |
| NumPy surface buffer | ⚡⚡ Very Fast | ✅ Full RGBA | Procedural assets, complex effects |
| Hybrid (`PixelArray` + blit) | ⚡ | ✅ | Sprite sheet or JSON decoding |

---

## 🧱 The Problem

`set_at()` calls into C for **every single pixel**. For a 64×64 sprite (4,096 pixels), one frame means 4,096 function calls — multiplied by every frame in an animation.

If you generate hundreds of frames, it quickly becomes a CPU bottleneck.

---

## 🧠 Why `PixelArray` Helps

`PixelArray` gives you **direct buffer access**, allowing you to set many pixels at once without the per-call overhead.

However, it only works with **RGB data** — alpha must be handled separately.

---

## 🧩 The Hybrid Approach

This pattern is ideal for building frames from JSON data:

```python
def _render_frame(self, frame_data) -> pygame.Surface:
    surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    px = pygame.PixelArray(surf)

    for y, row in enumerate(frame_data):
        for x, idx in enumerate(row):
            if idx < 0:
                continue
            r, g, b, a = self.palette[idx]
            px[x, y] = (r << 16) | (g << 8) | b  # fast RGB write

    del px  # unlock PixelArray

    # Apply alpha after bulk write
    alpha_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    alpha_surf.blit(surf, (0, 0))
    return alpha_surf
```

This approach:
- ⚡ Writes pixels in bulk (fast)
- ✅ Preserves alpha transparency
- 🧠 Keeps the API simple

---

## 💬 Key Takeaways

- `set_at()` is fine for **small or one-time sprite loads**.
- `PixelArray` shines for **large batch surface generation**.
- Full alpha-aware rendering can be achieved with a **hybrid pipeline**.
- The current implementation is fine for now — optimization can wait until your runtime handles dynamic rendering or shader-like effects.

---

### 🧭 Future Considerations
- Investigate **NumPy-backed pixel operations** for full RGBA speed.
- Experiment with **shared surface caches** for multi-frame sprites.
- Profile differences in load time for 64×64 vs 256×256 multi-frame sprites.

---

> ✅ *Conclusion:* For GDK’s current workflow (load once, draw many), `set_at()` is acceptable. If runtime procedural effects or large asset batches appear, switch to `PixelArray` or NumPy.

