from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ars.events import EventRecorder, EventType
from ars.core.types import Season
from ars.serialization import Serializable
from ars.core.types import Form, Technique


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
class LabEquipment(Serializable):
    """Laboratory equipment and tools."""

    name: str
    bonus: int
    specialization: Optional[LabSpecialization] = None
    forms: List[Form] = field(default_factory=list)
    techniques: List[Technique] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabEquipment":
        if data.get("specialization"):
            data["specialization"] = LabSpecialization(data["specialization"])
        if "forms" in data:
            data["forms"] = [Form(f) for f in data["forms"]]
        if "techniques" in data:
            data["techniques"] = [Technique(t) for t in data["techniques"]]
        return cls(**data)


@dataclass
class Laboratory(EventRecorder):
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
    location: str = "Covenant"

    # Magical properties
    magical_aura: int = 0
    warping: int = 0

    # Form and technique bonuses
    form_bonuses: Dict[Form, int] = field(default_factory=dict)
    technique_bonuses: Dict[Technique, int] = field(default_factory=dict)

    # Activity modifiers
    activity_modifiers: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Laboratory":
        # Convert enums
        if "features" in data:
            data["features"] = [LabFeature(f) for f in data["features"]]
        if "specializations" in data:
            data["specializations"] = [LabSpecialization(s) for s in data["specializations"]]

        # Convert equipment
        if "equipment" in data:
            data["equipment"] = [LabEquipment.from_dict(e) for e in data["equipment"]]

        # Convert form and technique bonuses
        if "form_bonuses" in data:
            data["form_bonuses"] = {Form(k): v for k, v in data["form_bonuses"].items()}
        if "technique_bonuses" in data:
            data["technique_bonuses"] = {Technique(k): v for k, v in data["technique_bonuses"].items()}

        return cls(**data)

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

    def calculate_extraction_bonus(self) -> int:
        """Calculate laboratory's bonus to vis extraction."""
        bonus = self.activity_modifiers.get("vis_extraction", 0)
        bonus += self.magical_aura // 2

        # Add specialization bonus
        if LabSpecialization.VIS_EXTRACTION in self.specializations:
            bonus += 3  # Standard bonus for specialization

        return bonus

    def calculate_enchantment_bonus(self) -> int:
        """Calculate laboratory's enchantment bonus."""
        bonus = 0

        # Specialization bonus
        if LabSpecialization.ENCHANTING in self.specializations:
            bonus += 3

        # Equipment bonus
        bonus += sum(item.bonus for item in self.equipment if item.specialization == LabSpecialization.ENCHANTING)

        # Size bonus
        bonus += max(0, self.size - 2)

        # Activity modifier
        bonus += self.activity_modifiers.get("enchanting", 0)

        return bonus

    def add_feature(self, feature: LabFeature) -> None:
        """Add a physical feature to the laboratory."""
        if feature not in self.features:
            self.features.append(feature)
            # Update characteristics based on feature
            if feature in [LabFeature.ORGANIZED, LabFeature.PROTECTED, LabFeature.WELL_VENTILATED]:
                self.safety += 1
            elif feature in [LabFeature.CHAOTIC, LabFeature.EXPOSED, LabFeature.STUFFY]:
                self.safety -= 1

    def add_specialization(self, spec: LabSpecialization) -> None:
        """Add a specialization to the laboratory."""
        if spec not in self.specializations:
            self.specializations.append(spec)

    def perform_activity(self, activity_type: str, details: Dict[str, any], year: int, season: Season) -> None:
        """Record laboratory activity."""
        self.record_event(
            type=EventType.LABORATORY_WORK,
            description=f"Laboratory activity: {activity_type} in {self.owner}'s laboratory",
            details={
                "owner": self.owner,
                "activity_type": activity_type,
                "activity_details": details,
                "laboratory_conditions": {
                    "size": self.size,
                    "aura": self.magical_aura,
                    "safety": self.safety,
                    "specializations": [spec.value for spec in self.specializations],
                },
            },
            year=year,
            season=season,
        )
