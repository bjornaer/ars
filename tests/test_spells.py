import pytest
# from typing import Dict

from ars.core.types import (
    Duration, FatigueLevel, Form, Range, Target, Technique
)
from ars.core.spells import Spell, SpellEffect, SpellCaster, CastingResult
from ars.core.characters.magus import Magus
from ars.core.dice import DiceResult


@pytest.fixture
def basic_magus() -> Magus:
    """Create a basic magus for testing."""
    magus = Magus(
        name="Test Magus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house="Bonisagus",
        techniques={Technique.CREO: 5, Technique.PERDO: 3},
        forms={Form.IGNEM: 4, Form.AQUAM: 2}
    )
    magus.characteristics = {"Intelligence": 3, "Stamina": 2}
    return magus


@pytest.fixture
def basic_spell() -> Spell:
    """Create a basic spell for testing."""
    return Spell(
        name="Test Fire",
        technique=Technique.CREO,
        form=Form.IGNEM,
        level=10,
        range=Range.VOICE,
        duration=Duration.DIAMETER,
        target=Target.INDIVIDUAL,
        description="A test fire spell",
        effects=[SpellEffect("Create Fire", 3, {"size": 1})]
    )


class TestSpellCasting:
    """Test spell casting mechanics."""

    def test_basic_casting(self, basic_magus, basic_spell):
        """Test basic spell casting."""
        result = SpellCaster.cast_spell(basic_spell, basic_magus)
        assert isinstance(result, CastingResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'total')

    def test_fatigue_effects(self, basic_magus, basic_spell):
        """Test fatigue effects on casting."""
        initial_fatigue = basic_magus.fatigue_level
        SpellCaster.cast_spell(basic_spell, basic_magus)
        assert basic_magus.fatigue_level.value > initial_fatigue.value

    def test_aura_modifier(self, basic_magus, basic_spell, monkeypatch):
        """Test magical aura effects."""
        def fixed_roll():
            return DiceResult(value=5, raw_rolls=[5])
        
        monkeypatch.setattr('ars.core.dice.DiceRoller.stress_die', fixed_roll)
        
        result_with_aura = SpellCaster.cast_spell(basic_spell, basic_magus, aura=3)
        basic_magus.fatigue_level = FatigueLevel.FRESH
        result_no_aura = SpellCaster.cast_spell(basic_spell, basic_magus)
        
        assert result_with_aura.total == result_no_aura.total + 3

    def test_botch_mechanics(self, basic_magus, basic_spell, monkeypatch):
        """Test botch mechanics."""
        def mock_stress_die():
            return DiceResult(
                value=0,
                raw_rolls=[1],
                is_botch=True,
                botch_dice=2,
                multiplier=1
            )
        
        monkeypatch.setattr('ars.core.dice.DiceRoller.stress_die', mock_stress_die)
        
        result = SpellCaster.cast_spell(basic_spell, basic_magus, stress=True)
        assert result.botch
        assert result.botch_dice == 2

    def test_ritual_casting(self, basic_magus):
        """Test ritual spell casting."""
        ritual_spell = Spell(
            name="Test Ritual",
            technique=Technique.CREO,
            form=Form.IGNEM,
            level=20,
            range=Range.SIGHT,
            duration=Duration.MOON,
            target=Target.BOUNDARY,
            description="A test ritual",
            ritual=True
        )
        result = SpellCaster.cast_spell(ritual_spell, basic_magus)
        assert result.fatigue_cost == 0  # Rituals don't cause fatigue

    def test_penetration(self, basic_magus, basic_spell):
        """Test spell penetration calculation."""
        casting_total = basic_spell.calculate_casting_total(
            basic_magus.techniques[Technique.CREO],
            basic_magus.forms[Form.IGNEM]
        )
        penetration = SpellCaster.calculate_penetration(
            casting_total=casting_total,
            spell_level=basic_spell.level,
            penetration_bonus=3
        )
        assert penetration >= 0


class TestSpellEffects:
    """Test spell effects and magnitudes."""

    def test_effect_magnitude(self):
        """Test spell effect magnitude calculation."""
        effect = SpellEffect("Test Effect", 3, {"size": 2, "power": 1})
        assert effect.calculate_magnitude() == 6

    def test_spell_total_magnitude(self, basic_spell):
        """Test total spell magnitude calculation."""
        assert basic_spell.get_magnitude() == 4  # Base 3 + size 1

    def test_spell_serialization(self, basic_spell):
        """Test spell serialization."""
        spell_dict = basic_spell.to_dict()
        reconstructed = Spell.from_dict(spell_dict)
        assert reconstructed.name == basic_spell.name
        assert reconstructed.level == basic_spell.level