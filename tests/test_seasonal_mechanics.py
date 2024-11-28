from unittest.mock import Mock, patch

import pytest

from ars.character import Character
from ars.events import EventType
from ars.seasonal_mechanics import AgingCrisis, SeasonalMechanicsManager, WarpingSource
from ars.core.types import Characteristic, House


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def mechanics_manager(event_manager):
    return SeasonalMechanicsManager(event_manager)


@pytest.fixture
def test_character():
    char = Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS,
        age=50,  # Set to 50 to make aging more likely
    )
    # Set initial characteristics
    for char_type in Characteristic:
        char.characteristics[char_type] = 0
    return char


class TestAgingMechanics:
    def test_no_aging_crisis(self, mechanics_manager, test_character):
        """Test when no aging crisis occurs."""
        # Force low aging roll
        with patch("ars.dice.DiceRoller.stress_die", return_value=1):
            result = mechanics_manager.process_aging(test_character, 1220, "Spring")

            assert result.crisis == AgingCrisis.NONE
            assert not result.characteristic_changes
            assert result.warping_gained == 0
            assert not result.died

    def test_minor_aging_crisis(self, mechanics_manager, test_character):
        """Test minor aging crisis."""
        # Force appropriate aging roll for minor crisis
        with patch("ars.dice.DiceRoller.stress_die", return_value=30):
            result = mechanics_manager.process_aging(test_character, 1220, "Spring")

            assert result.crisis == AgingCrisis.MINOR
            assert len(result.characteristic_changes) == 1
            assert result.warping_gained == 1
            assert result.warping_source == WarpingSource.AGING
            assert any(change == -1 for change in result.characteristic_changes.values())

    def test_major_aging_crisis(self, mechanics_manager, test_character):
        """Test major aging crisis."""
        # Force appropriate aging roll for major crisis
        with patch("ars.dice.DiceRoller.stress_die", return_value=40):
            result = mechanics_manager.process_aging(test_character, 1220, "Spring")

            assert result.crisis == AgingCrisis.MAJOR
            assert len(result.characteristic_changes) == 2
            assert result.warping_gained == 2
            assert result.apparent_age_change >= 2

    def test_critical_aging_crisis(self, mechanics_manager, test_character):
        """Test critical aging crisis."""
        # Force high aging roll
        with patch("ars.dice.DiceRoller.stress_die", return_value=60):
            result = mechanics_manager.process_aging(test_character, 1220, "Spring")

            assert result.crisis == AgingCrisis.CRITICAL
            assert len(result.characteristic_changes) == 3
            assert result.warping_gained == 3
            assert result.apparent_age_change >= 5

    def test_death_from_aging(self, mechanics_manager, test_character):
        """Test death from aging crisis."""
        # Set a characteristic close to death
        test_character.characteristics[Characteristic.STAMINA] = -2

        # Force critical aging that will affect Stamina
        with patch("random.choice", return_value=Characteristic.STAMINA):
            with patch("ars.dice.DiceRoller.stress_die", return_value=60):
                result = mechanics_manager.process_aging(test_character, 1220, "Spring")

                assert result.died
                assert test_character.characteristics[Characteristic.STAMINA] <= -3

    def test_longevity_ritual_effect(self, mechanics_manager, test_character):
        """Test longevity ritual affecting aging."""
        test_character.longevity_ritual_bonus = 10

        # Even with high roll, should be reduced by ritual
        with patch("ars.dice.DiceRoller.stress_die", return_value=30):
            result = mechanics_manager.process_aging(test_character, 1220, "Spring")

            assert result.crisis == AgingCrisis.MINOR  # Would have been MAJOR without ritual

    def test_apparent_age_tracking(self, mechanics_manager, test_character):
        """Test apparent age changes."""
        initial_age = test_character.age

        # Force major crisis for age change
        with patch("ars.dice.DiceRoller.stress_die", return_value=40):
            with patch("random.randint", return_value=3):  # Force specific age change
                result = mechanics_manager.process_aging(test_character, 1220, "Spring")

                assert result.apparent_age_change == 3
                assert test_character.apparent_age == initial_age + 3

    def test_event_recording(self, mechanics_manager, test_character, event_manager):
        """Test that aging events are properly recorded."""
        # Force minor crisis for consistent testing
        with patch("ars.dice.DiceRoller.stress_die", return_value=30):
            mechanics_manager.process_aging(test_character, 1220, "Spring")

            event_manager.add_event.assert_called_once()
            event = event_manager.add_event.call_args[0][0]

            assert event.type == EventType.AGING
            assert event.year == 1220
            assert event.season == "Spring"
            assert "character" in event.details
            assert "crisis_type" in event.details
            assert "characteristic_changes" in event.details
            assert "warping_gained" in event.details

    def test_multiple_characteristic_changes(self, mechanics_manager, test_character):
        """Test that multiple characteristics can be affected."""
        # Force critical crisis
        with patch("ars.dice.DiceRoller.stress_die", return_value=60):
            result = mechanics_manager.process_aging(test_character, 1220, "Spring")

            # Verify different characteristics were affected
            affected_chars = set(result.characteristic_changes.keys())
            assert len(affected_chars) == 3
            assert all(isinstance(char, Characteristic) for char in affected_chars)

    def test_description_generation(self, mechanics_manager, test_character):
        """Test aging description generation."""
        # Force minor crisis
        with patch("ars.dice.DiceRoller.stress_die", return_value=30):
            result = mechanics_manager.process_aging(test_character, 1220, "Spring")

            assert "Age crisis: Minor" in result.description
            assert "Lost" in result.description
            assert "Warping Point" in result.description
