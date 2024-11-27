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
