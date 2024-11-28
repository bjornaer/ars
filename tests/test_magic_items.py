from unittest.mock import Mock

import pytest

from ars.character import Character
from ars.events import EventType
from ars.laboratory import Laboratory
from ars.magic_items import InstallationType, ItemCreationManager, ItemEffect, ItemType, MagicItem
from ars.core.types import Season
from ars.core.types import Form, Technique


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def test_character():
    char = Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house="Bonisagus",
    )
    char.techniques = {"Creo": 10, "Rego": 8}
    char.forms = {"Ignem": 8, "Vim": 6}
    return char


@pytest.fixture
def test_laboratory():
    return Laboratory(owner="Testus of Bonisagus", size=3, magical_aura=3)


@pytest.fixture
def test_item():
    return MagicItem(
        name="Test Ring",
        type=ItemType.INVESTED,
        creator="Testus of Bonisagus",
        base_material="Silver",
        size=1,
        shape_bonus=1,
        material_bonus=2,
        vis_capacity=10,
    )


@pytest.fixture
def test_effect():
    return ItemEffect(
        name="Flame Burst",
        technique=Technique.CREO,
        form=Form.IGNEM,
        level=10,
        installation_type=InstallationType.EFFECT,
    )


@pytest.fixture
def item_manager(event_manager):
    return ItemCreationManager(event_manager)


class TestItemCreation:
    def test_start_project_success(
        self, item_manager, test_character, test_laboratory, test_item, test_effect, event_manager
    ):
        """Test successful project start with event recording."""
        result = item_manager.start_project(
            test_character, test_laboratory, test_item, test_effect, year=1220, season=Season.SPRING
        )

        assert result is True
        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.ITEM_CREATION
        assert "Started creation" in event.description
        assert event.details["character"] == test_character.name
        assert event.details["lab_total"] > 0

    def test_start_project_capacity_exceeded(self, item_manager, test_character, test_laboratory, event_manager):
        """Test project start failure due to capacity."""
        item = MagicItem(
            name="Small Ring",
            type=ItemType.INVESTED,
            creator="Testus of Bonisagus",
            base_material="Silver",
            size=0,
            vis_capacity=5,
            current_capacity=5,  # Already full
        )

        effect = ItemEffect(name="Big Effect", technique=Technique.CREO, form=Form.IGNEM, level=20)

        result = item_manager.start_project(
            test_character, test_laboratory, item, effect, year=1220, season=Season.SPRING
        )

        assert result is False
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.ITEM_CREATION
        assert "Failed to start item creation" in event.description
        assert "capacity" in event.details["reason"].lower()

    def test_continue_project_with_vis(
        self, item_manager, test_character, test_laboratory, test_item, test_effect, event_manager
    ):
        """Test project continuation with vis requirements."""
        # Start project
        item_manager.start_project(
            test_character, test_laboratory, test_item, test_effect, year=1220, season=Season.SPRING
        )

        # Mock vis manager
        vis_manager = Mock()
        vis_manager.use_vis.return_value = True

        result = item_manager.continue_project(
            test_character, test_laboratory, vis_manager, year=1220, season=Season.SUMMER
        )

        assert result["status"] in ["completed", "in_progress"]
        assert event_manager.record_event.call_count >= 2  # Start + Continue events

    def test_project_completion(
        self, item_manager, test_character, test_laboratory, test_item, test_effect, event_manager
    ):
        """Test successful project completion."""
        # Start project with minimal seasons required
        test_effect.seasons_required = 1
        item_manager.start_project(
            test_character, test_laboratory, test_item, test_effect, year=1220, season=Season.SPRING
        )

        result = item_manager.continue_project(test_character, test_laboratory, year=1220, season=Season.SUMMER)

        assert result["status"] == "completed"
        assert test_item in result["item"].effects
        completion_event = event_manager.record_event.call_args[0][0]
        assert "Completed installation" in completion_event.description

    def test_insufficient_vis(
        self, item_manager, test_character, test_laboratory, test_item, test_effect, event_manager
    ):
        """Test project continuation with insufficient vis."""
        # Start project
        item_manager.start_project(
            test_character, test_laboratory, test_item, test_effect, year=1220, season=Season.SPRING
        )

        # Mock vis manager that returns False for vis use
        vis_manager = Mock()
        vis_manager.use_vis.return_value = False

        result = item_manager.continue_project(
            test_character, test_laboratory, vis_manager, year=1220, season=Season.SUMMER
        )

        assert "error" in result
        assert "Insufficient" in result["error"]
        error_event = event_manager.record_event.call_args[0][0]
        assert "Failed to continue project" in error_event.description

    def test_save_load_state(self, item_manager, test_character, test_laboratory, test_item, test_effect, tmp_path):
        """Test saving and loading project state."""
        # Start project
        item_manager.start_project(
            test_character, test_laboratory, test_item, test_effect, year=1220, season=Season.SPRING
        )

        # Save state
        state_path = tmp_path / "test_projects.yml"
        item_manager.save_state(state_path)

        # Load state in new manager
        new_manager = ItemCreationManager.load_state(state_path)
        assert test_character.name in new_manager.current_projects
        loaded_item, loaded_effect = new_manager.current_projects[test_character.name]
        assert loaded_item.name == test_item.name
        assert loaded_effect.name == test_effect.name
