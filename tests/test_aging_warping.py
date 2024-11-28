from unittest.mock import Mock, patch

import pytest

from ars.aging import AgingCrisisType, AgingManager, WarpingManager, WarpingSource
from ars.character import Character
from ars.events import EventType
from ars.core.types import AbilityType, Characteristic, House


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def character():
    char = Character(
        name="Marcus", player="Test Player", saga="Test Saga", covenant="Test Covenant", house=House.BONISAGUS, age=35
    )
    # Set some base characteristics
    for char_type in Characteristic:
        char.characteristics[char_type] = 0
    return char


@pytest.fixture
def aging_manager(event_manager):
    return AgingManager(event_manager)


@pytest.fixture
def warping_manager(event_manager):
    return WarpingManager(event_manager)


class TestAgingManager:
    def test_normal_aging(self, aging_manager, character):
        """Test normal aging with no crisis."""
        with patch("random.randint", return_value=1):  # Ensures roll + modifiers <= 0
            result = aging_manager.check_aging(character, 1220, "Spring")

            assert result.crisis_type is None
            assert not result.characteristic_changes
            assert not result.died

    def test_minor_aging_crisis(self, aging_manager, character):
        """Test minor aging crisis."""
        with patch("random.randint", side_effect=[3, 1]):  # First for aging roll, second for characteristic
            result = aging_manager.check_aging(character, 1220, "Spring")

            assert result.crisis_type == AgingCrisisType.MINOR
            assert len(result.characteristic_changes) == 1
            assert not result.died
            assert any(change == -1 for change in result.characteristic_changes.values())

    def test_major_aging_crisis(self, aging_manager, character):
        """Test major aging crisis."""
        with patch("random.randint", side_effect=[5, 1, 2, 3]):  # Aging roll + characteristic selections
            result = aging_manager.check_aging(character, 1220, "Spring")

            assert result.crisis_type == AgingCrisisType.MAJOR
            assert len(result.characteristic_changes) > 0
            assert result.apparent_age_change > 0
            assert not result.died

    def test_fatal_aging_crisis(self, aging_manager, character):
        """Test fatal aging crisis."""
        with patch("random.randint", return_value=10):  # Ensures fatal crisis
            character.characteristics[Characteristic.STAMINA] = -2  # Set up for potential death

            result = aging_manager.check_aging(character, 1220, "Spring")

            assert result.crisis_type == AgingCrisisType.FATAL
            assert result.died
            assert len(result.characteristic_changes) > 0

    def test_aging_event_recording(self, aging_manager, character, event_manager):
        """Test that aging events are properly recorded."""
        with patch("random.randint", return_value=3):
            aging_manager.check_aging(character, 1220, "Spring")

            event_manager.add_event.assert_called_once()
            event = event_manager.add_event.call_args[0][0]
            assert event.type == EventType.AGING
            assert event.year == 1220
            assert event.details["character"] == "Marcus"

    def test_longevity_ritual_bonus(self, aging_manager, character):
        """Test longevity ritual effects on aging."""
        # Add longevity ritual to character
        character.abilities[AbilityType.ARCANE]["Longevity Ritual"] = 5

        with patch("random.randint", return_value=5):
            result = aging_manager.check_aging(character, 1220, "Spring")

            # Should have less severe effects due to ritual
            assert result.crisis_type != AgingCrisisType.FATAL


class TestWarpingManager:
    def test_add_warping_points(self, warping_manager, character):
        """Test adding warping points."""
        result = warping_manager.add_warping_points(
            character=character, points=3, source=WarpingSource.MAGICAL_AURA, year=1220, season="Spring"
        )

        assert result.points_gained == 3
        assert character.warping_points == 3
        assert result.new_score == 0  # Not enough for new score

    def test_warping_score_threshold(self, warping_manager, character):
        """Test reaching new warping score threshold."""
        result = warping_manager.add_warping_points(
            character=character, points=5, source=WarpingSource.SPELL_BOTCH, year=1220, season="Spring"
        )

        assert result.new_score == 1
        assert len(result.effects) > 0  # Should have generated effects

    def test_multiple_warping_scores(self, warping_manager, character):
        """Test accumulating multiple warping scores."""
        # Add points in multiple steps
        warping_manager.add_warping_points(
            character=character, points=5, source=WarpingSource.MAGICAL_AURA, year=1220, season="Spring"
        )

        result = warping_manager.add_warping_points(
            character=character, points=5, source=WarpingSource.TWILIGHT, year=1220, season="Summer"
        )

        assert result.new_score == 2
        assert len(result.effects) > 0
        assert character.warping_points == 10

    def test_warping_event_recording(self, warping_manager, character, event_manager):
        """Test that warping events are properly recorded."""
        warping_manager.add_warping_points(
            character=character, points=3, source=WarpingSource.VIS, year=1220, season="Spring"
        )

        event_manager.add_event.assert_called_once()
        event = event_manager.add_event.call_args[0][0]
        assert event.type == EventType.WARPING
        assert event.details["points_gained"] == 3
        assert event.details["source"] == WarpingSource.VIS.name

    def test_warping_effects_generation(self, warping_manager, character):
        """Test generation of different warping effects."""
        # Test minor effects
        character.warping_points = 4
        result = warping_manager.add_warping_points(
            character=character, points=1, source=WarpingSource.MAGICAL_AURA, year=1220, season="Spring"
        )
        assert len(result.effects) == 1

        # Test major effects
        character.warping_points = 9
        result = warping_manager.add_warping_points(
            character=character, points=1, source=WarpingSource.RITUAL, year=1220, season="Summer"
        )
        assert len(result.effects) == 1

        # Test powerful effects
        character.warping_points = 14
        result = warping_manager.add_warping_points(
            character=character, points=1, source=WarpingSource.ENCHANTED_ITEM, year=1220, season="Autumn"
        )
        assert len(result.effects) == 1

    def test_invalid_warping_points(self, warping_manager, character):
        """Test adding invalid (negative) warping points."""
        with pytest.raises(ValueError):
            warping_manager.add_warping_points(
                character=character, points=-1, source=WarpingSource.VIS, year=1220, season="Spring"
            )

    def test_warping_source_tracking(self, warping_manager, character):
        """Test tracking of warping sources."""
        result = warping_manager.add_warping_points(
            character=character, points=2, source=WarpingSource.TWILIGHT, year=1220, season="Spring"
        )

        assert result.source == WarpingSource.TWILIGHT
