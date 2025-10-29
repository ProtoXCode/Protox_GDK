from dataclasses import dataclass
from typing import Any

@dataclass
class ProjectDoc:
    project_name: str = 'unnamed'
    author: str = 'unknown'
    properties: dict[str, Any] = None

    @staticmethod
    def new(name: str, author: str = 'unknown') -> 'ProjectDoc':
        """ Create a new project document with defaults. """
        return ProjectDoc(
            project_name=name,
            author=author,
            properties={
                'game_type': 'Platformer',
                'gravity': True,
                'resolution': (800, 600),
                'fullscreen': False
            }
        )

    def to_json(self) -> dict[str, Any]:
        """ Serialize to JSON-compatible dictionary. """
        return {
            'project_name': self.project_name,
            'author': self.author,
            'properties': self.properties or {}
        }

    @staticmethod
    def from_json(data: dict[str, Any]) -> 'ProjectDoc':
        """ Rebuild a ProjectDoc from a dictionary. """
        return ProjectDoc(
            project_name=data.get('project_name'),
            author=data.get('author', 'unknown'),
            properties=data.get('properties', {})
        )
