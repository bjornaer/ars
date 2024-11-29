import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple


class DieType(Enum):
    """Types of dice rolls in Ars Magica."""

    SIMPLE = auto()
    STRESS = auto()
    BOTCH = auto()


@dataclass
class DiceResult:
    """Represents the result of a dice roll."""

    value: int
    is_botch: bool = False
    multiplier: int = 1
    botch_dice: int = 0
    raw_rolls: List[int] = None  # Store all raw rolls

    def __post_init__(self):
        if self.raw_rolls is None:
            self.raw_rolls = []

    @property
    def total(self) -> int:
        """Calculate total value including multiplier."""
        return self.value * self.multiplier if not self.is_botch else 0

    @property
    def roll(self) -> int:
        """Get the first (main) roll value."""
        return self.raw_rolls[0] if self.raw_rolls else self.value


class DiceRoller:
    """Handles all dice rolling mechanics for the game."""

    @staticmethod
    def roll_multiple(num_dice: int = 1, die_type: DieType = DieType.SIMPLE) -> List[DiceResult]:
        """
        Roll multiple dice of the specified type.

        Args:
            num_dice: Number of dice to roll
            die_type: Type of die to roll (simple, stress, or botch)
        """
        results = []
        for _ in range(num_dice):
            if die_type == DieType.STRESS:
                results.append(DiceRoller.stress_die())
            elif die_type == DieType.BOTCH:
                is_botch, zeros = DiceRoller.botch_check(1)
                results.append(DiceResult(value=0, is_botch=is_botch, botch_dice=zeros))
            else:
                results.append(DiceRoller.simple_die())
        return results

    @staticmethod
    def simple_die() -> DiceResult:
        """Roll a simple die (0-9)."""
        roll = random.randint(0, 9)
        return DiceResult(value=roll, raw_rolls=[roll])

    @staticmethod
    def stress_die() -> DiceResult:
        """
        Roll a stress die (0-9 with possible multiplier).
        1 triggers a botch check, 0 means multiply by 2 and roll again.
        """
        rolls = []
        multiplier = 1
        value = 0
        is_botch = False
        botch_dice = 0

        # First roll
        roll = random.randint(0, 9)
        rolls.append(roll)

        if roll == 1:
            # Botch check
            botch_roll = random.randint(0, 9)
            rolls.append(botch_roll)
            is_botch = botch_roll == 0
            botch_dice = 1
            value = 0
        else:
            # Handle explosions with a loop
            current_roll = roll
            while current_roll == 0:
                multiplier *= 2
                current_roll = random.randint(0, 9)
                rolls.append(current_roll)

            # If the last roll wasn't 0, it's our value
            value = current_roll if roll == 0 else roll

        return DiceResult(value=value, is_botch=is_botch, multiplier=multiplier, botch_dice=botch_dice, raw_rolls=rolls)

    @staticmethod
    def botch_check(botch_dice: int) -> Tuple[bool, int]:
        """
        Perform a botch check with specified number of botch dice.
        Returns (is_botch, zeros_rolled).
        """
        rolls = [random.randint(0, 9) for _ in range(botch_dice)]
        zeros = sum(1 for roll in rolls if roll == 0)
        return zeros > 0, zeros

    @classmethod
    def ability_check(
        cls, ability_score: int, stress: bool = False, modifier: int = 0, botch_dice: int = 0
    ) -> DiceResult:
        """
        Perform an ability check.

        Args:
            ability_score: Base ability score
            stress: Whether to use a stress die
            modifier: Additional modifier to the roll
            botch_dice: Number of additional botch dice
        """
        if stress:
            roll = cls.stress_die()
            if roll.is_botch:
                is_botch, zeros = cls.botch_check(botch_dice + 1)
                roll.is_botch = is_botch
                roll.botch_dice = zeros
            else:
                roll.value = roll.total + ability_score + modifier
        else:
            roll = cls.simple_die()
            roll.value = roll.value + ability_score + modifier

        return roll

    @classmethod
    def spell_check(
        cls,
        casting_total: int,
        stress: bool = True,
        aura_modifier: int = 0,
        fatigue_level: int = 0,
        botch_dice: int = 0,
    ) -> DiceResult:
        """
        Perform a spell casting check.

        Args:
            casting_total: Base casting score
            stress: Whether to use stress die
            aura_modifier: Magical aura modifier
            fatigue_level: Current fatigue level (negative modifier)
            botch_dice: Additional botch dice
        """
        modifier = aura_modifier - fatigue_level
        result = cls.ability_check(ability_score=casting_total, stress=stress, modifier=modifier, botch_dice=botch_dice)

        return result

    @classmethod
    def certamen_check(
        cls, technique_score: int, form_score: int, stress: bool = True, aura_modifier: int = 0, fatigue_level: int = 0
    ) -> DiceResult:
        """
        Perform a Certamen check.

        Args:
            technique_score: Technique score
            form_score: Form score
            stress: Whether to use stress die
            aura_modifier: Magical aura modifier
            fatigue_level: Current fatigue level
        """
        casting_total = technique_score + form_score
        return cls.spell_check(
            casting_total=casting_total, stress=stress, aura_modifier=aura_modifier, fatigue_level=fatigue_level
        )
