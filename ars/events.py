from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ars.core.types import EventType, Season


@dataclass
class EventContext:
    """Maintains the current game state context."""
    year: int
    season: Season
    location: Optional[str] = None

    def advance_season(self):
        """Advance to the next season."""
        if self.season == Season.WINTER:
            self.season = Season.SPRING
            self.year += 1
        else:
            self.season = Season.next_season(self.season)


@dataclass
class Event:
    """Represents a game event."""
    type: EventType
    year: Optional[int] = None
    season: Optional[Season] = None
    character: Optional[str] = None
    location: Optional[str] = None
    details: Dict[str, Any] = None
    id: UUID = None
    timestamp: datetime = None

    def __post_init__(self):
        """Initialize optional fields if not provided."""
        if self.id is None:
            self.id = uuid4()
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'id': str(self.id),
            'type': self.type.name,
            'year': self.year,
            'season': self.season,
            'character': self.character,
            'location': self.location,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            id=UUID(data['id']),
            type=EventType[data['type']],
            year=data['year'],
            season=data['season'],
            character=data['character'],
            location=data['location'],
            details=data['details'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class EventRecorder:
    """Base class for objects that can record events."""
    
    def __init__(self):
        self.event_manager = None

    def __post_init__(self):
        """Called after dataclass initialization."""
        self.event_manager = None

    def record_event(self, event_type: EventType, details: Dict[str, Any] = None) -> None:
        """Record an event if event manager is set, using context for temporal info."""
        if self.event_manager is not None:
            event = Event(
                type=event_type,
                year=None,  # Will be filled from context
                season=None,  # Will be filled from context
                character=getattr(self, 'name', None),
                location=None,  # Will be filled from context
                details=details or {}
            )
            self.event_manager.add_event(event)


class EventManager:
    """Manages game events and notifications."""
    
    def __init__(self, context: Optional[EventContext] = None):
        self._events: List[Event] = []
        self._observers: List[callable] = []
        self.context = context or EventContext(year=1220, season=Season.SPRING)

    def add_event(self, event: Event) -> None:
        """Add a new event and notify observers."""
        # If event doesn't specify year/season, use context
        if event.year is None:
            event.year = self.context.year
        if event.season is None:
            event.season = self.context.season
        if event.location is None:
            event.location = self.context.location

        self._events.append(event)
        self._notify_observers(event)

    def add_observer(self, observer: callable) -> None:
        """Add an observer to be notified of events."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: callable) -> None:
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, event: Event) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            observer(event)

    def get_events(self, 
                  event_type: Optional[EventType] = None,
                  character: Optional[str] = None,
                  start_year: Optional[int] = None,
                  end_year: Optional[int] = None,
                  location: Optional[str] = None) -> List[Event]:
        """Get events matching the specified filters."""
        filtered_events = self._events

        if event_type:
            filtered_events = [e for e in filtered_events if e.type == event_type]
        if character:
            filtered_events = [e for e in filtered_events if e.character == character]
        if start_year:
            filtered_events = [e for e in filtered_events if e.year >= start_year]
        if end_year:
            filtered_events = [e for e in filtered_events if e.year <= end_year]
        if location:
            filtered_events = [e for e in filtered_events if e.location == location]

        return filtered_events

    def clear_events(self) -> None:
        """Clear all events."""
        self._events.clear()

    def save_events(self, filepath: str) -> None:
        """Save events to file."""
        import json
        with open(filepath, 'w') as f:
            json.dump([e.to_dict() for e in self._events], f)

    def load_events(self, filepath: str) -> None:
        """Load events from file."""
        import json
        with open(filepath, 'r') as f:
            events_data = json.load(f)
            self._events = [Event.from_dict(e) for e in events_data]
