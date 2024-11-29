import pytest
from ars.core.dice import DiceRoller, DieType, DiceResult


def test_simple_die():
    """Test simple die roll."""
    result = DiceRoller.simple_die()
    assert isinstance(result, DiceResult)
    assert 0 <= result.value <= 9
    assert not result.is_botch
    assert result.multiplier == 1
    assert len(result.raw_rolls) == 1


def test_stress_die(monkeypatch):
    """Test stress die mechanics."""
    # Test normal roll
    monkeypatch.setattr('random.randint', lambda x, y: 5)
    result = DiceRoller.stress_die()
    assert result.value == 5
    assert result.multiplier == 1
    assert not result.is_botch
    
    # Test botch (roll of 1 then 0)
    rolls = iter([1, 0])
    monkeypatch.setattr('random.randint', lambda x, y: next(rolls))
    result = DiceRoller.stress_die()
    assert result.is_botch
    assert result.botch_dice == 1
    assert result.total == 0
    
    # Test explosion (roll of 0 then 5)
    rolls = iter([0, 5])
    monkeypatch.setattr('random.randint', lambda x, y: next(rolls))
    result = DiceRoller.stress_die()
    assert result.value == 5
    assert result.multiplier == 2
    assert result.total == 10
    
    # Test double explosion (0, 0, 5)
    rolls = iter([0, 0, 5])
    monkeypatch.setattr('random.randint', lambda x, y: next(rolls))
    result = DiceRoller.stress_die()
    assert result.value == 5
    assert result.multiplier == 4
    assert result.total == 20


def test_botch_check(monkeypatch):
    """Test botch check mechanics."""
    # No botch
    rolls = iter([1, 2, 3])
    with monkeypatch.context() as m:
        m.setattr('random.randint', lambda x, y: next(rolls))
        is_botch, zeros = DiceRoller.botch_check(3)
        assert not is_botch
        assert zeros == 0
    
    # Single botch
    rolls = iter([0, 2, 3])
    with monkeypatch.context() as m:
        m.setattr('random.randint', lambda x, y: next(rolls))
        is_botch, zeros = DiceRoller.botch_check(3)
        assert is_botch
        assert zeros == 1
    
    # Multiple zeros
    rolls = iter([0, 0, 0])
    with monkeypatch.context() as m:
        m.setattr('random.randint', lambda x, y: next(rolls))
        is_botch, zeros = DiceRoller.botch_check(3)
        assert is_botch
        assert zeros == 3


def test_ability_check(monkeypatch):
    """Test ability check mechanics."""
    # Simple check
    with monkeypatch.context() as m:
        m.setattr('random.randint', lambda x, y: 5)
        result = DiceRoller.ability_check(ability_score=3, stress=False)
        assert result.total == 8  # 5 + 3
    
    # Stress check with explosion
    with monkeypatch.context() as m:
        rolls = iter([0, 5])
        m.setattr('random.randint', lambda x, y: next(rolls))
        result = DiceRoller.ability_check(ability_score=3, stress=True)
        # For explosion: base value is 5, multiplier is 2, plus ability score 3
        assert result.value == 13  # (5 * 2) + 3
        assert result.multiplier == 2  # Multiplier is applied during roll
        assert result.total == 13


def test_spell_check(monkeypatch):
    """Test spell casting check mechanics."""
    # Successful cast
    with monkeypatch.context() as m:
        m.setattr('random.randint', lambda x, y: 5)
        result = DiceRoller.spell_check(
            casting_total=15,
            aura_modifier=3,
            fatigue_level=1
        )
        assert result.total == 22  # 5 + 15 + 3 - 1
    
    # Failed cast (botch)
    with monkeypatch.context() as m:
        rolls = iter([1, 0, 0])  # Roll 1, then botch check rolls 0
        m.setattr('random.randint', lambda x, y: next(rolls))
        result = DiceRoller.spell_check(casting_total=15)
        assert result.is_botch
        assert result.total == 0
    