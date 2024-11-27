import random
from dataclasses import dataclass
from enum import Enum, auto


class StressResult(Enum):
    """Possible results of a stress die roll."""

    NORMAL = auto()
    BOTCH = auto()
    REROLL = auto()


@dataclass
class DiceResult:
    """Result of a dice roll."""

    total: int
    rolls: list[int]
    botch: bool = False
    multiplier: int = 1

    @property
    def is_botch(self) -> bool:
        return self.botch

    def __str__(self) -> str:
        if self.botch:
            return f"Botch! (rolls: {self.rolls})"
        return f"Total: {self.total} (rolls: {self.rolls}, x{self.multiplier})"


class DiceRoller:
    """Handles dice rolling mechanics."""

    @staticmethod
    def simple_die() -> DiceResult:
        """Roll a simple die (0-9)."""
        roll = random.randint(0, 9)
        return DiceResult(total=roll, rolls=[roll])

    @staticmethod
    def stress_die() -> DiceResult:
        """Roll a stress die (0-9, with botch and reroll possibilities)."""
        rolls = []
        multiplier = 1
        initial_roll = random.randint(0, 9)
        rolls.append(initial_roll)

        if initial_roll == 0:
            rolls.extend([random.randint(0, 9) for _ in range(2)])
            if all(r == 0 for r in rolls):
                return DiceResult(total=0, rolls=rolls, botch=True)
            return DiceResult(total=0, rolls=rolls)

        elif initial_roll == 1:
            while initial_roll == 1:
                multiplier *= 2
                initial_roll = random.randint(0, 9)
                rolls.append(initial_roll)

        return DiceResult(total=initial_roll * multiplier, rolls=rolls, multiplier=multiplier)

    @staticmethod
    def botch_dice(number: int) -> tuple[bool, list[int]]:
        """Roll botch dice.

        Args:
            number: Number of botch dice to roll.

        Returns:
            Tuple of (botched: bool, rolls: list[int])
        """
        rolls = [random.randint(0, 9) for _ in range(number)]
        botched = rolls.count(0) > 0
        return botched, rolls


class ArtRoller:
    """Handles Art-specific rolls."""

    @staticmethod
    def cast_spell(technique: int, form: int, aura: int = 0, stress: bool = True, modifiers: int = 0) -> DiceResult:
        """Roll for spell casting.

        Args:
            technique: Technique score
            form: Form score
            aura: Magical aura modifier
            stress: Whether to use stress die
            modifiers: Additional modifiers

        Returns:
            DiceResult with casting total
        """
        base = technique + form + aura + modifiers
        if stress:
            roll = DiceRoller.stress_die()
        else:
            simple_roll = DiceRoller.simple_die()
            roll = DiceResult(total=simple_roll, rolls=[simple_roll])

        roll.total += base
        return roll


class CombatRoller:
    """Handles combat-related rolls."""

    @staticmethod
    def attack_roll(weapon_skill: int, modifiers: int = 0, stress: bool = False) -> DiceResult:
        """Roll for attack.

        Args:
            weapon_skill: Weapon ability score
            modifiers: Situational modifiers
            stress: Whether to use stress die

        Returns:
            DiceResult with attack total
        """
        base = weapon_skill + modifiers
        if stress:
            roll = DiceRoller.stress_die()
        else:
            simple_roll = DiceRoller.simple_die()
            roll = DiceResult(total=simple_roll, rolls=[simple_roll])

        roll.total += base
        return roll
