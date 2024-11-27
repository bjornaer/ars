from dataclasses import dataclass
from enum import Enum, auto

from .dice import DiceResult, DiceRoller


class WeaponType(Enum):
    """Types of weapons in Ars Magica."""

    SINGLE = auto()
    GREAT = auto()
    MISSILE = auto()


@dataclass
class Weapon:
    """Represents a weapon."""

    name: str
    weapon_type: WeaponType
    init_modifier: int
    attack_modifier: int
    defense_modifier: int
    damage_modifier: int
    range: str | None = None
    strength_requirement: int = 0


class CombatRoller:
    """Handles combat-specific dice rolls."""

    @staticmethod
    def simple_roll() -> DiceResult:
        """Perform a simple combat roll."""
        return DiceRoller.simple_die()

    @staticmethod
    def stress_roll() -> DiceResult:
        """Perform a stress combat roll."""
        return DiceRoller.stress_die()


class CombatManager:
    """Handles combat mechanics."""

    @staticmethod
    def calculate_initiative(quickness: int, weapon: Weapon, modifiers: int = 0) -> DiceResult:
        """Calculate initiative for a round."""
        base_total = quickness + weapon.init_modifier + modifiers
        roll = CombatRoller.simple_roll()
        return DiceResult(total=roll.total + base_total, rolls=roll.rolls, multiplier=roll.multiplier)

    @staticmethod
    def attack_roll(weapon_skill: int, weapon: Weapon, modifiers: int = 0, stress: bool = False) -> DiceResult:
        """Perform an attack roll."""
        base_total = weapon_skill + weapon.attack_modifier + modifiers
        roll = CombatRoller.stress_roll() if stress else CombatRoller.simple_roll()
        return DiceResult(total=roll.total + base_total, rolls=roll.rolls, multiplier=roll.multiplier, botch=roll.botch)

    @staticmethod
    def defense_roll(defense_skill: int, weapon: Weapon, modifiers: int = 0, stress: bool = False) -> DiceResult:
        """Perform a defense roll."""
        base_total = defense_skill + weapon.defense_modifier + modifiers
        roll = CombatRoller.stress_roll() if stress else CombatRoller.simple_roll()
        return DiceResult(total=roll.total + base_total, rolls=roll.rolls, multiplier=roll.multiplier, botch=roll.botch)

    @staticmethod
    def calculate_damage(
        strength: int, weapon: Weapon, attack_result: DiceResult, defense_result: DiceResult, soak: int
    ) -> int:
        """Calculate damage from an attack."""
        if attack_result.total <= defense_result.total:
            return 0

        damage = strength + weapon.damage_modifier + (attack_result.total - defense_result.total) // 5

        return max(0, damage - soak)


class CombatRound:
    """Manages a round of combat."""

    def __init__(self):
        self.participants: list[tuple[str, CombatStats]] = []
        self.current_turn: int = 0

    def add_participant(self, name: str, stats: "CombatStats") -> None:
        """Add a participant to the combat round."""
        self.participants.append((name, stats))
        self.participants.sort(key=lambda x: x[1].initiative_total, reverse=True)

    def next_turn(self) -> tuple[str, "CombatStats"] | None:
        """Get the next participant in initiative order."""
        if not self.participants or self.current_turn >= len(self.participants):
            return None

        participant = self.participants[self.current_turn]
        self.current_turn += 1
        return participant


@dataclass
class CombatStats:
    """Character's combat statistics."""

    initiative_total: int
    attack_total: int
    defense_total: int
    damage_total: int
    soak_total: int
