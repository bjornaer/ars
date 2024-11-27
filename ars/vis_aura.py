from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from .types import Form


class AuraType(Enum):
    """Types of magical auras."""

    MAGIC = "Magic"
    FAERIE = "Faerie"
    DIVINE = "Divine"
    INFERNAL = "Infernal"
    DOMINION = "Dominion"


class VisType(Enum):
    """Types of vis."""

    RAW = "Raw"
    PROCESSED = "Processed"
    ENCHANTED = "Enchanted"


@dataclass
class AuraProperties:
    """Properties of a magical aura."""

    type: AuraType
    strength: int
    properties: List[str] = field(default_factory=list)
    modifiers: Dict[str, int] = field(default_factory=dict)
    fluctuations: Dict[str, int] = field(default_factory=dict)

    def calculate_effective_strength(self, season: str = None) -> int:
        """Calculate effective aura strength including fluctuations."""
        base = self.strength
        if season and season in self.fluctuations:
            base += self.fluctuations[season]
        return max(0, base)


@dataclass
class VisSource:
    """A source of magical vis."""

    form: Form
    amount: int
    type: VisType = VisType.RAW
    season: Optional[str] = None
    location: str = ""
    description: str = ""
    properties: List[str] = field(default_factory=list)
    last_collected: Optional[int] = None


class AuraManager:
    """Manages magical auras and their effects."""

    def __init__(self):
        self.auras: Dict[str, AuraProperties] = {}

    def register_aura(self, location: str, aura: AuraProperties) -> None:
        """Register a new aura."""
        self.auras[location] = aura

    def get_aura(self, location: str) -> Optional[AuraProperties]:
        """Get aura properties for a location."""
        return self.auras.get(location)

    def calculate_aura_effects(self, location: str, activity_type: str, season: str = None) -> Dict[str, int]:
        """Calculate aura effects on an activity."""
        aura = self.get_aura(location)
        if not aura:
            return {}

        effects = {}
        strength = aura.calculate_effective_strength(season)

        # Base effects by aura type
        if aura.type == AuraType.MAGIC:
            effects["magical_activities"] = strength
            effects["spell_casting"] = strength
            effects["vis_extraction"] = strength
        elif aura.type == AuraType.FAERIE:
            effects["faerie_magic"] = strength
            effects["glamour"] = strength // 2
        elif aura.type == AuraType.DIVINE:
            effects["divine_power"] = strength
            effects["magic_resistance"] = strength
        elif aura.type == AuraType.INFERNAL:
            effects["corruption"] = strength
            effects["demonic_power"] = strength

        # Add specific modifiers
        effects.update(aura.modifiers)

        return effects


class VisManager:
    """Manages vis sources and collection."""

    def __init__(self):
        self.sources: Dict[str, VisSource] = {}
        self.stocks: Dict[Form, int] = {form: 0 for form in Form}

    def register_source(self, name: str, source: VisSource) -> None:
        """Register a new vis source."""
        self.sources[name] = source

    def collect_vis(self, source_name: str, year: int, season: str, aura_strength: int = 0) -> Tuple[Form, int]:
        """Attempt to collect vis from a source."""
        source = self.sources.get(source_name)
        if not source:
            return None, 0

        # Check if already collected this year
        if source.last_collected == year:
            return source.form, 0

        # Check if correct season
        if source.season and source.season != season:
            return source.form, 0

        # Calculate amount with aura bonus
        amount = source.amount + (aura_strength // 2)

        # Add to stocks
        self.stocks[source.form] += amount
        source.last_collected = year

        return source.form, amount

    def use_vis(self, form: Form, amount: int) -> bool:
        """Attempt to use vis from stocks."""
        if self.stocks[form] >= amount:
            self.stocks[form] -= amount
            return True
        return False

    def transfer_vis(self, form: Form, amount: int, target_manager: "VisManager") -> bool:
        """Transfer vis to another manager."""
        if self.use_vis(form, amount):
            target_manager.stocks[form] += amount
            return True
        return False

    def save(self, filepath: Path) -> None:
        """Save vis data to file."""
        data = {
            "sources": {
                name: {
                    "form": source.form.value,
                    "amount": source.amount,
                    "type": source.type.value,
                    "season": source.season,
                    "location": source.location,
                    "description": source.description,
                    "properties": source.properties,
                    "last_collected": source.last_collected,
                }
                for name, source in self.sources.items()
            },
            "stocks": {form.value: amount for form, amount in self.stocks.items()},
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load(cls, filepath: Path) -> "VisManager":
        """Load vis data from file."""
        manager = cls()

        with filepath.open("r") as f:
            data = yaml.safe_load(f)

            # Load sources
            for name, source_data in data.get("sources", {}).items():
                source = VisSource(
                    form=Form(source_data["form"]),
                    amount=source_data["amount"],
                    type=VisType(source_data["type"]),
                    season=source_data["season"],
                    location=source_data["location"],
                    description=source_data["description"],
                    properties=source_data["properties"],
                    last_collected=source_data["last_collected"],
                )
                manager.register_source(name, source)

            # Load stocks
            for form_name, amount in data.get("stocks", {}).items():
                manager.stocks[Form(form_name)] = amount

        return manager
