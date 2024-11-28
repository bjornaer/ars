from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional

from ars.character import Character
from ars.dice import DiceResult, DiceRoller
from ars.events import EventRecorder, EventType
from ars.core.types import Season


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


class WoundSeverity(Enum):
    LIGHT = "Light"  # -1 to all rolls
    MEDIUM = "Medium"  # -3 to all rolls
    HEAVY = "Heavy"  # -5 to all rolls, movement reduced
    INCAPACITATING = "Incapacitating"  # Cannot act
    FATAL = "Fatal"  # Character dies


@dataclass
class Wound:
    severity: WoundSeverity
    location: str
    penalty: int
    recovery_time: int  # in seasons
    description: str


@dataclass
class CombatResult:
    hit: bool
    damage: int
    wound: Optional[Wound] = None
    fatigue_cost: int = 0
    initiative_used: int = 0
    botch: bool = False
    details: str = ""


class CombatManager(EventRecorder):
    """Manages combat mechanics and wound tracking."""

    def __init__(self, event_manager=None):
        super().__init__(event_manager)
        self.initiative_order: List["Character"] = []
        self.round_number: int = 0

    def resolve_attack(
        self,
        attacker: "Character",
        defender: "Character",
        weapon: str,
        modifiers: Dict[str, int] = None,
        year: Optional[int] = None,
        season: Optional[Season] = None,
    ) -> CombatResult:
        """Resolve a combat attack."""
        modifiers = modifiers or {}

        # Calculate attack total
        attack_roll = DiceRoller.stress_die()
        attack_total = (
            attack_roll.total
            + attacker.get_weapon_skill(weapon)
            + sum(modifiers.values())
            - attacker.get_wound_penalties()
        )

        # Calculate defense
        defense_total = defender.get_defense_total() - defender.get_wound_penalties() - defender.get_fatigue_penalty()

        # Determine hit and damage
        hit = attack_total > defense_total
        damage = 0
        wound = None

        if hit:
            damage = self._calculate_damage(attacker, weapon, attack_total - defense_total)
            wound = self._apply_damage(defender, damage, weapon)

            # Record combat event
            if self.event_manager:
                self.record_event(
                    type=EventType.COMBAT,
                    description=f"Combat hit: {attacker.name} -> {defender.name}",
                    details={
                        "attacker": attacker.name,
                        "defender": defender.name,
                        "weapon": weapon,
                        "damage": damage,
                        "wound": wound.severity.value if wound else None,
                    },
                    year=year,
                    season=season,
                )

        return CombatResult(
            hit=hit,
            damage=damage,
            wound=wound,
            fatigue_cost=1,  # Base fatigue cost for attack
            initiative_used=5,  # Standard initiative cost
            botch=attack_roll.botch,
            details=f"Attack roll: {attack_roll.rolls}",
        )

    def _calculate_damage(self, attacker: "Character", weapon: str, margin: int) -> int:
        """Calculate damage from a successful hit."""
        weapon_damage = attacker.get_weapon_damage(weapon)
        strength_bonus = max(0, attacker.characteristics.get("Strength", 0))
        return weapon_damage + strength_bonus + (margin // 3)

    def _apply_damage(self, defender: "Character", damage: int, weapon: str) -> Optional[Wound]:
        """Apply damage and determine wound severity."""
        # Apply soak
        soak = defender.get_soak_value()
        final_damage = max(0, damage - soak)

        if final_damage == 0:
            return None

        # Determine wound severity
        severity = WoundSeverity.LIGHT
        if final_damage >= 15:
            severity = WoundSeverity.FATAL
        elif final_damage >= 12:
            severity = WoundSeverity.INCAPACITATING
        elif final_damage >= 9:
            severity = WoundSeverity.HEAVY
        elif final_damage >= 6:
            severity = WoundSeverity.MEDIUM

        wound = Wound(
            severity=severity,
            location=self._determine_hit_location(),
            penalty=self._get_wound_penalty(severity),
            recovery_time=self._get_recovery_time(severity),
            description=f"{severity.value} wound from {weapon}",
        )

        defender.add_wound(wound)
        return wound

    def _determine_hit_location(self) -> str:
        """Randomly determine hit location."""
        locations = {1: "Head", 2: "Torso", 3: "Torso", 4: "Right Arm", 5: "Left Arm", 6: "Right Leg", 7: "Left Leg"}
        roll = DiceRoller.simple_die(sides=7) + 1
        return locations[roll]

    @staticmethod
    def _get_wound_penalty(severity: WoundSeverity) -> int:
        """Get penalty for wound severity."""
        penalties = {
            WoundSeverity.LIGHT: -1,
            WoundSeverity.MEDIUM: -3,
            WoundSeverity.HEAVY: -5,
            WoundSeverity.INCAPACITATING: -10,
            WoundSeverity.FATAL: -15,
        }
        return penalties[severity]

    @staticmethod
    def _get_recovery_time(severity: WoundSeverity) -> int:
        """Get recovery time in seasons."""
        recovery_times = {
            WoundSeverity.LIGHT: 1,
            WoundSeverity.MEDIUM: 2,
            WoundSeverity.HEAVY: 4,
            WoundSeverity.INCAPACITATING: 8,
            WoundSeverity.FATAL: 0,  # Fatal wounds don't recover
        }
        return recovery_times[severity]


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
