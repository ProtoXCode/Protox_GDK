from dataclasses import dataclass
from typing import Any


@dataclass
class SceneDoc:
    name: str = 'unnamed'
    author: str = 'unnamed'
    properties: dict[str, Any] = None
