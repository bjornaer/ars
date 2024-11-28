from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict


class AbilityType(Enum):
    """Types of abilities in Ars Magica."""

    ACADEMIC = auto()
    ARCANE = auto()
    MARTIAL = auto()
    GENERAL = auto()


class House(Enum):
    """Houses of Hermes."""

    BONISAGUS = "Bonisagus"
    FLAMBEAU = "Flambeau"
    TREMERE = "Tremere"
    JERBITON = "Jerbiton"
    MERCERE = "Mercere"
    MERINITA = "Merinita"
    BJORNAER = "Bjornaer"
    CRIAMON = "Criamon"
    TYTALUS = "Tytalus"
    VERDITIUS = "Verditius"
    GUERNICUS = "Guernicus"
    EX_MISCELLANEA = "Ex Miscellanea"


class Range(Enum):
    """Spell ranges in Ars Magica."""

    PERSONAL = "Personal"
    TOUCH = "Touch"
    SIGHT = "Sight"
    VOICE = "Voice"
    ARCANE_CONNECTION = "Arcane Connection"


class Duration(Enum):
    """Spell durations in Ars Magica."""

    MOMENTARY = "Momentary"
    CONCENTRATION = "Concentration"
    DIAMETER = "Diameter"
    SUN = "Sun"
    MOON = "Moon"
    YEAR = "Year"


class Target(Enum):
    """Spell target types in Ars Magica."""

    INDIVIDUAL = "Individual"
    GROUP = "Group"
    ROOM = "Room"
    STRUCTURE = "Structure"
    BOUNDARY = "Boundary"


class Form(Enum):
    """Hermetic Forms of magic."""
    ANIMAL = auto()
    AQUAM = auto()
    AURAM = auto()
    CORPUS = auto()
    HERBAM = auto()
    IGNEM = auto()
    IMAGINEM = auto()
    MENTEM = auto()
    TERRAM = auto()
    VIM = auto()


class Technique(Enum):
    """Hermetic Techniques of magic."""
    CREO = auto()
    INTELLEGO = auto()
    MUTO = auto()
    PERDO = auto()
    REGO = auto()


class Characteristic(Enum):
    """Characteristics in Ars Magica."""

    STRENGTH = "Strength"
    DEXTERITY = "Dexterity"
    ENDURANCE = "Endurance"
    INTELLIGENCE = "Intelligence"
    WISDOM = "Wisdom"
    CHARISMA = "Charisma"


class ItemType(Enum):
    """Types of magic items."""

    CHARGED = "Charged Item"
    INVESTED = "Invested Device"
    LESSER = "Lesser Enchanted Item"
    GREATER = "Greater Enchanted Item"
    TALISMAN = "Talisman"


class InstallationType(Enum):
    """Types of effect installations."""

    EFFECT = "Effect"
    TRIGGER = "Trigger"
    ENVIRONMENTAL = "Environmental Trigger"
    LINKED = "Linked Trigger"
    RESTRICTED = "Use Restriction"

from enum import Enum, auto

class Season(Enum):
    """The four seasons of the year."""
    SPRING = "Spring"
    SUMMER = "Summer"
    AUTUMN = "Autumn"
    WINTER = "Winter"

    @classmethod
    def next_season(cls, current: "Season") -> "Season":
        """Get the next season in sequence."""
        seasons = list(cls)
        current_idx = seasons.index(current)
        return seasons[(current_idx + 1) % 4]

class ActivityType(Enum):
    """Types of seasonal activities."""
    STUDY = "Study"
    RESEARCH = "Research"
    TEACH = "Teach"
    LEARN = "Learn"
    PRACTICE = "Practice"
    ADVENTURE = "Adventure"
    COVENANT_SERVICE = "Covenant Service"
    WRITE = "Write"
    EXTRACT_VIS = "Extract Vis"
    ENCHANT_ITEM = "Enchant Item"
    LONGEVITY_RITUAL = "Longevity Ritual"
@dataclass
class SeasonalActivity:
    """An activity performed during a season."""

    type: ActivityType
    character: str
    season: Season
    year: int
    details: Dict = field(default_factory=dict)
    results: Dict = field(default_factory=dict)
    completed: bool = False

class EventType(Enum):
    """Types of game events."""
    AGING = auto()
    WARPING = auto()
    SEASONAL_ACTIVITY = auto()
    VIS_COLLECTION = auto()
    VIS_USE = auto()
    VIS_TRANSFER = auto()
    RESEARCH = auto()
    SPELL_CREATION = auto()
    ITEM_CREATION = auto()
    LABORATORY_WORK = auto()
    SEASON_CHANGE = auto()
    CHARACTER_DEATH = auto()
    TWILIGHT = auto()
    SPELLCASTING = auto()
    COMBAT = auto()
    CERTAMEN = auto()
    WOUND = auto()
    FATIGUE = auto()
    EXPERIENCE_GAIN = auto()
