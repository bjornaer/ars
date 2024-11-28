import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from ars.character import Character
from ars.covenant import Covenant
from ars.dice import DiceRoller
from ars.events import Event
from ars.core.types import EventType, Season, Characteristic


class AgingCrisis(Enum):
    """Types of aging crises."""

    NONE = "None"
    MINOR = "Minor"
    MAJOR = "Major"
    CRITICAL = "Critical"


class WarpingSource(Enum):
    """Sources of warping points."""

    AGING = "Aging"
    MAGICAL_AURA = "Magical Aura"
    SPELL_BOTCH = "Spell Botch"
    TWILIGHT = "Twilight"
    RITUAL = "Ritual"
    ENCHANTED_ITEM = "Enchanted Item"
    VIS = "Vis"


@dataclass
class AgingResult:
    """Result of an aging roll."""

    crisis: AgingCrisis
    characteristic_changes: Dict[Characteristic, int] = field(default_factory=dict)
    apparent_age_change: int = 0
    warping_gained: int = 0
    warping_source: Optional[WarpingSource] = None
    description: str = ""
    died: bool = False


class WeatherType(Enum):
    """Types of seasonal weather."""

    MILD = "Mild"
    HARSH = "Harsh"
    SEVERE = "Severe"
    EXTRAORDINARY = "Extraordinary"


@dataclass
class WeatherEffect:
    """Weather effects for a season."""

    type: WeatherType
    description: str
    modifiers: Dict[str, int] = field(default_factory=dict)


@dataclass
class SeasonalEvent:
    """An event that occurs during a season."""

    type: EventType
    title: str
    description: str
    severity: int  # 1-5
    effects: Dict[str, any] = field(default_factory=dict)


class SeasonalMechanicsManager:
    """Manages seasonal mechanics like aging, weather, and events."""

    def __init__(self, event_manager=None):
        self.weather_effects: Dict[Season, WeatherEffect] = {}
        self.events: List[SeasonalEvent] = []
        self.event_manager = event_manager

    def process_aging(self, character: Character, year: int, season: str) -> AgingResult:
        """Process aging for a character."""
        # Base aging roll
        apparent_age = character.apparent_age or character.age
        aging_roll = max(0, DiceRoller.stress_die() - character.longevity_ritual_bonus)

        # Determine crisis level
        crisis = AgingCrisis.NONE
        if aging_roll > apparent_age // 2:
            crisis = AgingCrisis.MINOR
        if aging_roll > apparent_age * 2 // 3:
            crisis = AgingCrisis.MAJOR
        if aging_roll > apparent_age:
            crisis = AgingCrisis.CRITICAL

        result = AgingResult(crisis=crisis)

        if crisis != AgingCrisis.NONE:
            # Determine characteristic changes
            changes = self._calculate_characteristic_changes(crisis)
            result.characteristic_changes = changes

            # Apply changes to character
            for char, change in changes.items():
                character.characteristics[char] += change

                # Check for death
                if character.characteristics[char] <= -3:
                    result.died = True

            # Calculate apparent age change
            result.apparent_age_change = self._calculate_age_change(crisis)
            character.apparent_age = (character.apparent_age or character.age) + result.apparent_age_change

            # Apply warping points
            result.warping_gained = len(changes)  # One point per characteristic affected
            result.warping_source = WarpingSource.AGING
            character.warping_points += result.warping_gained

            # Create description
            result.description = self._create_aging_description(crisis, changes, result)

            # Record event if event manager exists
            if self.event_manager:
                self._record_aging_event(character, result, year, season)

        return result

    def _calculate_characteristic_changes(self, crisis: AgingCrisis) -> Dict[Characteristic, int]:
        """Calculate characteristic changes based on crisis severity."""
        changes = {}
        num_characteristics = {AgingCrisis.MINOR: 1, AgingCrisis.MAJOR: 2, AgingCrisis.CRITICAL: 3}.get(crisis, 0)

        available_chars = list(Characteristic)
        for _ in range(num_characteristics):
            char = random.choice(available_chars)
            changes[char] = -1  # Always decrease by 1 for simplicity
            available_chars.remove(char)  # Don't affect the same characteristic twice

        return changes

    def _calculate_age_change(self, crisis: AgingCrisis) -> int:
        """Calculate apparent age change based on crisis severity."""
        age_changes = {AgingCrisis.MINOR: (1, 2), AgingCrisis.MAJOR: (2, 5), AgingCrisis.CRITICAL: (5, 10)}

        if crisis in age_changes:
            min_change, max_change = age_changes[crisis]
            return random.randint(min_change, max_change)
        return 0

    def _create_aging_description(
        self, crisis: AgingCrisis, changes: Dict[Characteristic, int], result: AgingResult
    ) -> str:
        """Create a detailed description of aging effects."""
        parts = [f"Age crisis: {crisis.value}."]

        for char, change in changes.items():
            parts.append(f"Lost {abs(change)} point(s) in {char.value}")

        if result.apparent_age_change:
            parts.append(f"Apparent age increased by {result.apparent_age_change} years")

        if result.warping_gained:
            parts.append(f"Gained {result.warping_gained} Warping Point(s)")

        if result.died:
            parts.append("Character has died from aging crisis")

        return " ".join(parts)

    def _record_aging_event(self, character: Character, result: AgingResult, year: int, season: str) -> None:
        """Record aging event."""
        event = Event(
            type=EventType.AGING,
            year=year,
            season=season,
            description=result.description,
            details={
                "character": character.name,
                "crisis_type": result.crisis.value,
                "characteristic_changes": {k.name: v for k, v in result.characteristic_changes.items()},
                "apparent_age_change": result.apparent_age_change,
                "warping_gained": result.warping_gained,
                "warping_source": result.warping_source.value if result.warping_source else None,
                "died": result.died,
            },
        )
        self.event_manager.add_event(event)

    def generate_weather(self, season: Season) -> WeatherEffect:
        """Generate weather for a season."""
        # Base weather probabilities per season
        probabilities = {
            Season.SPRING: {"MILD": 0.5, "HARSH": 0.3, "SEVERE": 0.15, "EXTRAORDINARY": 0.05},
            Season.SUMMER: {"MILD": 0.6, "HARSH": 0.25, "SEVERE": 0.1, "EXTRAORDINARY": 0.05},
            Season.AUTUMN: {"MILD": 0.4, "HARSH": 0.4, "SEVERE": 0.15, "EXTRAORDINARY": 0.05},
            Season.WINTER: {"MILD": 0.3, "HARSH": 0.4, "SEVERE": 0.25, "EXTRAORDINARY": 0.05},
        }

        # Roll for weather type
        roll = random.random()
        cumulative = 0
        weather_type = WeatherType.MILD

        for type_name, prob in probabilities[season].items():
            cumulative += prob
            if roll <= cumulative:
                weather_type = WeatherType(type_name)
                break

        # Generate effects based on weather type
        effects = {
            WeatherType.MILD: {"description": "Normal seasonal weather", "modifiers": {}},
            WeatherType.HARSH: {
                "description": f"Harsh {season.value.lower()} conditions",
                "modifiers": {"travel": -1, "outdoor_activities": -2},
            },
            WeatherType.SEVERE: {
                "description": f"Severe {season.value.lower()} weather",
                "modifiers": {"travel": -3, "outdoor_activities": -4, "living_conditions": -1},
            },
            WeatherType.EXTRAORDINARY: {
                "description": f"Extraordinary {season.value.lower()} phenomena",
                "modifiers": {"travel": -5, "outdoor_activities": -6, "living_conditions": -2, "magical_activities": 2},
            },
        }[weather_type]

        weather = WeatherEffect(type=weather_type, description=effects["description"], modifiers=effects["modifiers"])

        self.weather_effects[season] = weather
        return weather

    def generate_event(self, covenant: Covenant) -> Optional[SeasonalEvent]:
        """Generate a random seasonal event."""
        # Chance for an event to occur
        if random.random() > 0.3:  # 30% chance of event
            return None

        # Event type probabilities based on covenant
        probabilities = {
            EventType.MUNDANE: 0.4,
            EventType.MAGICAL: 0.2 + (covenant.aura * 0.05),
            EventType.POLITICAL: 0.15,
            EventType.RELIGIOUS: 0.1,
            EventType.FAERIE: 0.1,
            EventType.INFERNAL: 0.05,
        }

        # Normalize probabilities
        total = sum(probabilities.values())
        probabilities = {k: v / total for k, v in probabilities.items()}

        # Select event type
        event_type = random.choices(list(probabilities.keys()), weights=list(probabilities.values()))[0]

        # Generate event details based on type
        events_by_type = {
            EventType.MUNDANE: [
                ("Local Festival", "A nearby village holds a festival", 1),
                ("Trade Caravan", "Merchants arrive with exotic goods", 2),
                ("Bandit Activity", "Bandits threaten local roads", 3),
                ("Disease Outbreak", "A disease spreads in the area", 4),
                ("Natural Disaster", "A natural disaster strikes", 5),
            ],
            EventType.MAGICAL: [
                ("Vis Surge", "A temporary increase in local vis", 1),
                ("Magic Disturbance", "Strange magical effects occur", 2),
                ("Magical Beast", "A magical creature appears", 3),
                ("Wizard's War", "Conflict with another covenant", 4),
                ("Twilight Event", "Major magical phenomenon", 5),
            ],
            # ... similar entries for other event types ...
        }

        event_options = events_by_type[event_type]
        title, description, severity = random.choice(event_options)

        event = SeasonalEvent(
            type=event_type,
            title=title,
            description=description,
            severity=severity,
            effects=self._generate_event_effects(event_type, severity),
        )

        self.events.append(event)
        return event

    def _generate_event_effects(self, event_type: EventType, severity: int) -> Dict:
        """Generate specific effects for an event."""
        effects = {}

        if event_type == EventType.MUNDANE:
            effects["resources"] = -severity if severity > 3 else 0
            effects["reputation"] = random.randint(-1, 1) * severity
        elif event_type == EventType.MAGICAL:
            effects["aura_modifier"] = severity - 3
            effects["vis_bonus"] = severity if random.random() > 0.5 else 0
        # ... handle other event types ...

        return effects

    def apply_seasonal_effects(self, covenant: Covenant, characters: List[Character], season: Season) -> Dict[str, any]:
        """Apply all seasonal effects to covenant and characters."""
        results = {
            "weather": self.generate_weather(season),
            "event": self.generate_event(covenant),
            "aging": {},
            "covenant_effects": {},
        }

        # Apply weather effects
        weather = results["weather"]
        if weather.type != WeatherType.MILD:
            covenant.apply_modifiers(weather.modifiers)

        # Apply event effects
        event = results["event"]
        if event:
            covenant.apply_event(event)

        # Process aging for characters
        for character in characters:
            # Age check once per year in winter
            if season == Season.WINTER:
                aging_result = self.process_aging(character)
                results["aging"][character.name] = aging_result

                if aging_result.crisis != AgingCrisis.NONE:
                    character.apply_aging_crisis(aging_result)

        return results
