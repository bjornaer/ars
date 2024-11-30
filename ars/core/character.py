from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from ars.core.types import (
    AbilityType, ArmorType, Characteristic, FatigueLevel, WeaponStats,
    WeaponType
)


class CharacterError(Exception):
    """Base exception for character-related errors."""
    pass


class InvalidCharacterDataError(CharacterError):
    """Raised when character data is invalid."""
    pass


@dataclass
class Character:
    """Base character class for Ars Magica."""
    
    # Basic Information
    name: str
    player: str
    saga: str
    covenant: str
    age: int = 25
    size: int = 0
    confidence: int = 0
    
    # Core Stats
    characteristics: Dict[Characteristic, int] = field(default_factory=dict)
    fatigue_level: FatigueLevel = FatigueLevel.FRESH
    
    # Skills and Abilities
    abilities: Dict[AbilityType, Dict[str, int]] = field(
        default_factory=lambda: {ability_type: {} for ability_type in AbilityType}
    )
    
    # Equipment
    weapons: Dict[WeaponType, WeaponStats] = field(default_factory=dict)
    equipped_weapon: Optional[WeaponType] = None
    armor: Optional[ArmorType] = None
    
    # Personality
    personality_traits: Dict[str, int] = field(default_factory=dict)
    reputation: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default values for characteristics."""
        for char in Characteristic:
            if char not in self.characteristics:
                self.characteristics[char] = 0

    def add_ability(self, ability_type: AbilityType, ability_name: str, score: int) -> None:
        """Add or update an ability score."""
        if ability_name not in AbilityType.get_abilities(ability_type):
            raise InvalidCharacterDataError(f"Invalid ability '{ability_name}' for type {ability_type.value}")
        
        self.abilities[ability_type][ability_name] = score

    def get_ability_score(self, ability_type: AbilityType, ability_name: str) -> int:
        """Get the score for a specific ability."""
        return self.abilities[ability_type].get(ability_name, 0)

    def add_personality_trait(self, trait: str, value: int) -> None:
        """Add or update a personality trait."""
        if not -3 <= value <= 3:
            raise InvalidCharacterDataError("Personality trait values must be between -3 and 3")
        self.personality_traits[trait] = value

    def add_reputation(self, reputation: str, value: int) -> None:
        """Add or update a reputation."""
        if not 0 <= value <= 5:
            raise InvalidCharacterDataError("Reputation values must be between 0 and 5")
        self.reputation[reputation] = value

    def modify_fatigue(self, levels: int) -> None:
        """Modify character's fatigue level."""
        new_level = min(max(0, self.fatigue_level.value + levels), FatigueLevel.UNCONSCIOUS.value)
        self.fatigue_level = FatigueLevel(new_level)

    def get_characteristic_bonus(self, characteristic: Characteristic) -> int:
        """Get the bonus for a characteristic."""
        return self.characteristics.get(characteristic, 0)

    def equip_weapon(self, weapon: WeaponType, attack_mod: int = 0, damage_mod: int = 0, init_mod: int = 0, defense_mod: int = 0) -> None:
        """Equip a weapon with associated skill."""
        if not 0 <= attack_mod <= 5:
            raise InvalidCharacterDataError("Weapon skill must be between 0 and 5")
        
        self.weapons[weapon] = WeaponStats(
            attack=attack_mod,
            damage=damage_mod,
            init=init_mod,
            defense=defense_mod
        )
        self.equipped_weapon = weapon

    def equip_armor(self, armor: ArmorType) -> None:
        """Equip armor."""
        self.armor = armor

    def get_combat_bonus(self, weapon: WeaponType) -> int:
        """Calculate total combat bonus for a weapon."""
        # Dexterity + Combat Ability + Weapon Attack Modifier + Stress Dice
        weapon_stats = self.weapons.get(weapon)
        dex_bonus = self.characteristics.get(Characteristic.DEXTERITY, 0)
        str_bonus = self.characteristics.get(Characteristic.STRENGTH, 0)
        fatigue_penalty = FatigueLevel.get_penalty(self.fatigue_level)
        weapon_bonus = weapon_stats.attack
        
        return dex_bonus + str_bonus + fatigue_penalty + weapon_bonus

    def get_damage_bonus(self, weapon: WeaponType) -> int:
        """Calculate total damage bonus for a weapon."""
        weapon_stats = self.weapons.get(weapon)
        str_bonus = self.characteristics.get(Characteristic.STRENGTH, 0)
        return weapon_stats.damage + str_bonus

    def get_defense_bonus(self, weapon: WeaponType) -> int:
        """Calculate total defense bonus for armor and attributes."""
        # Speed + Combat Ability + Weapon Defense Modifier + Stress Dice
        weapon_stats = self.weapons.get(weapon)
        dex_bonus = self.characteristics.get(Characteristic.DEXTERITY, 0)
        str_bonus = self.characteristics.get(Characteristic.STRENGTH, 0)
        fatigue_penalty = FatigueLevel.get_penalty(self.fatigue_level)
        weapon_bonus = weapon_stats.defense

        return dex_bonus + str_bonus + fatigue_penalty + weapon_bonus

    def get_soak_bonus(self) -> int:
        """Calculate character's soak bonus."""
        stamina = self.characteristics.get(Characteristic.STAMINA, 0)
        armour_bonus = ArmorType.get_stats(self.armor).protection
        
        return stamina + armour_bonus
    
    def get_initiative_bonus(self, weapon: WeaponType) -> int:
        """Calculate character's initiative bonus."""
        quickness = self.characteristics.get(Characteristic.QUICKNESS, 0)
        weapon_bonus = self.weapons.get(weapon).init
        return quickness + weapon_bonus

    def to_dict(self) -> dict:
        """Convert character to dictionary for saving."""
        return {
            "name": self.name,
            "player": self.player,
            "saga": self.saga,
            "covenant": self.covenant,
            "age": self.age,
            "size": self.size,
            "confidence": self.confidence,
            "characteristics": {char.value: value for char, value in self.characteristics.items()},
            "fatigue_level": self.fatigue_level.value,
            "abilities": {
                ability_type.value: abilities 
                for ability_type, abilities in self.abilities.items()
            },
            "weapons": {weapon.value: skill for weapon, skill in self.weapons.items()},
            "equipped_weapon": self.equipped_weapon.value if self.equipped_weapon else None,
            "armor": self.armor.value if self.armor else None,
            "personality_traits": self.personality_traits,
            "reputation": self.reputation
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        """Create character from dictionary data."""
        # Convert string keys back to enums
        characteristics = {
            Characteristic(key): value 
            for key, value in data.get("characteristics", {}).items()
        }
        
        abilities = {
            AbilityType(key): value_dict 
            for key, value_dict in data.get("abilities", {}).items()
        }
        
        weapons = {
            WeaponType(key): value 
            for key, value in data.get("weapons", {}).items()
        }
        
        armor = ArmorType(data["armor"]) if data.get("armor") else None
        
        return cls(
            name=data["name"],
            player=data["player"],
            saga=data["saga"],
            covenant=data["covenant"],
            age=data.get("age", 25),
            size=data.get("size", 0),
            confidence=data.get("confidence", 0),
            characteristics=characteristics,
            fatigue_level=FatigueLevel(data.get("fatigue_level", 0)),
            abilities=abilities,
            weapons=weapons,
            equipped_weapon=WeaponType(data.get("equipped_weapon")) if data.get("equipped_weapon") else None,
            armor=armor,
            personality_traits=data.get("personality_traits", {}),
            reputation=data.get("reputation", {})
        )

    def save(self, directory: Path = Path("characters")) -> None:
        """Save character to YAML file."""
        directory.mkdir(exist_ok=True)
        filepath = directory / f"{self.name.lower().replace(' ', '_')}.yml"
        
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f)

    @classmethod
    def load(cls, name: str, directory: Path = Path("characters")) -> "Character":
        """Load character from YAML file."""
        filepath = directory / f"{name.lower().replace(' ', '_')}.yml"
        
        if not filepath.exists():
            raise CharacterError(f"No character file found for {name}")
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            
        return cls.from_dict(data) 