from dataclasses import dataclass
from typing import Any

@dataclass
class LevelDoc:
    name: str = 'unnamed'
    author: str = 'unnamed'
    properties: dict[str, Any] = None
