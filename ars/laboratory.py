from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .types import Form, Technique


class LabFeature(Enum):
    """Physical features of a laboratory."""

    ORGANIZED = "Organized"
    CHAOTIC = "Chaotic"
    WELL_LIT = "Well Lit"
    DARK = "Dark"
    SPACIOUS = "Spacious"
    CRAMPED = "Cramped"
    PROTECTED = "Protected"
    EXPOSED = "Exposed"
    WELL_VENTILATED = "Well Ventilated"
    STUFFY = "Stuffy"


class LabSpecialization(Enum):
    """Laboratory specializations."""

    VIS_EXTRACTION = "Vis Extraction"
    ENCHANTING = "Enchanting"
    EXPERIMENTATION = "Experimentation"
    LONGEVITY = "Longevity Rituals"
    FAMILIAR = "Familiar Binding"
    POTIONS = "Potion Brewing"


@dataclass
class LabEquipment:
    """Laboratory equipment and tools."""

    name: str
    bonus: int
    specialization: Optional[LabSpecialization] = None
    forms: List[Form] = field(default_factory=list)
    techniques: List[Technique] = field(default_factory=list)
    description: str = ""


@dataclass
class Laboratory:
    """Represents a magus's laboratory."""

    owner: str
    size: int
    features: List[LabFeature] = field(default_factory=list)
    equipment: List[LabEquipment] = field(default_factory=list)
    specializations: List[LabSpecialization] = field(default_factory=list)

    # Lab characteristics
    safety: int = 0
    health: int = 0
    aesthetics: int = 0
    upkeep: int = 0

    # Magical properties
    magical_aura: int = 0
    warping: int = 0

    # Form and technique bonuses
    form_bonuses: Dict[Form, int] = field(default_factory=dict)
    technique_bonuses: Dict[Technique, int] = field(default_factory=dict)

    def calculate_total_bonus(self, technique: Technique, form: Form) -> int:
        """Calculate total lab bonus for a specific combination."""
        base_bonus = self.safety  # Base bonus from lab safety

        # Add equipment bonuses
        for item in self.equipment:
            if technique in item.techniques or form in item.forms:
                base_bonus += item.bonus

        # Add form and technique specific bonuses
        base_bonus += self.form_bonuses.get(form, 0)
        base_bonus += self.technique_bonuses.get(technique, 0)

        # Add aura bonus
        base_bonus += self.magical_aura

        return base_bonus

    def add_equipment(self, equipment: LabEquipment) -> None:
        """Add new equipment to the laboratory."""
        self.equipment.append(equipment)

    def remove_equipment(self, equipment_name: str) -> Optional[LabEquipment]:
        """Remove equipment from the laboratory."""
        for i, item in enumerate(self.equipment):
            if item.name == equipment_name:
                return self.equipment.pop(i)
        return None

    def save(self, directory: Path = Path("ars/data/laboratories")) -> None:
        """Save laboratory to file."""
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / f"{self.owner.lower().replace(' ', '_')}_lab.yml"

        # Convert enums to strings for YAML
        data = {
            "owner": self.owner,
            "size": self.size,
            "features": [f.value for f in self.features],
            "equipment": [
                {
                    "name": e.name,
                    "bonus": e.bonus,
                    "specialization": e.specialization.value if e.specialization else None,
                    "forms": [f.value for f in e.forms],
                    "techniques": [t.value for t in e.techniques],
                    "description": e.description,
                }
                for e in self.equipment
            ],
            "specializations": [s.value for s in self.specializations],
            "safety": self.safety,
            "health": self.health,
            "aesthetics": self.aesthetics,
            "upkeep": self.upkeep,
            "magical_aura": self.magical_aura,
            "warping": self.warping,
            "form_bonuses": {k.value: v for k, v in self.form_bonuses.items()},
            "technique_bonuses": {k.value: v for k, v in self.technique_bonuses.items()},
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load(cls, owner: str, directory: Path = Path("ars/data/laboratories")) -> "Laboratory":
        """Load laboratory from file."""
        filepath = directory / f"{owner.lower().replace(' ', '_')}_lab.yml"

        with filepath.open("r") as f:
            data = yaml.safe_load(f)

            # Convert strings back to enums
            data["features"] = [LabFeature(f) for f in data["features"]]
            data["specializations"] = [LabSpecialization(s) for s in data["specializations"]]

            # Convert equipment data
            equipment = []
            for e in data["equipment"]:
                equipment.append(
                    LabEquipment(
                        name=e["name"],
                        bonus=e["bonus"],
                        specialization=LabSpecialization(e["specialization"]) if e["specialization"] else None,
                        forms=[Form(f) for f in e["forms"]],
                        techniques=[Technique(t) for t in e["techniques"]],
                        description=e["description"],
                    )
                )
            data["equipment"] = equipment

            # Convert form and technique bonuses
            data["form_bonuses"] = {Form(k): v for k, v in data["form_bonuses"].items()}
            data["technique_bonuses"] = {Technique(k): v for k, v in data["technique_bonuses"].items()}

            return cls(**data)
