from dataclasses import dataclass, field
from typing import Dict, Optional, List

from ars.core.character import Character
from ars.core.types import ArmorType, WeaponType, Duration, Form, Range, Target, Technique
from ars.core.spells import Spell, SpellEffect, SpellCaster, CastingResult


@dataclass
class Grog(Character):
    """Represents a non-magical character (Grog) in Ars Magica."""
    
    # Combat-specific attributes
    weapon_specialties: Dict[WeaponType, str] = field(default_factory=dict)
    armor_proficiency: Dict[ArmorType, int] = field(default_factory=dict)
    shield_bonus: int = 0
    
    def get_weapon_attack_bonus(self, weapon: WeaponType) -> int:
        """Calculate total attack bonus with a weapon."""
        base_bonus = super().get_combat_bonus(weapon)
        specialty_bonus = 1 if weapon in self.weapon_specialties else 0
        weapon_stats = WeaponType.get_stats(weapon)
        
        return base_bonus + specialty_bonus + weapon_stats["attack"]

    def get_weapon_defense_bonus(self, weapon: WeaponType) -> int:
        """Calculate total defense bonus with a weapon."""
        base_bonus = super().get_combat_bonus(weapon)
        weapon_stats = WeaponType.get_stats(weapon)
        shield = self.shield_bonus if weapon_stats["defense"] > 0 else 0
        
        return base_bonus + weapon_stats["defense"] + shield

    def get_armor_encumbrance(self) -> int:
        """Calculate total armor encumbrance."""
        if not self.armor:
            return 0
            
        armor_stats = ArmorType.get_stats(self.armor)
        proficiency = self.armor_proficiency.get(self.armor, 0)
        
        return max(0, armor_stats["load"] - proficiency)

    def get_initiative_bonus(self, weapon: WeaponType) -> int:
        """Calculate initiative bonus with a weapon."""
        quickness = self.characteristics.get('Quickness', 0)
        weapon_stats = WeaponType.get_stats(weapon)
        encumbrance = self.get_armor_encumbrance()
        
        return quickness + weapon_stats["init"] - encumbrance

    def to_dict(self) -> dict:
        """Convert grog to dictionary for saving."""
        base_dict = super().to_dict()
        combat_dict = {
            "weapon_specialties": {weapon.value: spec for weapon, spec in self.weapon_specialties.items()},
            "armor_proficiency": {armor.value: prof for armor, prof in self.armor_proficiency.items()},
            "shield_bonus": self.shield_bonus
        }
        return {**base_dict, **combat_dict}

    @classmethod
    def from_dict(cls, data: dict) -> "Grog":
        """Create grog from dictionary data."""
        # Convert string keys back to enums
        weapon_specialties = {
            WeaponType(key): value 
            for key, value in data.get("weapon_specialties", {}).items()
        }
        armor_proficiency = {
            ArmorType(key): value 
            for key, value in data.get("armor_proficiency", {}).items()
        }
        
        # Create base character first
        base_char = super().from_dict(data)
        
        return cls(
            **{k: v for k, v in base_char.__dict__.items()},
            weapon_specialties=weapon_specialties,
            armor_proficiency=armor_proficiency,
            shield_bonus=data.get("shield_bonus", 0)
        ) 
