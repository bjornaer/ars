from unittest.mock import Mock

import pytest

from ars.character import Character
from ars.combat import CombatManager, WoundSeverity
from ars.events import EventType
from ars.core.types import Season
from ars.spells import Spell, SpellCaster, SpellParameters
from ars.core.types import Duration, Form, Range, Target, Technique


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def test_mage(event_manager):
    mage = Character(
        name="Marcus of Bonisagus", player="Test Player", saga="Test Saga", covenant="Test Covenant", house="Bonisagus"
    )
    mage.event_manager = event_manager
    mage.techniques = {"Creo": 10, "Rego": 8}
    mage.forms = {"Ignem": 8, "Corpus": 6}
    return mage


@pytest.fixture
def test_warrior(event_manager):
    warrior = Character(
        name="Gerhard the Strong", player="Test Player", saga="Test Saga", covenant="Test Covenant", house=None
    )
    warrior.event_manager = event_manager
    warrior.abilities["Martial"] = {"Single Weapon": 5, "Dodge": 3}
    warrior.characteristics["Strength"] = 3
    warrior.characteristics["Stamina"] = 2
    return warrior


@pytest.fixture
def combat_manager(event_manager):
    manager = CombatManager()
    manager.event_manager = event_manager
    return manager


class TestCombatSpellcastingIntegration:
    def test_spell_in_combat(self, test_mage, test_warrior, combat_manager, event_manager):
        """Test casting a spell during combat."""
        # Create a test spell
        spell = Spell.create(
            SpellParameters(
                name="Ball of Abysmal Flame",
                technique=Technique.CREO,
                form=Form.IGNEM,
                level=15,
                range=Range.VOICE,
                duration=Duration.MOMENTARY,
                target=Target.INDIVIDUAL,
            )
        )
        test_mage.spells = {spell.name: spell}

        # Cast spell
        cast_result = SpellCaster.cast_spell(spell, test_mage, aura=3)

        # Verify spell casting event
        event_manager.record_event.assert_called()
        spell_event = event_manager.record_event.call_args_list[0][0][0]
        assert spell_event.type == EventType.SPELLCASTING

        if cast_result.success:
            # If spell succeeds, resolve combat effect
            _ = combat_manager.resolve_attack(
                attacker=test_mage,
                defender=test_warrior,
                weapon="spell",
                modifiers={"spell_attack": cast_result.roll_result.total},
            )

            # Verify combat event
            combat_event = event_manager.record_event.call_args_list[-1][0][0]
            assert combat_event.type == EventType.COMBAT

            # Check fatigue accumulation
            assert test_mage.fatigue_level > 0

    def test_wounded_spellcaster(self, test_mage, combat_manager):
        """Test casting spells while wounded."""
        # Apply a wound to the mage
        wound = combat_manager._apply_damage(test_mage, 7, "sword")
        assert wound.severity == WoundSeverity.MEDIUM

        # Create and cast a test spell
        spell = Spell.create(
            SpellParameters(
                name="Test Spell",
                technique=Technique.CREO,
                form=Form.IGNEM,
                level=10,
                range=Range.VOICE,
                duration=Duration.MOMENTARY,
                target=Target.INDIVIDUAL,
            )
        )

        result = SpellCaster.cast_spell(spell, test_mage)

        # Verify wound penalties affected casting
        assert result.roll_result.total < (
            test_mage.techniques["Creo"] + test_mage.forms["Ignem"] + result.roll_result.rolls[0]
        )

    def test_fatigue_accumulation(self, test_mage, test_warrior, combat_manager):
        """Test fatigue accumulation from both combat and spellcasting."""
        spell = Spell.create(
            SpellParameters(
                name="Test Spell",
                technique=Technique.CREO,
                form=Form.IGNEM,
                level=5,
                range=Range.VOICE,
                duration=Duration.MOMENTARY,
                target=Target.INDIVIDUAL,
            )
        )

        # Cast spell multiple times
        initial_fatigue = test_mage.fatigue_level
        for _ in range(3):
            SpellCaster.cast_spell(spell, test_mage)

        # Engage in combat
        combat_manager.resolve_attack(test_mage, test_warrior, "dagger")

        # Verify cumulative fatigue
        assert test_mage.fatigue_level > initial_fatigue

        # Try casting when extremely fatigued
        test_mage.fatigue_level = 4  # Nearly unconscious
        result = SpellCaster.cast_spell(spell, test_mage)
        assert not result.success
        assert "Too fatigued" in result.botch_details

    def test_seasonal_recovery(self, test_mage, test_warrior, combat_manager):
        """Test wound and fatigue recovery over seasons."""
        # Apply wounds and fatigue
        combat_manager._apply_damage(test_warrior, 8, "mace")
        test_warrior.fatigue_level = 3

        initial_wounds = len(test_warrior.wounds)
        initial_fatigue = test_warrior.fatigue_level

        # Simulate season passing
        test_warrior.process_season(Season.SPRING, 1220)

        # Check recovery
        assert test_warrior.fatigue_level < initial_fatigue
        assert len(test_warrior.wounds) <= initial_wounds
