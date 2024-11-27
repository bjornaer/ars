import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .character import Character
from .covenant import Covenant
from .dice import DiceRoller
from .seasons import Season


class AgingCrisis(Enum):
    """Types of aging crises."""

    NONE = "None"
    MINOR = "Minor"
    MAJOR = "Major"
    CRITICAL = "Critical"


@dataclass
class AgingResult:
    """Result of an aging roll."""

    crisis: AgingCrisis
    characteristic_lost: Optional[str] = None
    points_lost: int = 0
    warping_gained: int = 0
    description: str = ""


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


class EventType(Enum):
    """Types of seasonal events."""

    MUNDANE = "Mundane"
    MAGICAL = "Magical"
    POLITICAL = "Political"
    RELIGIOUS = "Religious"
    FAERIE = "Faerie"
    INFERNAL = "Infernal"


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

    def __init__(self):
        self.weather_effects: Dict[Season, WeatherEffect] = {}
        self.events: List[SeasonalEvent] = []

    def process_aging(self, character: Character) -> AgingResult:
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
            # Determine characteristic loss
            characteristics = [
                "Strength",
                "Stamina",
                "Dexterity",
                "Quickness",
                "Intelligence",
                "Perception",
                "Presence",
                "Communication",
            ]
            result.characteristic_lost = random.choice(characteristics)

            # Calculate points lost
            result.points_lost = {AgingCrisis.MINOR: 1, AgingCrisis.MAJOR: 2, AgingCrisis.CRITICAL: 3}.get(crisis, 0)

            # Apply warping points
            result.warping_gained = result.points_lost

            # Create description
            result.description = (
                f"Age crisis: {crisis.value}. "
                f"Lost {result.points_lost} point(s) in {result.characteristic_lost}. "
                f"Gained {result.warping_gained} Warping Point(s)."
            )

        return result

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
