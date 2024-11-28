from unittest.mock import Mock

import pytest

from ars.character import Character, CharacterNotFoundError
from ars.events import EventType
from ars.core.types import Season
from ars.core.types import AbilityType, Characteristic, House, ItemType
from ars.virtues_flaws import VirtueFlaw


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def test_character(event_manager):
    char = Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS,
    )
    char.event_manager = event_manager
    return char


class TestCharacter:
    def test_character_creation(self, test_character):
        """Test basic character creation."""
        assert test_character.name == "Testus of Bonisagus"
        assert test_character.house == House.BONISAGUS
        assert test_character.age == 25
        assert test_character.apparent_age == 25

    def test_add_experience(self, test_character, event_manager):
        """Test adding experience with event recording."""
        test_character.add_experience(ability="Magic Theory", points=5, year=1220, season=Season.SPRING)

        assert test_character.abilities.get("Magic Theory") == 5

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.SEASONAL_ACTIVITY
        assert "Magic Theory" in event.description
        assert event.details["points_gained"] == 5
        assert event.details["new_value"] == 5
        assert event.year == 1220
        assert event.season == Season.SPRING

    def test_add_warping_points(self, test_character, event_manager):
        """Test adding warping points with event recording."""
        test_character.add_warping_points(points=3, source="Magical experimentation", year=1220, season=Season.SPRING)

        assert test_character.warping_points == 3
        assert test_character.warping_score == 0  # Not enough for score increase

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.WARPING
        assert "warping points" in event.description
        assert event.details["points_gained"] == 3
        assert event.details["source"] == "Magical experimentation"
        assert not event.details["score_increased"]

    def test_warping_score_increase(self, test_character, event_manager):
        """Test warping score increase with event recording."""
        test_character.add_warping_points(points=5, source="Powerful magic", year=1220, season=Season.SPRING)

        assert test_character.warping_points == 5
        assert test_character.warping_score == 1

        event = event_manager.record_event.call_args[0][0]
        assert event.details["score_increased"]
        assert event.details["new_score"] == 1

    def test_add_decrepitude_points(self, test_character, event_manager):
        """Test adding decrepitude points with event recording."""
        test_character.add_decrepitude_points(points=2, source="Aging crisis", year=1220, season=Season.SPRING)

        assert test_character.decrepitude_points == 2
        assert test_character.decrepitude_score == 0

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.AGING
        assert "decrepitude points" in event.description
        assert event.details["points_gained"] == 2
        assert event.details["source"] == "Aging crisis"

    def test_decrepitude_score_increase(self, test_character, event_manager):
        """Test decrepitude score increase with event recording."""
        test_character.add_decrepitude_points(points=5, source="Major aging crisis", year=1220, season=Season.SPRING)

        assert test_character.decrepitude_points == 5
        assert test_character.decrepitude_score == 1

        event = event_manager.record_event.call_args[0][0]
        assert event.details["score_increased"]
        assert event.details["new_score"] == 1

    def test_virtues_and_flaws(self, test_character):
        """Test adding virtues and flaws."""
        virtue = VirtueFlaw(
            name="The Gift", category="Hermetic", is_virtue=True, description="The ability to use Hermetic magic"
        )
        flaw = VirtueFlaw(
            name="Weak Magic", category="Hermetic", is_virtue=False, description="Magic is weaker than normal"
        )

        test_character.add_virtue(virtue)
        test_character.add_flaw(flaw)

        assert virtue in test_character.virtues
        assert flaw in test_character.flaws

        with pytest.raises(ValueError):
            test_character.add_virtue(flaw)
        with pytest.raises(ValueError):
            test_character.add_flaw(virtue)

    def test_can_enchant(self, test_character):
        """Test magic item creation requirements."""
        # Without Magic Theory
        assert not test_character.can_enchant(ItemType.CHARGED)

        # Add sufficient Magic Theory for charged items
        test_character.abilities[AbilityType.ARCANE]["Magic Theory"] = 3
        assert test_character.can_enchant(ItemType.CHARGED)
        assert not test_character.can_enchant(ItemType.INVESTED)

        # Add more Magic Theory for invested items
        test_character.abilities[AbilityType.ARCANE]["Magic Theory"] = 5
        assert test_character.can_enchant(ItemType.INVESTED)
        assert not test_character.can_enchant(ItemType.TALISMAN)

    def test_save_load(self, test_character, tmp_path):
        """Test character serialization and deserialization."""
        # Add some data
        test_character.characteristics[Characteristic.INTELLIGENCE] = 3
        test_character.abilities[AbilityType.ARCANE]["Magic Theory"] = 4
        test_character.add_personality_trait("Brave", 3)

        # Save and load
        save_path = tmp_path / "characters"
        test_character.save(save_path)

        loaded_char = Character.load(test_character.name, save_path)

        assert loaded_char.name == test_character.name
        assert loaded_char.characteristics[Characteristic.INTELLIGENCE] == 3
        assert loaded_char.abilities[AbilityType.ARCANE]["Magic Theory"] == 4
        assert loaded_char.personality_traits["Brave"] == 3

    def test_character_not_found(self, tmp_path):
        """Test loading non-existent character."""
        with pytest.raises(CharacterNotFoundError):
            Character.load("NonExistent", tmp_path)

    def test_list_characters(self, tmp_path):
        """Test listing saved characters."""
        # Create test character files
        char_dir = tmp_path / "characters"
        char_dir.mkdir()
        (char_dir / "test1.yml").touch()
        (char_dir / "test2.yml").touch()

        characters = Character.list_characters(char_dir)
        assert "test1" in characters
        assert "test2" in characters
