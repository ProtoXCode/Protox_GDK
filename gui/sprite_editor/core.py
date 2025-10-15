from dataclasses import dataclass
from typing import Any


@dataclass
class SpriteFrame:
    # 2D matrix: int palette index or -1 for transparent
    pixels: list[list[int]]


@dataclass
class SpriteDoc:
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

    @staticmethod
    def empty(width: int, height: int, palette: list[list[int]],
              name: str = 'unnamed') -> 'SpriteDoc':
        blank = [[-1 for _ in range(width)] for _ in range(height)]
        return SpriteDoc(width=width, height=height, palette=palette,
                         frames=[SpriteFrame(blank)], name=name, tags=[],
                         properties={
                             'collision': False,
                             'static': False,
                             'background': False,
                             'player': False
                         })

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'loop': self.loop,
            'author': self.author,
            'tags': self.tags,
            'palette': self.palette,
            'frames': [f.pixels for f in self.frames],
            'properties': self.properties or {}
        }

    @staticmethod
    def from_json(d: dict) -> 'SpriteDoc':
        return SpriteDoc(
            name=d.get('name', 'unnamed'),
            width=int(d['width']),
            height=int(d['height']),
            fps=int(d.get('fps', 10)),
            loop=bool(d.get('loop', True)),
            author=d.get('author', 'unknown'),
            tags=d.get('tags', []),
            palette=[list(map(int, rgba)) for rgba in d['palette']],
            frames=[SpriteFrame(
                [[int(v) for v in row] for row in m]) for m in d['frames']],
            properties=d.get('properties', {
                'collision': False,
                'static': False,
                'background': False,
                'player': False
            })
        )
