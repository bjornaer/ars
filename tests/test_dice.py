from unittest.mock import patch

from ars.dice import DiceResult, DiceRoller, DieType


def test_simple_die():
    """Test simple die roll."""
    with patch("random.randint", return_value=5):
        result = DiceRoller.simple_die()
        assert result.value == 5
        assert result.multiplier == 1
        assert not result.is_botch
        assert result.raw_rolls == [5]


def test_stress_die_normal():
    """Test normal stress die roll."""
    with patch("random.randint", return_value=5):
        result = DiceRoller.stress_die()
        assert result.value == 5
        assert result.multiplier == 1
        assert not result.is_botch
        assert result.raw_rolls == [5]


def test_stress_die_explosion():
    """Test stress die explosion (0 followed by normal roll)."""
    with patch("random.randint", side_effect=[0, 5]):
        result = DiceRoller.stress_die()
        assert result.value == 5
        assert result.multiplier == 2
        assert not result.is_botch
        assert result.raw_rolls == [0, 5]


def test_stress_die_multiple_explosions():
    """Test multiple stress die explosions."""
    with patch("random.randint", side_effect=[0, 0, 5]):
        result = DiceRoller.stress_die()
        assert result.value == 5
        assert result.multiplier == 4  # Two explosions: 2 * 2
        assert not result.is_botch
        assert result.raw_rolls == [0, 0, 5]


def test_stress_die_botch():
    """Test stress die botch (1 followed by 0)."""
    with patch("random.randint", side_effect=[1, 0]):
        result = DiceRoller.stress_die()
        assert result.value == 0
        assert result.is_botch
        assert result.botch_dice == 1
        assert result.raw_rolls == [1, 0]


def test_roll_multiple_simple():
    """Test rolling multiple simple dice."""
    with patch("random.randint", side_effect=[3, 5, 7]):
        results = DiceRoller.roll_multiple(num_dice=3, die_type=DieType.SIMPLE)
        assert len(results) == 3
        assert [r.value for r in results] == [3, 5, 7]
        assert all(not r.is_botch for r in results)
        assert all(r.multiplier == 1 for r in results)


def test_roll_multiple_stress():
    """Test rolling multiple stress dice."""
    with patch("random.randint", side_effect=[0, 5, 1, 0, 7]):
        results = DiceRoller.roll_multiple(num_dice=3, die_type=DieType.STRESS)
        assert len(results) == 3

        # First die: explosion
        assert results[0].value == 5
        assert results[0].multiplier == 2
        assert results[0].raw_rolls == [0, 5]

        # Second die: botch
        assert results[1].value == 0
        assert results[1].is_botch
        assert results[1].raw_rolls == [1, 0]

        # Third die: normal
        assert results[2].value == 7
        assert results[2].multiplier == 1
        assert results[2].raw_rolls == [7]


def test_ability_check():
    """Test ability check calculation."""
    with patch("random.randint", return_value=5):
        result = DiceRoller.ability_check(ability_score=3, stress=False, modifier=2)
        assert result.value == 10  # 5 + 3 + 2
        assert result.raw_rolls == [5]


def test_ability_check_stress():
    """Test ability check with stress die."""
    with patch("random.randint", side_effect=[0, 5]):
        result = DiceRoller.ability_check(ability_score=3, stress=True, modifier=2)
        assert result.value == 15  # (5 * 2) + 3 + 2
        assert result.raw_rolls == [0, 5]


def test_spell_check():
    """Test spell casting check."""
    with patch("random.randint", return_value=5):
        result = DiceRoller.spell_check(casting_total=15, aura_modifier=3, fatigue_level=1)
        assert result.value == 22  # 5 + 15 + (3 - 1)
        assert result.raw_rolls == [5]


def test_spell_check_botch():
    """Test spell casting check with botch."""
    with patch("random.randint", side_effect=[1, 0, 0]):
        result = DiceRoller.spell_check(casting_total=15, botch_dice=2)
        assert result.value == 0
        assert result.is_botch
        assert result.botch_dice == 1
        assert result.raw_rolls == [1, 0]


def test_certamen_check():
    """Test certamen check."""
    with patch("random.randint", return_value=5):
        result = DiceRoller.certamen_check(technique_score=5, form_score=4, aura_modifier=2)
        assert result.value == 16  # 5 + (5 + 4) + 2
        assert result.raw_rolls == [5]


def test_botch_check():
    """Test botch check mechanics."""
    with patch("random.randint", side_effect=[0, 1, 0]):
        is_botch, zeros = DiceRoller.botch_check(3)
        assert is_botch
        assert zeros == 2


def test_dice_result_total():
    """Test DiceResult total property calculation."""
    # Normal result
    result = DiceResult(value=5, multiplier=2, raw_rolls=[0, 5])
    assert result.total == 10

    # Botch result
    result = DiceResult(value=0, is_botch=True, raw_rolls=[1, 0])
    assert result.total == 0


def test_roll_multiple_empty():
    """Test rolling zero dice."""
    results = DiceRoller.roll_multiple(num_dice=0)
    assert len(results) == 0


def test_roll_multiple_negative():
    """Test rolling negative number of dice."""
    results = DiceRoller.roll_multiple(num_dice=-1)
    assert len(results) == 0


def test_raw_rolls_initialization():
    """Test that raw_rolls is properly initialized."""
    result = DiceResult(value=5)
    assert result.raw_rolls == []
