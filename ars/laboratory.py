from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml

from ars.core.types import Form, Technique


class LabFeature(Enum):
    """Laboratory features that affect its capabilities."""
    ORGANIZED = auto()
    WELL_LIT = auto()
    SECURE = auto()
    MAINTAINED = auto()
    REINFORCED = auto()
    INSULATED = auto()


class LabSpecialization(Enum):
    """Types of laboratory specializations."""
    POTIONS = auto()
    VIS_EXTRACTION = auto()
    ENCHANTING = auto()
    EXPERIMENTATION = auto()
    LONGEVITY = auto()


@dataclass
class LabEquipment:
    """Equipment that can be installed in a laboratory."""
    name: str
    bonus: int
    specialization: Optional[LabSpecialization] = None
    forms: Set[Form] = field(default_factory=set)
    techniques: Set[Technique] = field(default_factory=set)
    description: str = ""

    def to_dict(self) -> dict:
        """Convert equipment to dictionary for serialization."""
        return {
            'name': self.name,
            'bonus': self.bonus,
            'specialization': self.specialization.name if self.specialization else None,
            'forms': [form.name for form in self.forms],
            'techniques': [tech.name for tech in self.techniques],
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LabEquipment':
        """Create equipment from dictionary."""
        return cls(
            name=data['name'],
            bonus=data['bonus'],
            specialization=LabSpecialization[data['specialization']] if data['specialization'] else None,
            forms={Form[form] for form in data['forms']},
            techniques={Technique[tech] for tech in data['techniques']},
            description=data['description']
        )

    def save(self, path: Path) -> None:
        """Save equipment to file."""
        with open(path, 'w') as f:
            yaml.safe_dump(self.to_dict(), f)

    @classmethod
    def load(cls, path: Path) -> 'LabEquipment':
        """Load equipment from file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return cls.from_dict(data)


@dataclass
class Laboratory:
    """A magical laboratory where research and experimentation occur."""
    owner: str
    size: int
    magical_aura: int = 0
    safety: int = 0
    health: int = 0
    aesthetics: int = 0
    upkeep: int = 0
    equipment: List[LabEquipment] = field(default_factory=list)
    features: List[LabFeature] = field(default_factory=list)
    specializations: List[LabSpecialization] = field(default_factory=list)
    form_bonuses: Dict[Form, int] = field(default_factory=dict)
    technique_bonuses: Dict[Technique, int] = field(default_factory=dict)

    def add_equipment(self, equipment: LabEquipment) -> None:
        """Add equipment to the laboratory."""
        self.equipment.append(equipment)

    def remove_equipment(self, equipment_name: str) -> Optional[LabEquipment]:
        """Remove equipment from the laboratory."""
        for i, eq in enumerate(self.equipment):
            if eq.name == equipment_name:
                return self.equipment.pop(i)
        return None

    def add_feature(self, feature: LabFeature) -> None:
        """Add a feature to the laboratory."""
        if feature not in self.features:
            self.features.append(feature)

    def add_specialization(self, specialization: LabSpecialization) -> None:
        """Add a specialization to the laboratory."""
        if specialization not in self.specializations:
            self.specializations.append(specialization)

    def calculate_total_bonus(self, technique: Technique, form: Form) -> int:
        """Calculate total bonus for a specific technique and form combination."""
        total = self.safety + self.magical_aura
        total += self.form_bonuses.get(form, 0)
        total += self.technique_bonuses.get(technique, 0)

        for equipment in self.equipment:
            if form in equipment.forms or technique in equipment.techniques:
                total += equipment.bonus

        return total

    def to_dict(self) -> dict:
        """Convert laboratory to dictionary for serialization."""
        return {
            'owner': self.owner,
            'size': self.size,
            'magical_aura': self.magical_aura,
            'safety': self.safety,
            'health': self.health,
            'aesthetics': self.aesthetics,
            'upkeep': self.upkeep,
            'equipment': [eq.to_dict() for eq in self.equipment],
            'features': [feature.name for feature in self.features],
            'specializations': [spec.name for spec in self.specializations],
            'form_bonuses': {form.name: bonus for form, bonus in self.form_bonuses.items()},
            'technique_bonuses': {tech.name: bonus for tech, bonus in self.technique_bonuses.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Laboratory':
        """Create laboratory from dictionary."""
        lab = cls(
            owner=data['owner'],
            size=data['size'],
            magical_aura=data['magical_aura'],
            safety=data['safety'],
            health=data['health'],
            aesthetics=data['aesthetics'],
            upkeep=data['upkeep']
        )
        
        lab.equipment = [LabEquipment.from_dict(eq) for eq in data['equipment']]
        lab.features = [LabFeature[feature] for feature in data['features']]
        lab.specializations = [LabSpecialization[spec] for spec in data['specializations']]
        lab.form_bonuses = {Form[form]: bonus for form, bonus in data['form_bonuses'].items()}
        lab.technique_bonuses = {Technique[tech]: bonus for tech, bonus in data['technique_bonuses'].items()}
        
        return lab

    def save(self, directory: Path | None = None) -> None:
        """Save laboratory to file."""
        if directory is None:
            directory = Path.cwd()
        path = directory / f"{self.owner}_laboratory.yml"
        with open(path, 'w') as f:
            yaml.safe_dump(self.to_dict(), f)

    @classmethod
    def load(cls, owner: str, directory: Path = None) -> 'Laboratory':
        """Load laboratory from file."""
        if directory is None:
            directory = Path.cwd()
        path = directory / f"{owner}_laboratory.yml"
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return cls.from_dict(data)
