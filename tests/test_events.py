from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

from ars.events import EventManager, EventRecorder, EventType, GameEvent, SeasonalEventManager
from ars.core.types import Season


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def event_recorder(event_manager):
    return EventRecorder(event_manager)


@pytest.fixture
def sample_event():
    return GameEvent(
        type=EventType.SEASONAL_ACTIVITY,
        description="Test activity",
        details={"character": "Marcus", "activity_type": "Study", "results": {"experience": 5}},
        year=1220,
        season=Season.SPRING,
    )


class TestEventSystem:
    def test_event_creation(self, sample_event):
        """Test basic event creation and attributes."""
        assert sample_event.type == EventType.SEASONAL_ACTIVITY
        assert sample_event.year == 1220
        assert sample_event.season == Season.SPRING
        assert isinstance(sample_event.id, UUID)
        assert isinstance(sample_event.timestamp, datetime)

    def test_event_manager_filtering(self, event_manager, sample_event):
        """Test event filtering capabilities."""
        event_manager.add_event(sample_event)

        # Test type filtering
        assert len(event_manager.get_events(event_type=EventType.SEASONAL_ACTIVITY)) == 1
        assert len(event_manager.get_events(event_type=EventType.AGING)) == 0

        # Test year filtering
        assert len(event_manager.get_events(start_year=1219)) == 1
        assert len(event_manager.get_events(end_year=1219)) == 0

        # Test character filtering
        assert len(event_manager.get_events(character="Marcus")) == 1
        assert len(event_manager.get_events(character="Unknown")) == 0

    def test_observer_pattern(self, event_manager, sample_event):
        """Test observer notification system."""
        mock_observer = Mock()
        event_manager.add_observer(mock_observer)

        event_manager.add_event(sample_event)
        mock_observer.assert_called_once_with(sample_event)

        # Test observer removal
        event_manager.remove_observer(mock_observer)
        event_manager.add_event(sample_event)
        assert mock_observer.call_count == 1

    def test_event_recorder(self, event_recorder, event_manager):
        """Test EventRecorder mixin."""
        event_recorder.record_event(
            type=EventType.AGING,
            description="Test aging",
            details={"character": "Marcus"},
            year=1220,
            season=Season.SPRING,
        )

        events = event_manager.get_events(event_type=EventType.AGING)
        assert len(events) == 1
        assert events[0].description == "Test aging"

    def test_seasonal_event_manager(self, season_manager):
        """Test SeasonalEventManager functionality."""
        seasonal_manager = SeasonalEventManager(season_manager)

        # Test season change recording
        seasonal_manager.record_season_change(Season.SUMMER)

        events = season_manager.event_manager.get_events(event_type=EventType.SEASON_CHANGE)
        assert len(events) == 1
        assert events[0].details["new_season"] == Season.SUMMER
