from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

import yaml

T = TypeVar("T", bound="Serializable")


class Serializable(ABC):
    """Base class for all serializable game objects."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        if is_dataclass(self):
            data = asdict(self)
        else:
            data = self.__dict__.copy()

        # Handle special types
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Serializable):
                data[key] = value.to_dict()
            elif isinstance(value, dict):
                data[key] = {k: v.to_dict() if isinstance(v, Serializable) else v for k, v in value.items()}
            elif isinstance(value, (list, tuple)):
                data[key] = [v.to_dict() if isinstance(v, Serializable) else v for v in value]

        return data

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create object from dictionary."""
        pass

    def save(self, path: Path) -> None:
        """Save object to file."""
        with path.open("w") as f:
            yaml.safe_dump(self.to_dict(), f)

    @classmethod
    def load(cls: Type[T], path: Path) -> T:
        """Load object from file."""
        with path.open("r") as f:
            data = yaml.safe_load(f)
            return cls.from_dict(data)
