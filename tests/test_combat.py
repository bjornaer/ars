import pytest

from ars.combat import CombatManager, Weapon, WeaponType
from ars.dice import DiceResult


@pytest.fixture
def longsword():
    return Weapon(
        name="Longsword",
        weapon_type=WeaponType.SINGLE,
        init_modifier=0,
        attack_modifier=2,
        defense_modifier=1,
        damage_modifier=5,
    )


def test_combat_initiative(longsword):
    result = CombatManager.calculate_initiative(quickness=2, weapon=longsword)
    assert isinstance(result, DiceResult)
    assert result.total >= 2  # Quickness + roll
    assert len(result.rolls) == 1  # Simple roll should have one die


def test_attack_roll(longsword):
    result = CombatManager.attack_roll(weapon_skill=3, weapon=longsword, stress=False)
    assert isinstance(result, DiceResult)
    assert result.total >= 5  # Skill + weapon modifier + roll
    assert len(result.rolls) == 1  # Simple roll should have one die


def test_damage_calculation(longsword):
    attack_result = DiceResult(total=15, rolls=[5], multiplier=1)
    defense_result = DiceResult(total=10, rolls=[5], multiplier=1)

    damage = CombatManager.calculate_damage(
        strength=2, weapon=longsword, attack_result=attack_result, defense_result=defense_result, soak=3
    )

    assert damage >= 0
