from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .character import Character
from .covenant import Covenant
from .laboratory import Laboratory
from .spell_research import ResearchProject


class Season(Enum):
    """The four seasons of the year."""

    SPRING = "Spring"
    SUMMER = "Summer"
    AUTUMN = "Autumn"
    WINTER = "Winter"

    @classmethod
    def next_season(cls, current: "Season") -> "Season":
        """Get the next season in sequence."""
        seasons = list(cls)
        current_idx = seasons.index(current)
        return seasons[(current_idx + 1) % 4]


class ActivityType(Enum):
    """Types of seasonal activities."""

    STUDY = "Study"
    RESEARCH = "Research"
    TEACH = "Teach"
    LEARN = "Learn"
    PRACTICE = "Practice"
    ADVENTURE = "Adventure"
    COVENANT_SERVICE = "Covenant Service"
    WRITE = "Write"
    EXTRACT_VIS = "Extract Vis"
    ENCHANT_ITEM = "Enchant Item"
    LONGEVITY_RITUAL = "Longevity Ritual"


@dataclass
class SeasonalActivity:
    """An activity performed during a season."""

    type: ActivityType
    character: str
    season: Season
    year: int
    details: Dict = field(default_factory=dict)
    results: Dict = field(default_factory=dict)
    completed: bool = False


@dataclass
class GameYear:
    """Represents a year in the saga."""

    year: int
    current_season: Season = Season.SPRING
    activities: Dict[str, List[SeasonalActivity]] = field(default_factory=dict)
    covenant_events: List[str] = field(default_factory=list)

    def advance_season(self) -> Season:
        """Advance to the next season."""
        self.current_season = Season.next_season(self.current_season)
        if self.current_season == Season.SPRING:
            self.year += 1
        return self.current_season


class SeasonManager:
    """Manages seasonal activities and progression."""

    def __init__(self, saga_name: str):
        self.saga_name = saga_name
        self.current_year = GameYear(year=1220)  # Default start year
        self.characters: Dict[str, Character] = {}
        self.covenant: Optional[Covenant] = None

    def load_saga(self) -> None:
        """Load saga data."""
        try:
            filepath = Path(f"ars/data/sagas/{self.saga_name.lower()}.yml")
            with filepath.open("r") as f:
                data = yaml.safe_load(f)
                self.current_year = GameYear(year=data["year"], current_season=Season(data["current_season"]))
                # Load activities
                for char, activities in data.get("activities", {}).items():
                    self.current_year.activities[char] = [SeasonalActivity(**act) for act in activities]
        except FileNotFoundError:
            # New saga
            pass

    def save_saga(self) -> None:
        """Save saga data."""
        filepath = Path(f"ars/data/sagas/{self.saga_name.lower()}.yml")
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "year": self.current_year.year,
            "current_season": self.current_year.current_season.value,
            "activities": {
                char: [
                    {
                        "type": act.type.value,
                        "character": act.character,
                        "season": act.season.value,
                        "year": act.year,
                        "details": act.details,
                        "results": act.results,
                        "completed": act.completed,
                    }
                    for act in activities
                ]
                for char, activities in self.current_year.activities.items()
            },
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    def register_character(self, character: Character) -> None:
        """Register a character for seasonal activities."""
        self.characters[character.name] = character
        if character.name not in self.current_year.activities:
            self.current_year.activities[character.name] = []

    def set_covenant(self, covenant: Covenant) -> None:
        """Set the covenant for the saga."""
        self.covenant = covenant

    def schedule_activity(self, character: str, activity_type: ActivityType, details: Dict = None) -> SeasonalActivity:
        """Schedule an activity for the current season."""
        if character not in self.characters:
            raise ValueError(f"Character {character} not registered")

        activity = SeasonalActivity(
            type=activity_type,
            character=character,
            season=self.current_year.current_season,
            year=self.current_year.year,
            details=details or {},
        )

        self.current_year.activities[character].append(activity)
        return activity

    def execute_season(self) -> Dict[str, Dict]:
        """Execute all scheduled activities for the current season."""
        results = {}

        # Execute character activities
        for character_name, activities in self.current_year.activities.items():
            character = self.characters[character_name]
            current_activities = [
                act
                for act in activities
                if act.season == self.current_year.current_season
                and act.year == self.current_year.year
                and not act.completed
            ]

            for activity in current_activities:
                result = self._execute_activity(activity, character)
                activity.results = result
                activity.completed = True

                if character_name not in results:
                    results[character_name] = {}
                results[character_name][activity.type.value] = result

        # Execute covenant activities
        if self.covenant:
            self._execute_covenant_activities()

        # Advance to next season
        self.current_year.advance_season()

        return results

    def _execute_activity(self, activity: SeasonalActivity, character: Character) -> Dict:
        """Execute a single activity."""
        if activity.type == ActivityType.STUDY:
            return self._handle_study(activity, character)
        elif activity.type == ActivityType.RESEARCH:
            return self._handle_research(activity, character)
        elif activity.type == ActivityType.PRACTICE:
            return self._handle_practice(activity, character)
        # ... handle other activity types ...

        return {"status": "completed"}

    def _handle_study(self, activity: SeasonalActivity, character: Character) -> Dict:
        """Handle study activities."""
        source = activity.details.get("source")
        subject = activity.details.get("subject")

        if not all([source, subject]):
            return {"error": "Invalid study details"}

        # Calculate and apply experience
        experience = self._calculate_study_experience(source, subject)
        character.add_experience(subject, experience)

        return {"subject": subject, "experience": experience}

    def _handle_research(self, activity: SeasonalActivity, character: Character) -> Dict:
        """Handle research activities."""
        try:
            project = ResearchProject.load(character.name)
            laboratory = Laboratory.load(character.name)

            from .spell_research_manager import SpellResearchManager

            result = SpellResearchManager.conduct_research(project, character, laboratory)

            return {
                "outcome": result.outcome.value,
                "points": result.points_gained,
                "breakthrough": result.breakthrough_points,
            }
        except Exception as e:
            return {"error": str(e)}

    def _handle_practice(self, activity: SeasonalActivity, character: Character) -> Dict:
        """Handle practice activities."""
        ability = activity.details.get("ability")
        if not ability:
            return {"error": "No ability specified"}

        # Calculate and apply experience
        experience = 2  # Base practice experience
        character.add_experience(ability, experience)

        return {"ability": ability, "experience": experience}

    def _execute_covenant_activities(self) -> None:
        """Execute covenant-wide activities."""
        if not self.covenant:
            return

        # Handle seasonal vis collection
        if self.current_year.current_season in [Season.SPRING, Season.SUMMER]:
            self.covenant.collect_vis(self.current_year.current_season.value)

        # Handle covenant upkeep
        self.covenant.calculate_expenses()
        self.covenant.calculate_income()

        # Save covenant state
        self.covenant.save()
