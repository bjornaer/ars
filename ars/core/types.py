from enum import Enum, auto
from typing import Dict, List, Optional
import yaml


class Technique(Enum):
    CREO = "Creo"
    INTELLEGO = "Intellego"
    MUTO = "Muto"
    PERDO = "Perdo"
    REGO = "Rego"

    @classmethod
    def get_description(cls, technique: "Technique") -> str:
        descriptions = {
            cls.CREO: "Create something from nothing",
            cls.INTELLEGO: "Gather information",
            cls.MUTO: "Transform something",
            cls.PERDO: "Destroy something",
            cls.REGO: "Control something"
        }
        return descriptions.get(technique, "No description available")


class Form(Enum):
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

    @classmethod
    def get_description(cls, form: "Form") -> str:
        descriptions = {
            cls.ANIMAL: "Animals and animal products",
            cls.AQUAM: "Water and liquids",
            cls.AURAM: "Air and weather",
            cls.CORPUS: "Human body",
            cls.HERBAM: "Plants and plant products",
            cls.IGNEM: "Fire and heat",
            cls.IMAGINEM: "Images and sensory effects",
            cls.MENTEM: "Mind and mental effects",
            cls.TERRAM: "Earth and minerals",
            cls.VIM: "Magical power itself"
        }
        return descriptions.get(form, "No description available")


class Range(Enum):
    PERSONAL = "Personal"
    TOUCH = "Touch"
    VOICE = "Voice"
    SIGHT = "Sight"
    ARCANE_CONNECTION = "Arcane Connection"

    @classmethod
    def get_modifier(cls, range_type: "Range") -> int:
        modifiers = {
            cls.PERSONAL: 0,
            cls.TOUCH: 0,
            cls.VOICE: 2,
            cls.SIGHT: 3,
            cls.ARCANE_CONNECTION: 4
        }
        return modifiers.get(range_type, 0)


class Duration(Enum):
    MOMENTARY = "Momentary"
    CONCENTRATION = "Concentration"
    DIAMETER = "Diameter"
    SUN = "Sun"
    MOON = "Moon"
    YEAR = "Year"

    @classmethod
    def get_modifier(cls, duration: "Duration") -> int:
        modifiers = {
            cls.MOMENTARY: 0,
            cls.CONCENTRATION: 1,
            cls.DIAMETER: 2,
            cls.SUN: 3,
            cls.MOON: 4,
            cls.YEAR: 5
        }
        return modifiers.get(duration, 0)


class Target(Enum):
    INDIVIDUAL = "Individual"
    GROUP = "Group"
    ROOM = "Room"
    STRUCTURE = "Structure"
    BOUNDARY = "Boundary"

    @classmethod
    def get_modifier(cls, target: "Target") -> int:
        modifiers = {
            cls.INDIVIDUAL: 0,
            cls.GROUP: 2,
            cls.ROOM: 2,
            cls.STRUCTURE: 3,
            cls.BOUNDARY: 4
        }
        return modifiers.get(target, 0)


class WeaponType(Enum):
    DAGGER = "Dagger"
    SWORD = "Sword"
    BOW = "Bow"
    SPEAR = "Spear"
    MACE = "Mace"
    BRAWLING = "Brawling"

    @classmethod
    def get_stats(cls, weapon: "WeaponType") -> Dict[str, int]:
        stats = {
            cls.DAGGER: {"init": 3, "attack": 3, "defense": 1, "damage": 3},
            cls.SWORD: {"init": 5, "attack": 6, "defense": 6, "damage": 7},
            cls.BOW: {"init": 0, "attack": 6, "defense": 0, "damage": 8},
            cls.SPEAR: {"init": 3, "attack": 6, "defense": 3, "damage": 6},
            cls.MACE: {"init": 3, "attack": 5, "defense": 4, "damage": 8},
            cls.BRAWLING: {"init": 0, "attack": 0, "defense": 0, "damage": 0}
        }
        return stats.get(weapon, {"init": 0, "attack": 0, "defense": 0, "damage": 0})


class ArmorType(Enum):
    NONE = "None"
    LEATHER = "Leather"
    CHAIN = "Chain"
    PLATE = "Plate"

    @classmethod
    def get_stats(cls, armor: "ArmorType") -> Dict[str, int]:
        stats = {
            cls.NONE: {"protection": 0, "load": 0},
            cls.LEATHER: {"protection": 2, "load": 1},
            cls.CHAIN: {"protection": 4, "load": 3},
            cls.PLATE: {"protection": 6, "load": 5}
        }
        return stats.get(armor, {"protection": 0, "load": 0})


class House(Enum):
    BONISAGUS = "Bonisagus"
    FLAMBEAU = "Flambeau"
    TREMERE = "Tremere"
    JERBITON = "Jerbiton"
    MERCERE = "Mercere"
    MERINITA = "Merinita"
    TYTALUS = "Tytalus"
    VERDITIUS = "Verditius"
    CRIAMON = "Criamon"
    BJORNAER = "Bjornaer"
    GUERNICUS = "Guernicus"
    EX_MISCELLANEA = "Ex Miscellanea"

    @classmethod
    def get_description(cls, house: "House") -> str:
        descriptions = {
            cls.BONISAGUS: "Founders and researchers of magic theory",
            cls.FLAMBEAU: "Combat specialists and wielders of destructive magic",
            cls.TREMERE: "Structured and hierarchical house of ambitious magi",
            cls.JERBITON: "Cultured magi who appreciate fine arts and mundane society",
            cls.MERCERE: "Messengers and facilitators of communication",
            cls.MERINITA: "Masters of faerie magic",
            cls.TYTALUS: "Challengers and conflict seekers",
            cls.VERDITIUS: "Crafters of magical items",
            cls.CRIAMON: "Enigmatic seekers of magical enlightenment",
            cls.BJORNAER: "Shapeshifters with strong connections to nature",
            cls.GUERNICUS: "Judges and keepers of the Order's laws",
            cls.EX_MISCELLANEA: "Diverse collection of magical traditions"
        }
        return descriptions.get(house, "No description available")


class Characteristic(Enum):
    INTELLIGENCE = "Intelligence"
    PERCEPTION = "Perception"
    STRENGTH = "Strength"
    STAMINA = "Stamina"
    PRESENCE = "Presence"
    COMMUNICATION = "Communication"
    DEXTERITY = "Dexterity"
    QUICKNESS = "Quickness"

    @classmethod
    def get_description(cls, characteristic: "Characteristic") -> str:
        descriptions = {
            cls.INTELLIGENCE: "Mental capability and learning",
            cls.PERCEPTION: "Awareness and attention to detail",
            cls.STRENGTH: "Physical power and lifting capacity",
            cls.STAMINA: "Endurance and resistance",
            cls.PRESENCE: "Force of personality and leadership",
            cls.COMMUNICATION: "Social interaction and expression",
            cls.DEXTERITY: "Manual coordination and agility",
            cls.QUICKNESS: "Speed and reflexes"
        }
        return descriptions.get(characteristic, "No description available")


class FatigueLevel(Enum):
    FRESH = 0
    WINDED = 1
    WEARY = 2
    TIRED = 3
    DAZED = 4
    UNCONSCIOUS = 5

    @classmethod
    def get_penalty(cls, level: "FatigueLevel") -> int:
        penalties = {
            cls.FRESH: 0,
            cls.WINDED: 0,
            cls.WEARY: -1,
            cls.TIRED: -3,
            cls.DAZED: -5,
            cls.UNCONSCIOUS: -1000  # Effectively prevents any action
        }
        return penalties.get(level, 0)


class AbilityType(Enum):
    ACADEMIC = "Academic"
    ARCANE = "Arcane"
    MARTIAL = "Martial"
    SOCIAL = "Social"
    SUPERNATURAL = "Supernatural"

    @classmethod
    def get_abilities(cls, type: "AbilityType") -> List[str]:
        abilities = {
            cls.ACADEMIC: ["Artes Liberales", "Civil and Canon Law", "Medicine", "Philosophy", "Theology"],
            cls.ARCANE: ["Magic Theory", "Parma Magica", "Penetration", "Finesse"],
            cls.MARTIAL: ["Athletics", "Brawl", "Ride", "Swim", "Hunt"],
            cls.SOCIAL: ["Charm", "Etiquette", "Folk Ken", "Guile", "Leadership"],
            cls.SUPERNATURAL: ["Second Sight", "Sense Holiness", "Dowsing", "Premonitions"]
        }
        return abilities.get(type, [])


def register_yaml_constructors():
    """Register YAML constructors for custom types."""
    def enum_constructor(loader, node):
        value = loader.construct_scalar(node)
        return WeaponType(value)
    
    yaml.add_constructor('tag:yaml.org,2002:python/object/apply:ars.core.types.WeaponType', 
                        enum_constructor)
    # Add other enum constructors as needed
    for enum_class in [ArmorType, AbilityType, Characteristic, Form, Technique]:
        yaml.add_constructor(f'tag:yaml.org,2002:python/object/apply:ars.core.types.{enum_class.__name__}',
                           lambda loader, node, cls=enum_class: cls(loader.construct_scalar(node)))

# Call this at module import
register_yaml_constructors()