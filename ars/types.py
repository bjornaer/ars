from enum import Enum, auto


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
    """Magical Forms in Ars Magica."""

    ANIMAL = "Animal"
    AQUAM = "Aquam"
    AURAM = "Auram"
    CORPUS = "Corpus"
    HERBAM = "Herbam"
    IGNEM = "Ignem"
    IMAGINEM = "Imaginem"
    MENTEM = "Mentem"
    TERRAM = "Terram"
    VIM = "Vim"


class Technique(Enum):
    """Magical Techniques in Ars Magica."""

    CREO = "Creo"
    INTELLEGO = "Intellego"
    MUTO = "Muto"
    PERDO = "Perdo"
    REGO = "Rego"
