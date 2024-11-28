from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import yaml

from ars.events import Event, EventRecorder, EventManager
from ars.experience import ExperienceManager
from ars.serialization import Serializable
from ars.core.types import (
    AbilityType, Characteristic, House, ItemType, Season, 
    EventType, Form, Technique  # Add Form and Technique imports
)
from ars.virtues_flaws import VirtueFlaw
from ars.core.base_types import BaseCharacter


if TYPE_CHECKING:
    from ars.magic_items import MagicItem
    from ars.spells import Spell


class CharacterNotFoundError(Exception):
    """Raised when a character cannot be found."""

    pass


@dataclass
class Character(Serializable, EventRecorder, BaseCharacter):
    """Represents a character in Ars Magica."""

    name: str
    player: str
    saga: str
    covenant: str
    house: House
    age: int = 25
    apparent_age: Optional[int] = None

    # Core attributes
    size: int = 0
    warping_points: int = 0
    confidence: int = 0
    warping_score: int = 0
    decrepitude_score: int = 0
    decrepitude_points: int = 0

    # Characteristics
    characteristics: Dict[Characteristic, int] = field(default_factory=dict)

    # Personality
    personality_traits: Dict[str, int] = field(default_factory=dict)
    virtues: List[VirtueFlaw] = field(default_factory=list)
    flaws: List[VirtueFlaw] = field(default_factory=list)

    # Magic abilities
    techniques: Dict[Technique, int] = field(default_factory=dict)
    forms: Dict[Form, int] = field(default_factory=dict)

    # Skills and abilities
    abilities: Dict[AbilityType, Dict[str, int]] = field(
        default_factory=lambda: {ability_type: {} for ability_type in AbilityType}
    )

    # Specializations
    specializations: Dict[str, int] = field(default_factory=dict)

    # Rituals
    longevity_ritual_bonus: int = 0
    magic_items: List["MagicItem"] = field(default_factory=list)

    # Spells
    spells: Dict[str, 'Spell'] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize after dataclass creation."""
        EventRecorder.__init__(self)  # Initialize EventRecorder
        super().__post_init__()  # Call parent's post_init if it exists
        self.event_manager = None
        if not self.apparent_age:
            self.apparent_age = self.age
        self.experience = ExperienceManager()
        
        # Initialize arts
        for technique in Technique:
            if technique not in self.techniques:
                self.techniques[technique] = 0
                
        for form in Form:
            if form not in self.forms:
                self.forms[form] = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        # Handle special conversions
        data["house"] = House(data["house"])

        # Convert characteristics
        char_data = data.pop("characteristics")
        data["characteristics"] = {Characteristic[name]: value for name, value in char_data.items()}

        # Convert abilities
        abilities_data = data.pop("abilities")
        data["abilities"] = {AbilityType[type_name]: abilities for type_name, abilities in abilities_data.items()}

        # Convert techniques and forms to enums
        tech_data = data.pop("techniques", {})
        form_data = data.pop("forms", {})
        data["techniques"] = {Technique[name]: value for name, value in tech_data.items()}
        data["forms"] = {Form[name]: value for name, value in form_data.items()}

        # Convert virtues and flaws
        data["virtues"] = [VirtueFlaw.from_dict(v) for v in data.get("virtues", [])]
        data["flaws"] = [VirtueFlaw.from_dict(f) for f in data.get("flaws", [])]

        # Create instance
        char = cls(**data)

        # Handle experience separately
        if "experience" in data:
            char.experience = ExperienceManager.from_dict(data["experience"])

        return char

    def add_virtue(self, virtue: VirtueFlaw) -> None:
        """Add a virtue to the character."""
        if virtue.is_virtue:
            self.virtues.append(virtue)
        else:
            raise ValueError("Attempted to add a flaw as a virtue")

    def add_flaw(self, flaw: VirtueFlaw) -> None:
        """Add a flaw to the character."""
        if not flaw.is_virtue:
            self.flaws.append(flaw)
        else:
            raise ValueError("Attempted to add a virtue as a flaw")

    def add_personality_trait(self, trait: str, value: int) -> None:
        """Add or update a personality trait."""
        self.personality_traits[trait] = value

    def save(self, directory: Path = Path("ars/data/characters")) -> None:
        """Save character to file."""
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / f"{self.name.lower().replace(' ', '_')}.yml"

        # Convert enum keys to strings for YAML
        data = self.__dict__.copy()
        data["abilities"] = {type_name.name: abilities for type_name, abilities in self.abilities.items()}
        data["house"] = self.house.value
        
        # Convert techniques and forms to strings
        data["techniques"] = {tech.name: value for tech, value in self.techniques.items()}
        data["forms"] = {form.name: value for form, value in self.forms.items()}

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load(cls, name: str, directory: Path = Path("ars/data/characters")) -> "Character":
        """Load character from file."""
        filepath = directory / f"{name.lower().replace(' ', '_')}.yml"

        try:
            with filepath.open("r") as f:
                data = yaml.safe_load(f)

                # Convert string ability types back to enum
                abilities_data = data.pop("abilities")
                data["abilities"] = {
                    AbilityType[type_name]: abilities for type_name, abilities in abilities_data.items()
                }

                # Convert house string back to enum
                data["house"] = House[data["house"].upper()]

                return cls(**data)
        except FileNotFoundError as err:
            raise CharacterNotFoundError(f"Character '{name}' not found") from err

    @staticmethod
    def list_characters(directory: Path = Path("ars/data/characters")) -> list[str]:
        """List all saved characters."""
        directory.mkdir(parents=True, exist_ok=True)
        return [f.stem for f in directory.glob("*.yml")]

    def add_exp(self, amount: int, description: str, category: str) -> None:
        self.experience.add_experience(amount, description, category)

    def can_improve(self, category: str, cost: int) -> bool:
        return self.experience.get_available_exp() >= cost

    def improve_ability(self, category: str, cost: int) -> bool:
        return self.experience.spend_experience(cost, category)

    def can_enchant(self, item_type: ItemType) -> bool:
        """Check if character can create given type of magic item."""
        if not hasattr(self, "abilities"):
            return False

        magic_theory = self.abilities.get("Magic Theory", 0)

        requirements = {
            ItemType.CHARGED: 3,
            ItemType.INVESTED: 5,
            ItemType.LESSER: 8,
            ItemType.GREATER: 12,
            ItemType.TALISMAN: 15,
        }

        return magic_theory >= requirements[item_type]

    def add_experience(self, ability: str, points: int) -> None:
        """Add experience points to an ability."""
        current_value = self.abilities.get(ability, 0)
        self.abilities[ability] = current_value + points

        self.record_event(
            event_type=EventType.EXPERIENCE_GAIN,
            details={
                "ability": ability,
                "points_gained": points,
                "new_value": self.abilities[ability]
            }
        )

    def add_warping_points(self, points: int, source: str) -> None:
        """Add warping points and check for score increase."""
        self.warping_points += points
        old_score = self.warping_score

        # Check for warping score increase
        self.warping_score = self.warping_points // 5
        gained_score = self.warping_score - old_score

        self.record_event(
            event_type=EventType.WARPING,
            details={
                "points_gained": points,
                "source": source,
                "total_points": self.warping_points,
                "score_increased": gained_score > 0,
                "new_score": self.warping_score
            }
        )

    def add_decrepitude_points(self, points: int, source: str) -> None:
        """Add decrepitude points and check for score increase."""
        self.decrepitude_points += points
        old_score = self.decrepitude_score

        # Check for decrepitude score increase
        self.decrepitude_score = self.decrepitude_points // 5
        gained_score = self.decrepitude_score - old_score

        self.record_event(
            event_type=EventType.AGING,
            details={
                "points_gained": points,
                "source": source,
                "total_points": self.decrepitude_points,
                "score_increased": gained_score > 0,
                "new_score": self.decrepitude_score
            }
        )

    def add_spell(self, spell: 'Spell') -> None:
        """Add a spell to the character's repertoire."""
        self.spells[spell.name] = spell
        
        self.record_event(
            event_type=EventType.SPELLCASTING,
            details={
                "action": "learn_spell",
                "spell_name": spell.name,
                "spell_level": spell.level
            }
        )

    def cast_spell(self, spell: 'Spell', **kwargs) -> 'SpellCastingResult':
        """Cast a spell using the current game context for temporal information."""
        # Calculate casting result
        result = self._calculate_spell_result(spell, **kwargs)
        
        self.record_event(
            event_type=EventType.SPELLCASTING,
            details={
                "spell_name": spell.name,
                "casting_total": result.casting_total,
                "success": result.success
            }
        )
        
        return result
