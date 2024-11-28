from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from ars.serialization import Serializable


@dataclass
class ExperienceEntry(Serializable):
    amount: int
    date: datetime
    description: str
    category: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperienceEntry":
        data["date"] = datetime.fromisoformat(data["date"])
        return cls(**data)


@dataclass
class ExperienceManager(Serializable):
    total_exp: int = 0
    spent_exp: int = 0
    history: List[ExperienceEntry] = field(default_factory=list)
    exp_by_category: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperienceManager":
        manager = cls(total_exp=data["total_exp"], spent_exp=data["spent_exp"], exp_by_category=data["exp_by_category"])
        manager.history = [ExperienceEntry.from_dict(entry) for entry in data["history"]]
        return manager
