from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ars.core.types import Season, EventType, SeasonalActivity


@dataclass
class GameEvent:
    """Represents a game event."""

    type: EventType
    description: str
    details: Dict[str, Any]
    year: int
    season: Season
    timestamp: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)


class EventManager:
    """Manages game events."""

    def __init__(self):
        self.events: List[GameEvent] = []
        self.observers: List[callable] = []

    def add_event(self, event: GameEvent) -> None:
        """Add a new event and notify observers."""
        self.events.append(event)
        self._notify_observers(event)

    def get_events(
        self,
        event_type: Optional[EventType] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        character: Optional[str] = None,
    ) -> List[GameEvent]:
        """Get filtered events."""
        filtered = self.events

        if event_type:
            filtered = [e for e in filtered if e.type == event_type]
        if start_year:
            filtered = [e for e in filtered if e.year >= start_year]
        if end_year:
            filtered = [e for e in filtered if e.year <= end_year]
        if character:
            filtered = [e for e in filtered if character in str(e.details.get("character", ""))]

        return filtered

    def add_observer(self, observer: callable) -> None:
        """Add an observer to be notified of new events."""
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer: callable) -> None:
        """Remove an observer."""
        if observer in self.observers:
            self.observers.remove(observer)

    def _notify_observers(self, event: GameEvent) -> None:
        """Notify all observers of a new event."""
        for observer in self.observers:
            observer(event)

    def clear_events(self) -> None:
        """Clear all events."""
        self.events.clear()


class EventRecorder:
    """Mixin class for objects that need to record events."""

    def __init__(self, event_manager: Optional[EventManager] = None):
        self.event_manager = event_manager

    def record_event(
        self, type: EventType, description: str, details: Dict[str, Any], year: int, season: Season
    ) -> None:
        """Record a game event if event manager exists."""
        if self.event_manager:
            event = GameEvent(type=type, description=description, details=details, year=year, season=season)
            self.event_manager.add_event(event)


class SeasonalEventManager(EventRecorder):
    """Manages seasonal events."""

    def __init__(self, season_manager):
        super().__init__(season_manager.event_manager)
        self.season_manager = season_manager

    def record_season_change(self, new_season: Season) -> None:
        """Record a season change event."""
        self.record_event(
            type=EventType.SEASON_CHANGE,
            description=f"Season changed to {new_season.value}",
            details={"previous_season": self.season_manager.current_season, "new_season": new_season},
            year=self.season_manager.current_year,
            season=new_season,
        )

    def record_activity(self, activity: "SeasonalActivity", results: Dict[str, Any]) -> None:
        """Record a seasonal activity event."""
        self.record_event(
            type=EventType.SEASONAL_ACTIVITY,
            description=f"{activity.character.name} performed {activity.type.value}",
            details={
                "character": activity.character.name,
                "activity_type": activity.type.value,
                "activity_details": activity.details,
                "results": results,
            },
            year=activity.year,
            season=activity.season,
        )
