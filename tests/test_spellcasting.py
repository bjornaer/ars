import pytest

from ars.character import Character
from ars.spells import Spell, SpellParameters, SpellCastingResult
from ars.events import EventType
from ars.core.types import (
    AbilityType, Form, House, Technique,
    Range, Duration, Target,
    Season
)


@pytest.fixture
def base_spell():
    """Provides a basic test spell."""
    return Spell(
        name="Ball of Abysmal Flame",
        technique=Technique.CREO,
        form=Form.IGNEM,
        level=15,
        parameters=SpellParameters(
            range=Range.VOICE,
            duration=Duration.DIAMETER,
            target=Target.INDIVIDUAL
        )
    )


class TestSpellcasting:
    def test_basic_spellcasting(self, base_character, base_spell, event_manager):
        """Test basic spell casting mechanics."""
        # Cast the spell
        result = base_character.cast_spell(base_spell)
        
        # Verify casting result
        assert isinstance(result, SpellCastingResult)
        assert result.success
        assert result.casting_total > 0
        
        # Verify event recording with context
        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.SPELLCASTING
        assert event.details["spell_name"] == base_spell.name
        assert event.year == event_manager.context.year  # Should be 1220
        assert event.season == event_manager.context.season  # Should be SPRING

    def test_spell_casting_failure(self, base_character, base_spell):
        """Test spell casting failure conditions."""
        # Create a high-level spell that should be difficult to cast
        difficult_spell = Spell(
            name="Mighty Conflagration",
            technique=Technique.CREO,
            form=Form.IGNEM,
            level=40,  # Very high level
            parameters=SpellParameters(
                range=Range.VOICE,
                duration=Duration.DIAMETER,
                target=Target.INDIVIDUAL
            )
        )
        
        result = base_character.cast_spell(difficult_spell)
        
        assert not result.success
        assert result.casting_total < difficult_spell.level

    def test_spell_botch(self, base_character, base_spell, monkeypatch):
        """Test spell botching mechanics."""
        # Mock the dice roll to force a botch
        def mock_roll_stress_die():
            return 0  # Botch result
        
        monkeypatch.setattr(base_character, "roll_stress_die", mock_roll_stress_die)
        
        result = base_character.cast_spell(base_spell)
        
        assert not result.success
        assert result.botch
        assert result.casting_total == 0

    def test_fatigue_levels(self, base_character, base_spell):
        """Test fatigue accumulation from spellcasting."""
        initial_fatigue = base_character.fatigue_level
        
        # Cast multiple spells
        for _ in range(3):
            base_character.cast_spell(base_spell)
        
        assert base_character.fatigue_level > initial_fatigue
        
        # Test casting while fatigued
        result = base_character.cast_spell(base_spell)
        
        assert result.casting_total < (result.casting_roll + result.stress_die)  # Penalty applied

    def test_casting_modifiers(self, base_character, base_spell):
        """Test various casting modifiers."""
        # Test casting with aura bonus
        result_with_aura = base_character.cast_spell(
            spell=base_spell,
            aura_bonus=5
        )
        
        # Test casting without aura bonus
        result_without_aura = base_character.cast_spell(
            spell=base_spell,
            aura_bonus=0
        )
        
        assert result_with_aura.casting_total > result_without_aura.casting_total

    def test_spontaneous_casting(self, base_character):
        """Test spontaneous spell casting."""
        result = base_character.cast_spontaneous_spell(
            technique=Technique.CREO,
            form=Form.IGNEM,
            level=10,
            parameters=SpellParameters(
                range=Range.VOICE,
                duration=Duration.DIAMETER,
                target=Target.INDIVIDUAL
            )
        )
        
        assert isinstance(result, SpellCastingResult)
        # Spontaneous casting should have lower totals than formulaic
        assert result.casting_total < (base_character.techniques[Technique.CREO] + 
                                     base_character.forms[Form.IGNEM]) 


class TestSpellMastery:
    def test_spell_mastery_basics(self, base_character, base_spell):
        """Test basic spell mastery mechanics."""
        # Add mastery points to the spell
        base_character.add_spell_mastery(
            spell_name=base_spell.name,
            points=5
        )
        
        assert base_spell.name in base_character.mastered_spells
        assert base_character.mastered_spells[base_spell.name] == 5
        
        # Cast mastered spell
        result = base_character.cast_spell(base_spell)
        
        # Mastery should improve casting total
        assert result.mastery_bonus > 0
        assert result.casting_total > (result.casting_roll + result.stress_die)

    def test_mastery_special_abilities(self, base_character, base_spell):
        """Test spell mastery special abilities."""
        # Add mastery with special abilities
        base_character.add_spell_mastery(
            spell_name=base_spell.name,
            points=5,
            special_abilities=["Multiple Casting", "Fast Cast"]
        )
        
        # Test multiple casting
        results = base_character.cast_multiple(
            spell=base_spell,
            times=3
        )
        
        assert len(results) == 3
        for result in results:
            assert result.success
            
        # Test fast casting
        fast_cast_result = base_character.cast_spell(
            spell=base_spell,
            fast_cast=True
        )
        
        assert fast_cast_result.initiative_bonus > 0

    def test_mastery_fatigue_reduction(self, base_character, base_spell):
        """Test fatigue reduction with mastered spells."""
        # Add mastery with Quiet Casting
        base_character.add_spell_mastery(
            spell_name=base_spell.name,
            points=5,
            special_abilities=["Quiet Casting"]
        )
        
        initial_fatigue = base_character.fatigue_level
        
        # Cast mastered spell
        base_character.cast_spell(base_spell)
        
        # Should have reduced or no fatigue cost
        assert base_character.fatigue_level <= initial_fatigue


class TestMagicalDefenses:
    def test_parma_magica_basics(self, base_character):
        """Test basic Parma Magica mechanics."""
        # Activate Parma Magica
        base_character.activate_parma_magica()
        
        assert base_character.parma_active
        assert base_character.magic_resistance > 0
        
        # Calculate base resistance
        expected_resistance = (base_character.abilities[AbilityType.ARCANE]["Parma Magica"] * 5)
        assert base_character.magic_resistance == expected_resistance

    def test_parma_magica_against_spells(self, base_character, base_spell):
        """Test Parma Magica's effectiveness against spells."""
        # Setup another character as the attacker
        attacker = Character(
            name="Attackus of Flambeau",
            player="Test Player",
            saga="Test Saga",
            covenant="Test Covenant",
            house=House.FLAMBEAU
        )
        attacker.techniques[Technique.CREO] = 10
        attacker.forms[Form.IGNEM] = 10
        
        # Activate defender's Parma
        base_character.activate_parma_magica()
        initial_resistance = base_character.magic_resistance
        
        # Cast spell at defender
        result = attacker.cast_spell(
            spell=base_spell,
            target=base_character,
            penetration_bonus=5
        )
        
        # Spell penetration should be reduced by Parma
        assert result.penetration_total < result.casting_total
        assert result.penetration_total == (result.casting_total - initial_resistance)

    def test_parma_sharing(self, base_character):
        """Test sharing Parma Magica protection."""
        # Create another character to share Parma with
        protected_char = Character(
            name="Protectus",
            player="Test Player",
            saga="Test Saga",
            covenant="Test Covenant",
            house=House.BONISAGUS
        )
        
        # Activate and share Parma
        base_character.activate_parma_magica()
        base_character.share_parma_magica(protected_char)
        
        # Protected character should get partial resistance
        expected_shared_resistance = (base_character.abilities[AbilityType.ARCANE]["Parma Magica"] * 5) // 2
        assert protected_char.magic_resistance == expected_shared_resistance

    def test_penetration_calculation(self, base_character, base_spell):
        """Test spell penetration against magical resistance."""
        # Setup target with Parma
        target = Character(
            name="Targetius",
            player="Test Player",
            saga="Test Saga",
            covenant="Test Covenant",
            house=House.BONISAGUS
        )
        target.abilities[AbilityType.ARCANE]["Parma Magica"] = 2
        target.activate_parma_magica()
        
        # Cast spell at target
        result = base_character.cast_spell(
            spell=base_spell,
            target=target,
            penetration_bonus=5
        )
        
        # Verify penetration calculations
        assert result.penetration_total == (result.casting_total + 5 - target.magic_resistance)
        assert result.success == (result.penetration_total > 0)