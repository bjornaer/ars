from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ars.core.types import Season

@dataclass
class BaseMagicItem:
    """Base class for magic items."""
    name: str = ""
    level: int = 0
    description: str = ""
    creator: Optional[str] = None
    creation_date: Optional[Dict[str, any]] = None

@dataclass
class BaseCharacter:
    """Base class containing shared character attributes."""
    name: str
    player: str
    saga: str
    covenant: str
    house: Optional[str] = None
    age: int = 25
    warping_points: int = 0
    fatigue_level: int = 0 