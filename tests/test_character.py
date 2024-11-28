import pytest

from ars.character import Character, CharacterNotFoundError
from ars.events import EventType
from ars.core.types import (
    AbilityType, Characteristic, Duration, House, Range, Season,
    Form, Target, Technique
)


class TestCharacter:
    def test_character_creation(self, base_character):
        """Test basic character creation and initialization."""
        assert base_character.name == "Testus of Bonisagus"
        assert base_character.house == House.BONISAGUS
        assert base_character.age == 25  # Default starting age
        assert base_character.apparent_age == 25
        
        # Test initial arts
        assert base_character.techniques[Technique.CREO] == 10
        assert base_character.techniques[Technique.REGO] == 8
        assert base_character.forms[Form.IGNEM] == 8
        assert base_character.forms[Form.VIM] == 6
        
        # Test initial characteristics
        assert base_character.characteristics[Characteristic.INTELLIGENCE] == 3
        assert base_character.characteristics[Characteristic.STAMINA] == 2
        
        # Test initial abilities
        assert base_character.abilities[AbilityType.ARCANE]["Magic Theory"] == 4
        assert base_character.abilities[AbilityType.ARCANE]["Parma Magica"] == 1

    def test_add_experience(self, base_character, event_manager):
        """Test adding experience with event recording."""
        base_character.add_experience(
            ability="Magic Theory",
            points=5,
            year=1220,
            season=Season.SPRING
        )

        # Verify experience was added
        assert base_character.abilities[AbilityType.ARCANE]["Magic Theory"] == 9

        # Verify event was recorded
        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.EXPERIENCE_GAIN
        assert event.details["ability"] == "Magic Theory"
        assert event.details["points_gained"] == 5
        assert event.details["new_value"] == 9
        assert event.year == 1220
        assert event.season == Season.SPRING

    def test_save_load(self, base_character, tmp_saga_path):
        """Test character serialization and deserialization."""
        # Add some additional data
        base_character.add_personality_trait("Brave", 3)
        base_character.techniques[Technique.PERDO] = 5
        base_character.forms[Form.CORPUS] = 4

        # Save character
        base_character.save(directory=tmp_saga_path)

        # Load character
        loaded_char = Character.load(base_character.name, directory=tmp_saga_path)

        # Verify basic attributes
        assert loaded_char.name == base_character.name
        assert loaded_char.house == base_character.house
        assert loaded_char.age == base_character.age

        # Verify arts
        assert loaded_char.techniques[Technique.CREO] == base_character.techniques[Technique.CREO]
        assert loaded_char.techniques[Technique.PERDO] == 5
        assert loaded_char.forms[Form.IGNEM] == base_character.forms[Form.IGNEM]
        assert loaded_char.forms[Form.CORPUS] == 4

        # Verify characteristics and abilities
        assert loaded_char.characteristics[Characteristic.INTELLIGENCE] == 3
        assert loaded_char.abilities[AbilityType.ARCANE]["Magic Theory"] == 4

        # Verify personality traits
        assert loaded_char.personality_traits["Brave"] == 3

    def test_character_not_found(self, tmp_saga_path):
        """Test loading non-existent character."""
        with pytest.raises(CharacterNotFoundError):
            Character.load("NonExistent", tmp_saga_path)

    def test_list_characters(self, base_character, tmp_saga_path):
        """Test listing saved characters."""
        # Save test character
        base_character.save(directory=tmp_saga_path)

        # List characters
        characters = Character.list_characters(tmp_saga_path)
        assert "testus_of_bonisagus" in characters

    def test_add_spell(self, base_character, event_manager):
        """Test adding spells to character."""
        from ars.spells import Spell, SpellParameters
        
        spell = Spell(
            name="Test Flame",
            technique=Technique.CREO,
            form=Form.IGNEM,
            level=10,
            parameters=SpellParameters(
                range=Range.VOICE,
                duration=Duration.DIAMETER,
                target=Target.INDIVIDUAL
            )
        )
        
        base_character.add_spell(spell)
        
        # Verify spell was added
        assert spell.name in base_character.spells
        
        # Verify event recording
        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.SPELLCASTING
        assert event.details["action"] == "learn_spell"
        assert event.details["spell_name"] == spell.name