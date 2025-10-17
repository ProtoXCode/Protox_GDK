default_palette = [
    # --- 0–7 : Neutrals & Grays ---
    [0, 0, 0, 0], [0, 0, 0, 255],
    [255, 255, 255, 255],
    [230, 230, 230, 255],
    [128, 128, 128, 255],
    [64, 64, 64, 255],
    [33, 33, 33, 255],
    [16, 16, 16, 255],

    # --- 8–15 : Reds & Oranges ---
    [206, 28, 36, 255], [255, 89, 0, 255],
    [255, 140, 0, 255], [255, 185, 90, 255],
    [255, 220, 180, 255], [180, 60, 30, 255],
    [120, 30, 20, 255], [80, 20, 10, 255],

    # --- 16–23 : Yellows & Greens ---
    [255, 236, 39, 255], [255, 200, 0, 255],
    [220, 180, 60, 255], [180, 150, 30, 255],
    [0, 163, 104, 255], [0, 180, 60, 255],
    [40, 100, 30, 255], [10, 50, 10, 255],

    # --- 24–31 : Blues & Purples ---
    [0, 121, 241, 255], [99, 155, 255, 255],
    [134, 120, 252, 255], [80, 80, 200, 255],
    [118, 66, 138, 255], [233, 0, 120, 255],
    [244, 0, 161, 255], [180, 100, 220, 255],

    # --- 32–39 : Browns & Sand ---
    [143, 86, 59, 255], [180, 110, 60, 255],
    [210, 150, 100, 255], [230, 190, 140, 255],
    [255, 210, 160, 255], [120, 90, 60, 255],
    [80, 60, 40, 255], [50, 35, 20, 255],

    # --- 40–47 : Greens (extra vegetation) ---
    [60, 200, 60, 255], [90, 230, 90, 255],
    [120, 255, 120, 255], [180, 255, 180, 255],
    [40, 150, 40, 255], [25, 90, 25, 255],
    [15, 60, 15, 255], [0, 40, 0, 255],

    # --- 48–55 : Sky & Water tones ---
    [0, 190, 255, 255], [60, 210, 255, 255],
    [120, 230, 255, 255], [180, 250, 255, 255],
    [0, 140, 200, 255], [0, 90, 150, 255],
    [0, 60, 110, 255], [0, 30, 70, 255],

    # --- 56–63 : Highlights & misc ---
    [255, 255, 200, 255], [255, 255, 150, 255],
    [255, 240, 100, 255], [255, 200, 60, 255],
    [255, 170, 200, 255], [255, 150, 255, 255],
    [180, 255, 255, 255], [120, 220, 255, 255],
]

extended_palette_256 = []


def _add_range(base, count, step):
    """Generate gradient range (r, g, b, a=255)."""
    for i in range(count):
        val = [min(255, c + step * i) for c in base[:3]]
        extended_palette_256.append([*val, 255])


# --- 0–15 : Neutrals / grayscale ---
for i in range(16):
    g = int(i * 255 / 15)
    extended_palette_256.append([g, g, g, 255])

# --- 16–47 : Reds to Yellows ---
for r in range(0, 256, 16):
    extended_palette_256.append([r, 0, 0, 255])
for o in range(0, 256, 16):
    extended_palette_256.append([255, o, 0, 255])
for y in range(0, 256, 16):
    extended_palette_256.append([255, 255, y, 255])

# --- 48–79 : Greens ---
for g in range(0, 256, 16):
    extended_palette_256.append([0, g, 0, 255])
for g in range(0, 256, 16):
    extended_palette_256.append([0, g, 128, 255])
for g in range(0, 256, 16):
    extended_palette_256.append([0, g, 255, 255])

# --- 80–111 : Blues / Cyans ---
for b in range(0, 256, 16):
    extended_palette_256.append([0, 0, b, 255])
for b in range(0, 256, 16):
    extended_palette_256.append([0, 128, b, 255])
for b in range(0, 256, 16):
    extended_palette_256.append([0, 255, b, 255])

# --- 112–143 : Magentas / Purples ---
for m in range(0, 256, 16):
    extended_palette_256.append([m, 0, m, 255])
for m in range(0, 256, 16):
    extended_palette_256.append([128, 0, m, 255])
for m in range(0, 256, 16):
    extended_palette_256.append([255, 0, m, 255])

# --- 144–175 : Browns / Sands ---
browns = [
    [60, 40, 20], [90, 60, 30], [120, 80, 40],
    [150, 100, 50], [180, 120, 60], [210, 150, 90],
    [240, 180, 120], [255, 210, 150]]
for c in browns:
    extended_palette_256.append([*c, 255])
    extended_palette_256.append([min(255, c[0] + 30),
                                 min(255, c[1] + 20),
                                 min(255, c[2] + 10), 255])

# --- 176–239 : Pastels / Highlights ---
for i in range(64):
    val = 192 + int(i * 63 / 64)
    extended_palette_256.append([val, 255, val, 255])

# --- 240–255 : Transparency range / specials ---
for i in range(16):
    extended_palette_256.append([0, 0, 0, i * 16])

PALETTES = {
    'ProtoX 64': default_palette,
    'VGA 256': extended_palette_256
}
