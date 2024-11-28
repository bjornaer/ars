import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from ars.character import Character
from ars.events import EventType, GameEvent
from ars.core.types import AbilityType, Characteristic


class AgingCrisisType(Enum):
    """Types of aging crises."""

    MINOR = auto()
    MAJOR = auto()
    FATAL = auto()


class WarpingSource(Enum):
    """Sources of warping points."""

    MAGICAL_AURA = auto()
    SPELL_BOTCH = auto()
    TWILIGHT = auto()
    RITUAL = auto()
    ENCHANTED_ITEM = auto()
    VIS = auto()


@dataclass
class AgingResult:
    """Result of an aging roll."""

    crisis_type: Optional[AgingCrisisType] = None
    characteristic_changes: Dict[Characteristic, int] = field(default_factory=dict)
    description: str = ""
    apparent_age_change: int = 0
    died: bool = False


@dataclass
class WarpingResult:
    """Result of warping points accumulation."""

    points_gained: int = 0
    source: WarpingSource = None
    new_score: int = 0
    triggered_points: int = 0  # Points that triggered a new warping score
    effects: List[str] = field(default_factory=list)


class AgingManager:
    """Manages character aging and longevity rituals."""

    def __init__(self, event_manager=None):
        self.event_manager = event_manager

    def check_aging(self, character: Character, year: int, season: str) -> AgingResult:
        """Perform aging check for character."""
        # Base aging roll
        roll = random.randint(1, 10) - 3  # -3 is the standard living conditions modifier

        # Apply longevity ritual if present
        ritual_bonus = self._get_longevity_bonus(character)
        if ritual_bonus:
            roll -= ritual_bonus

        # Apply lifestyle modifiers
        roll += self._get_lifestyle_modifier(character)

        result = AgingResult()

        # Process aging result
        if roll <= 0:
            # No aging this year
            result.description = "No significant aging effects"
        elif roll <= 3:
            result = self._handle_minor_aging(character)
        elif roll <= 6:
            result = self._handle_major_aging(character)
        else:
            result = self._handle_crisis_aging(character)

        # Record event
        if self.event_manager:
            self._record_aging_event(character, result, year, season)

        return result

    def _get_longevity_bonus(self, character: Character) -> int:
        """Calculate longevity ritual bonus."""
        # TODO: Implement actual longevity ritual mechanics
        return character.abilities.get(AbilityType.ARCANE, {}).get("Longevity Ritual", 0)

    def _get_lifestyle_modifier(self, character: Character) -> int:
        """Calculate lifestyle modifier for aging."""
        # Base on covenant quality and personal wealth
        return 0  # Default modifier

    def _handle_minor_aging(self, character: Character) -> AgingResult:
        """Handle minor aging effects."""
        result = AgingResult(crisis_type=AgingCrisisType.MINOR)

        # Randomly decrease one characteristic
        char = random.choice(list(Characteristic))
        character.characteristics[char] -= 1
        result.characteristic_changes[char] = -1
        result.description = f"Minor aging: {char.value} decreased by 1"

        return result

    def _handle_major_aging(self, character: Character) -> AgingResult:
        """Handle major aging effects."""
        result = AgingResult(crisis_type=AgingCrisisType.MAJOR)

        # Decrease multiple characteristics
        for _ in range(2):
            char = random.choice(list(Characteristic))
            character.characteristics[char] -= 1
            result.characteristic_changes[char] = result.characteristic_changes.get(char, 0) - 1

        result.apparent_age_change = random.randint(2, 5)
        result.description = "Major aging: Multiple characteristics decreased"

        return result

    def _handle_crisis_aging(self, character: Character) -> AgingResult:
        """Handle crisis aging effects."""
        result = AgingResult(crisis_type=AgingCrisisType.FATAL)

        # Severe characteristic decreases
        for _ in range(3):
            char = random.choice(list(Characteristic))
            decrease = random.randint(1, 3)
            character.characteristics[char] -= decrease
            result.characteristic_changes[char] = result.characteristic_changes.get(char, 0) - decrease

        result.apparent_age_change = random.randint(5, 10)

        # Check for death
        if any(value <= -3 for value in character.characteristics.values()):
            result.died = True
            result.description = "Fatal aging crisis: Character has died"
        else:
            result.description = "Severe aging crisis: Multiple characteristics severely decreased"

        return result

    def _record_aging_event(self, character: Character, result: AgingResult, year: int, season: str) -> None:
        """Record aging event."""
        if self.event_manager:
            event = GameEvent(
                type=EventType.AGING,
                year=year,
                season=season,
                description=result.description,
                details={
                    "character": character.name,
                    "crisis_type": result.crisis_type.name if result.crisis_type else None,
                    "characteristic_changes": {k.name: v for k, v in result.characteristic_changes.items()},
                    "apparent_age_change": result.apparent_age_change,
                    "died": result.died,
                },
            )
            self.event_manager.add_event(event)


class WarpingManager:
    """Manages warping points and effects."""

    def __init__(self, event_manager=None):
        self.event_manager = event_manager

    def add_warping_points(
        self, character: Character, points: int, source: WarpingSource, year: int, season: str
    ) -> WarpingResult:
        """Add warping points to character."""
        result = WarpingResult(points_gained=points, source=source)

        # Add points
        old_score = character.warping_points // 5
        character.warping_points += points
        new_score = character.warping_points // 5

        result.new_score = new_score

        # Check if new warping score reached
        if new_score > old_score:
            result.triggered_points = character.warping_points - (old_score * 5)
            result.effects = self._apply_warping_effects(character, new_score)

        # Record event
        if self.event_manager:
            self._record_warping_event(character, result, year, season)

        return result

    def _apply_warping_effects(self, character: Character, score: int) -> List[str]:
        """Apply warping effects based on new score."""
        effects = []

        # Minor supernatural effects
        if score == 1:
            effect = self._generate_minor_warping_effect()
            effects.append(effect)

        # Major supernatural changes
        elif score == 2:
            effect = self._generate_major_warping_effect()
            effects.append(effect)

        # Powerful supernatural changes
        elif score >= 3:
            effect = self._generate_powerful_warping_effect()
            effects.append(effect)

        return effects

    def _generate_minor_warping_effect(self) -> str:
        """Generate a minor warping effect."""
        effects = [
            "Faint magical aura",
            "Slight physical oddity",
            "Minor behavioral change",
            "Unusual eye color",
            "Strange birthmark appears",
        ]
        return random.choice(effects)

    def _generate_major_warping_effect(self) -> str:
        """Generate a major warping effect."""
        effects = [
            "Visible magical aura",
            "Significant physical change",
            "Major personality shift",
            "Magical sensitivity",
            "Supernatural mark",
        ]
        return random.choice(effects)

    def _generate_powerful_warping_effect(self) -> str:
        """Generate a powerful warping effect."""
        effects = [
            "Permanent magical aura",
            "Dramatic physical transformation",
            "Supernatural ability manifests",
            "Constant magical effect",
            "Profound metaphysical change",
        ]
        return random.choice(effects)

    def _record_warping_event(self, character: Character, result: WarpingResult, year: int, season: str) -> None:
        """Record warping event."""
        if self.event_manager:
            event = GameEvent(
                type=EventType.WARPING,
                year=year,
                season=season,
                description=f"Warping points gained from {result.source.name}",
                details={
                    "character": character.name,
                    "points_gained": result.points_gained,
                    "source": result.source.name,
                    "new_score": result.new_score,
                    "triggered_points": result.triggered_points,
                    "effects": result.effects,
                },
            )
            self.event_manager.add_event(event)
