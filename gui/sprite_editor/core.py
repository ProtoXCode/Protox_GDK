from dataclasses import dataclass
from typing import Any

from gdk.palette import PALETTES


@dataclass
class SpriteFrame:
    """Represents a single frame (2D matrix of palette indices)."""
    pixels: list[list[int]]


@dataclass
class SpriteDoc:
    """Serializable sprite document with metadata, palette, and frames."""

    width: int
    height: int
    palette: list[list[int]]
    frames: list[SpriteFrame]
    name: str = 'unnamed'
    fps: int = 10
    loop: bool = True
    author: str = 'unknown'
    tags: list[str] = None
    properties: dict[str, Any] = None
    palette_name: str = 'ProtoX 64'

    # -------------------------------------------------------------------------
    # Factory
    # -------------------------------------------------------------------------
    @staticmethod
    def empty(width: int, height: int, palette: list[list[int]],
              name: str = 'unnamed',
              palette_name: str = 'ProtoX 64') -> "SpriteDoc":
        """Create an empty sprite with a blank frame and default metadata."""
        blank = [[-1 for _ in range(width)] for _ in range(height)]
        return SpriteDoc(
            width=width,
            height=height,
            palette=palette,
            palette_name=palette_name,
            frames=[SpriteFrame(blank)],
            name=name,
            tags=[],
            properties={
                'collision': False,
                'static': False,
                'background': False,
                'player': False,
            }
        )

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    def to_json(self) -> dict:
        """Convert this sprite document into a JSON-compatible dict."""
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'loop': self.loop,
            'author': self.author,
            'tags': self.tags or [],
            'palette_name': self.palette_name,
            'palette': self.palette,
            'frames': [f.pixels for f in self.frames],
            'properties': self.properties or {},
        }

    @staticmethod
    def from_json(d: dict) -> "SpriteDoc":
        """Reconstruct a SpriteDoc from JSON data."""
        palette_name = d.get('palette_name', 'ProtoX 64')
        palette = PALETTES.get(palette_name, d.get('palette', []))

        return SpriteDoc(
            name=d.get('name', 'unnamed'),
            width=int(d['width']),
            height=int(d['height']),
            fps=int(d.get('fps', 10)),
            loop=bool(d.get('loop', True)),
            author=d.get('author', 'unknown'),
            tags=d.get('tags', []),
            palette=palette,
            palette_name=palette_name,
            frames=[
                SpriteFrame([[int(v) for v in row] for row in m])
                for m in d['frames']
            ],
            properties=d.get(
                'properties',
                {
                    'collision': False,
                    'static': False,
                    'background': False,
                    'player': False,
                },
            ),
        )
