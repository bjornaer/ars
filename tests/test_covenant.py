from unittest.mock import Mock

import pytest

from ars.covenant import Building, BuildingType, Covenant, CovenantSize, VisSource
from ars.events import EventType
from ars.core.types import Season
from ars.core.types import Form


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def test_covenant(event_manager):
    covenant = Covenant(name="Test Covenant", size=CovenantSize.MEDIUM, age=50, aura=3)
    covenant.event_manager = event_manager
    return covenant


@pytest.fixture
def test_building():
    return Building(type=BuildingType.LABORATORY, name="Test Laboratory", size=3, quality=2, maintenance_cost=10)


@pytest.fixture
def test_vis_source():
    return VisSource(
        name="Sacred Spring",
        form=Form.AQUAM,
        amount=3,
        season="Spring",
        description="A magical spring that produces Aquam vis",
    )


class TestCovenant:
    def test_add_building(self, test_covenant, test_building, event_manager):
        """Test adding a building with event recording."""
        test_covenant.add_building(test_building, year=1220, season=Season.SPRING)

        assert test_building in test_covenant.buildings
        assert test_covenant.expenses == test_building.maintenance_cost

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.COVENANT_CHANGE
        assert test_building.name in event.description
        assert event.details["building_type"] == BuildingType.LABORATORY.value
        assert event.details["maintenance_cost"] == test_building.maintenance_cost

    def test_add_vis_source(self, test_covenant, test_vis_source, event_manager):
        """Test adding a vis source with event recording."""
        test_covenant.add_vis_source(test_vis_source, year=1220, season=Season.SPRING)

        assert test_vis_source in test_covenant.vis_sources

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.VIS_COLLECTION
        assert test_vis_source.name in event.description
        assert event.details["form"] == Form.AQUAM.value
        assert event.details["amount"] == test_vis_source.amount

    def test_collect_vis(self, test_covenant, test_vis_source, event_manager):
        """Test collecting vis with event recording."""
        test_covenant.add_vis_source(test_vis_source)
        event_manager.reset_mock()  # Reset mock after adding source

        collected = test_covenant.collect_vis(season="Spring", year=1220)

        assert collected[Form.AQUAM] == test_vis_source.amount
        assert test_covenant.vis_stocks[Form.AQUAM] == test_vis_source.amount
        assert test_vis_source.claimed

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.VIS_COLLECTION
        assert "Collected" in event.description
        assert event.details["new_stock"] == test_vis_source.amount

    def test_add_book(self, test_covenant, event_manager):
        """Test adding a book with event recording."""
        test_covenant.add_book(name="De Magica", level=10, year=1220, season=Season.SPRING)

        assert "De Magica" in test_covenant.library.books
        assert test_covenant.library.books["De Magica"] == 10

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.COVENANT_CHANGE
        assert "De Magica" in event.description
        assert event.details["level"] == 10

    def test_add_magus(self, test_covenant, event_manager):
        """Test adding a magus with event recording."""
        test_covenant.add_magus(name="Marcus of Bonisagus", year=1220, season=Season.SPRING)

        assert "Marcus of Bonisagus" in test_covenant.magi

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.COVENANT_CHANGE
        assert "Marcus of Bonisagus" in event.description
        assert event.details["total_magi"] == 1

    def test_remove_magus(self, test_covenant, event_manager):
        """Test removing a magus with event recording."""
        test_covenant.add_magus("Marcus of Bonisagus")
        event_manager.reset_mock()  # Reset mock after adding magus

        test_covenant.remove_magus(name="Marcus of Bonisagus", reason="died", year=1220, season=Season.SPRING)

        assert "Marcus of Bonisagus" not in test_covenant.magi

        event_manager.record_event.assert_called_once()
        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.COVENANT_CHANGE
        assert "died" in event.description
        assert event.details["total_magi"] == 0

    def test_library_capacity(self, test_covenant, event_manager):
        """Test library capacity limit with event recording."""
        test_covenant.library.capacity = 1
        test_covenant.add_book("Book 1", 10)

        with pytest.raises(ValueError, match="Library capacity reached"):
            test_covenant.add_book("Book 2", 5)

    def test_serialization(self, test_covenant, test_building, test_vis_source, tmp_path):
        """Test covenant serialization and deserialization."""
        # Add some data
        test_covenant.add_building(test_building)
        test_covenant.add_vis_source(test_vis_source)
        test_covenant.add_magus("Marcus of Bonisagus")

        # Convert to dict and back
        data = test_covenant.to_dict()
        loaded_covenant = Covenant.from_dict(data)

        assert loaded_covenant.name == test_covenant.name
        assert loaded_covenant.size == test_covenant.size
        assert len(loaded_covenant.buildings) == len(test_covenant.buildings)
        assert len(loaded_covenant.vis_sources) == len(test_covenant.vis_sources)
        assert loaded_covenant.magi == test_covenant.magi

    def test_aura_effects(self, test_covenant):
        """Test applying aura effects."""
        initial_aura = test_covenant.aura
        test_covenant.apply_aura_effects({"magical_activities": 2, "vis_extraction": 1})

        assert test_covenant.aura == initial_aura + 2
        for source in test_covenant.vis_sources:
            assert source.amount >= 1  # Should never go below 1
