# 📦 GDKIMG File Format Specification — v0.1

> **ProtoX Game Developer Kit — Binary Sprite Format**  
> Author: ProtoX  
> Status: Draft

---

## 🧩 Overview

The **GDKIMG** format is the binary equivalent of the `.sprite.json` asset used in the **ProtoX GDK** toolchain. It is designed for **fast loading**, **low I/O overhead**, and **easy runtime parsing** while preserving the same conceptual structure as the JSON-based source data.

It is primarily intended for use in the **GDK Runtime**, where assets must be loaded rapidly during gameplay or preloading stages.

---

## 🧱 Design Goals

- ⚡ **Fast load time** — no JSON parsing required.
- 💾 **Compact storage** — uses byte-level encoding with optional compression.
- 🔒 **Immutable** — optimized for distribution, not editing.
- 🧠 **Schema-aligned** — compatible with the same metadata fields as `.sprite.json`.
- 🧩 **Cross-platform** — endian-safe and portable.

---

## 📘 File Structure

| Section              | Size     | Description                            |
|----------------------|----------|----------------------------------------|
| **Header**           | 16 bytes | Identifies format and version          |
| **Palette**          | variable | Array of RGBA color entries            |
| **Frame Index Data** | variable | Raw pixel indices (per frame)          |
| **Metadata (TLV)**   | variable | Optional name, author, fps, tags, etc. |

---

## 🧩 Header (16 bytes)

| Offset   | Type      | Field        | Description                        |
|----------|-----------|--------------|------------------------------------|
| `0x00`   | `char[6]` | Magic        | Always `"GDKIMG"`                  |
| `0x06`   | `uint8`   | Version      | File format version (0x01)         |
| `0x07`   | `uint8`   | Flags        | Bit flags (e.g., compression, RLE) |
| `0x08`   | `uint16`  | Width        | Sprite width in pixels             |
| `0x0A`   | `uint16`  | Height       | Sprite height in pixels            |
| `0x0C`   | `uint16`  | Frames       | Number of animation frames         |
| `0x0E`   | `uint16`  | PaletteCount | Number of palette colors           |

> **Note:** All integer values are little-endian unless otherwise stated.

---

## 🎨 Palette Section

Immediately following the header, a sequence of `PaletteCount` RGBA entries defines the available colors.

Each color is 4 bytes: `(R, G, B, A)` — all `uint8`.

```
for i in range(PaletteCount):
    R, G, B, A = read(4)
```

Total palette size = `PaletteCount * 4` bytes.

---

## 🖼️ Frame Data Section

For each frame, pixel data is stored as a row-major sequence of **palette indices** (`uint8`), optionally compressed using RLE.

### Uncompressed layout:
```
Frame 0 → [index0, index1, ..., index(N)]
Frame 1 → [index0, index1, ..., index(N)]
```

Each frame is `Width * Height` bytes.

### RLE Compression (optional)
If flag bit 0x01 is set, data is compressed in `(count, value)` pairs:
```
[count:uint8][value:uint8]
```
Where `count` = number of times `value` repeats.

Example:
```
(5,3)(2,4)(1,0)  →  [3,3,3,3,3,4,4,0]
```

---

## 🧠 Metadata Section (TLV)

At the end of the file, an optional **TLV** (Type-Length-Value) structure contains string metadata for compatibility with the `.sprite.json` source.

| Typ-e  | Des-cription | Enco-ding               |
|--------|--------------|-------------------------|
| `0x01` | Name         | UTF-8 string            |
| `0x02` | Author       | UTF-8 string            |
| `0x03` | Tags         | Comma-separated string  |
| `0x04` | FPS          | uint8                   |
| `0x05` | Loop         | uint8 (1=True, 0=False) |

Each TLV entry:
```
[Type:uint8][Length:uint16][Value:bytes]
```

---

## ⚙️ Example Layout

```
Offset  Size   Description
0x0000  6      "GDKIMG"
0x0006  1      Version = 1
0x0007  1      Flags = 0
0x0008  2      Width = 16
0x000A  2      Height = 16
0x000C  2      Frames = 2
0x000E  2      PaletteCount = 64
0x0010  256    Palette (64 * 4 bytes)
0x0110  512    Frame 0 (16x16)
0x0310  512    Frame 1 (16x16)
0x0510  TLV    Metadata (name, author, fps...)
```

---

## 🔒 Checksum (future spec v0.2)

Future versions may add an optional CRC32 checksum appended after the metadata section:
```
[0xFF][Length=4][CRC32]
```

This would help validate file integrity during runtime loading.

---

## 🧰 Conversion Flow

### Export (Editor → Binary)
```
JSON (.sprite.json)
   ↓
Serialize + Pack
   ↓
Binary (.gdkimg)
```

### Import (Runtime → Sprite Object)
```
Binary (.gdkimg)
   ↓
Parse + Map to Surface
   ↓
Drawable Sprite
```

---

## 🧪 Notes

- JSON and GDKIMG share schema compatibility.
- GDKIMG is **lossless** — it can be decompiled back to JSON.
- Ideal for runtime distribution in packaged games or build pipelines.

---

> *“Readable in dev, blazingly fast in runtime — GDKIMG is the bridge between imagination and execution.”*
