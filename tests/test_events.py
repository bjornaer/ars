import pytest
from ars.events import Event, EventManager, EventContext, EventRecorder
from ars.core.types import EventType, Season

def test_event_context_management():
    """Test event context management."""
    context = EventContext(year=1220, season=Season.SPRING)
    manager = EventManager(context)
    
    event = Event(
        type=EventType.SPELLCASTING,
        details={"spell_name": "Test Spell"}
    )
    
    manager.add_event(event)
    
    # Event should have context information
    assert event.year == 1220
    assert event.season == Season.SPRING

def test_season_advancement():
    """Test season advancement in context."""
    context = EventContext(year=1220, season=Season.WINTER)
    context.advance_season()
    
    assert context.year == 1221
    assert context.season == Season.SPRING

def test_event_recording_with_context():
    """Test event recording using context."""
    context = EventContext(
        year=1220,
        season=Season.SPRING,
        location="Test Covenant"
    )
    manager = EventManager(context)
    
    class TestRecorder(EventRecorder):
        def __init__(self, name):
            super().__init__()
            self.name = name
    
    recorder = TestRecorder("Test Character")
    recorder.event_manager = manager
    
    recorder.record_event(
        event_type=EventType.SPELLCASTING,
        details={"action": "test"}
    )
    
    events = manager.get_events()
    assert len(events) == 1
    assert events[0].year == 1220
    assert events[0].season == Season.SPRING
    assert events[0].location == "Test Covenant"
    assert events[0].character == "Test Character"