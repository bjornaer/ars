from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .character import Character
from .events import EventRecorder, EventType
from .laboratory import Laboratory
from ars.core.types import Season
from .spells import Spell
from .core.types import Form, Technique


class ResearchType(Enum):
    """Types of magical research."""

    SPELL_CREATION = "Spell Creation"
    SPELL_MODIFICATION = "Spell Modification"
    SPELL_MASTERY = "Spell Mastery"
    SPELL_INTEGRATION = "Spell Integration"
    SPELL_EXPERIMENTATION = "Spell Experimentation"


class ResearchOutcome(Enum):
    """Possible outcomes of magical research."""

    SUCCESS = "Success"
    PARTIAL_SUCCESS = "Partial Success"
    FAILURE = "Failure"
    CATASTROPHIC_FAILURE = "Catastrophic Failure"
    BREAKTHROUGH = "Breakthrough"


@dataclass
class ResearchModifier:
    """Modifiers affecting spell research."""

    name: str
    bonus: int
    description: str
    applicable_types: List[ResearchType] = field(default_factory=list)


@dataclass
class ResearchProject:
    """A magical research project."""

    researcher: str
    research_type: ResearchType
    target_spell: Optional[Spell] = None
    target_level: Optional[int] = None
    technique: Optional[Technique] = None
    form: Optional[Form] = None

    # Research progress
    seasons_invested: int = 0
    research_points: int = 0
    breakthrough_points: int = 0

    # Project details
    notes: List[str] = field(default_factory=list)
    modifiers: List[ResearchModifier] = field(default_factory=list)

    def calculate_research_total(self, character: Character, laboratory: Laboratory) -> int:
        """Calculate total research points for a season."""
        # Base total from relevant Art scores
        if self.technique and self.form:
            art_score = character.techniques.get(self.technique.value, 0) + character.forms.get(self.form.value, 0)
        elif self.target_spell:
            art_score = character.techniques.get(self.target_spell.technique, 0) + character.forms.get(
                self.target_spell.form, 0
            )
        else:
            art_score = 0

        # Add laboratory bonus
        lab_bonus = laboratory.calculate_total_bonus(
            self.technique or Technique(self.target_spell.technique), self.form or Form(self.target_spell.form)
        )

        # Add research modifiers
        modifier_bonus = sum(mod.bonus for mod in self.modifiers)

        return art_score + lab_bonus + modifier_bonus

    def add_season_progress(self, points: int) -> None:
        """Add research progress from a season's work."""
        self.seasons_invested += 1
        self.research_points += points

    def add_breakthrough_points(self, points: int) -> None:
        """Add breakthrough points from exceptional research."""
        self.breakthrough_points += points

    def add_note(self, note: str) -> None:
        """Add a research note."""
        self.notes.append(note)

    def save(self, directory: Path = Path("ars/data/research")) -> None:
        """Save research project to file."""
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / f"{self.researcher.lower().replace(' ', '_')}_research.yml"

        data = {
            "researcher": self.researcher,
            "research_type": self.research_type.value,
            "target_spell": self.target_spell.name if self.target_spell else None,
            "target_level": self.target_level,
            "technique": self.technique.value if self.technique else None,
            "form": self.form.value if self.form else None,
            "seasons_invested": self.seasons_invested,
            "research_points": self.research_points,
            "breakthrough_points": self.breakthrough_points,
            "notes": self.notes,
            "modifiers": [
                {
                    "name": m.name,
                    "bonus": m.bonus,
                    "description": m.description,
                    "applicable_types": [t.value for t in m.applicable_types],
                }
                for m in self.modifiers
            ],
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load(cls, researcher: str, directory: Path = Path("ars/data/research")) -> "ResearchProject":
        """Load research project from file."""
        filepath = directory / f"{researcher.lower().replace(' ', '_')}_research.yml"

        with filepath.open("r") as f:
            data = yaml.safe_load(f)

            # Convert enums
            data["research_type"] = ResearchType(data["research_type"])
            if data["technique"]:
                data["technique"] = Technique(data["technique"])
            if data["form"]:
                data["form"] = Form(data["form"])

            # Load target spell if exists
            if data["target_spell"]:
                data["target_spell"] = Spell.load(data["target_spell"])

            # Convert modifiers
            modifiers = []
            for m in data["modifiers"]:
                modifiers.append(
                    ResearchModifier(
                        name=m["name"],
                        bonus=m["bonus"],
                        description=m["description"],
                        applicable_types=[ResearchType(t) for t in m["applicable_types"]],
                    )
                )
            data["modifiers"] = modifiers

            return cls(**data)

    def apply_vis_effects(self, effects: Dict[str, int]) -> None:
        """Apply vis effects to research project."""
        for effect, value in effects.items():
            if effect.endswith("_bonus"):
                form = effect.replace("_bonus", "")
                if hasattr(self, "research_bonuses"):
                    self.research_bonuses[form] = value


@dataclass
class ResearchResult:
    """Result of a research activity."""

    points_gained: int = 0
    breakthrough: bool = False
    warping_points: int = 0
    insight_gained: Optional[str] = None
    complications: List[str] = field(default_factory=list)


class SpellResearchManager(EventRecorder):
    """Manages magical research activities."""

    def __init__(self, event_manager=None):
        super().__init__(event_manager)

    def conduct_research(
        self, project: "ResearchProject", character: "Character", laboratory: "Laboratory", year: int, season: Season
    ) -> ResearchResult:
        """Conduct magical research."""
        # Calculate base research points
        art_score = min(character.techniques[project.technique], character.forms[project.form])
        lab_total = laboratory.calculate_lab_total(project.technique, project.form)

        # Calculate research points
        points = (art_score + lab_total) // 10

        # Check for breakthroughs
        breakthrough = self._check_breakthrough(points, project)

        # Calculate warping
        warping = self._calculate_warping(laboratory.magical_aura)

        result = ResearchResult(points_gained=points, breakthrough=breakthrough, warping_points=warping)

        # Record the research event
        self.record_event(
            type=EventType.RESEARCH,
            description=f"Research conducted by {character.name} on {project.name}",
            details={
                "character": character.name,
                "project_name": project.name,
                "research_type": project.research_type.value,
                "points_gained": points,
                "breakthrough": breakthrough,
                "warping_points": warping,
                "laboratory_conditions": {"aura": laboratory.magical_aura, "lab_total": lab_total},
            },
            year=year,
            season=season,
        )

        return result

    def _check_breakthrough(self, points: int, project: "ResearchProject") -> bool:
        """Check if a breakthrough occurs."""
        if points > project.target_level // 2:
            return True
        return False

    def _calculate_warping(self, aura: int) -> int:
        """Calculate warping points from research."""
        return max(0, (aura - 5) // 2)  # Warping from high aura exposure


@dataclass
class MasteryEffect:
    """Represents a spell mastery special ability."""

    name: str
    description: str
    level_required: int
    effect: Dict[str, any]


class SpellMasteryEffects:
    """Registry of available mastery effects."""

    EFFECTS = {
        "fast_cast": MasteryEffect(
            name="Fast Cast",
            description="Cast spell as a fast action",
            level_required=1,
            effect={"initiative_bonus": 3},
        ),
        "multiple_casting": MasteryEffect(
            name="Multiple Casting",
            description="Cast spell multiple times per round",
            level_required=2,
            effect={"max_casts": 2},
        ),
        "quiet_casting": MasteryEffect(
            name="Quiet Casting", description="Cast without voice", level_required=2, effect={"silent": True}
        ),
        "penetration": MasteryEffect(
            name="Penetration",
            description="Improved magic resistance penetration",
            level_required=1,
            effect={"penetration_bonus": 3},
        ),
    }
