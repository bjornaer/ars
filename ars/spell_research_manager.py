import random
from dataclasses import dataclass
from typing import List, Optional

from .character import Character
from .dice import DiceRoller
from .laboratory import Laboratory
from .spell_research import ResearchModifier, ResearchOutcome, ResearchProject, ResearchType
from .spells import Spell, SpellParameters


@dataclass
class ResearchResult:
    """Result of a research season."""

    outcome: ResearchOutcome
    points_gained: int
    breakthrough_points: int = 0
    notes: List[str] = None
    warping_points: int = 0
    new_spell: Optional[Spell] = None


class SpellResearchManager:
    """Manages spell research activities and outcomes."""

    # Research point requirements
    POINTS_NEEDED = {
        ResearchType.SPELL_CREATION: lambda level: level * 2,
        ResearchType.SPELL_MODIFICATION: lambda level: level * 3,
        ResearchType.SPELL_MASTERY: lambda level: level,
        ResearchType.SPELL_INTEGRATION: lambda level: level * 4,
        ResearchType.SPELL_EXPERIMENTATION: lambda level: level * 2,
    }

    # Breakthrough thresholds
    BREAKTHROUGH_THRESHOLD = 30

    @staticmethod
    def create_research_project(
        researcher: Character,
        research_type: ResearchType,
        target_spell: Optional[Spell] = None,
        target_level: Optional[int] = None,
        technique: Optional[str] = None,
        form: Optional[str] = None,
    ) -> ResearchProject:
        """Create a new research project."""
        return ResearchProject(
            researcher=researcher.name,
            research_type=research_type,
            target_spell=target_spell,
            target_level=target_level,
            technique=technique,
            form=form,
        )

    @classmethod
    def conduct_research(cls, project: ResearchProject, character: Character, laboratory: Laboratory) -> ResearchResult:
        """Conduct one season of research."""
        # Calculate base research points
        base_points = project.calculate_research_total(character, laboratory)

        # Roll for research outcome
        stress_roll = DiceRoller.stress_die()
        total_points = base_points + stress_roll.total

        # Check for botch
        if stress_roll.botch:
            return cls._handle_botch(project)

        # Check for breakthrough
        breakthrough_roll = DiceRoller.simple_die()
        breakthrough_points = 0
        if breakthrough_roll == 0 and total_points > base_points:
            breakthrough_points = total_points // 5

        # Determine outcome
        outcome = cls._determine_outcome(project, total_points, breakthrough_points)

        # Handle special cases
        if project.research_type == ResearchType.SPELL_EXPERIMENTATION:
            return cls._handle_experimentation(project, total_points, breakthrough_points)

        # Add progress to project
        project.add_season_progress(total_points)
        if breakthrough_points:
            project.add_breakthrough_points(breakthrough_points)

        # Check for completion
        new_spell = None
        if cls._is_project_complete(project):
            new_spell = cls._complete_project(project, character)

        return ResearchResult(
            outcome=outcome,
            points_gained=total_points,
            breakthrough_points=breakthrough_points,
            notes=[f"Research total: {total_points} (Base: {base_points}, Roll: {stress_roll.total})"],
            new_spell=new_spell,
        )

    @classmethod
    def _determine_outcome(cls, project: ResearchProject, points: int, breakthrough_points: int) -> ResearchOutcome:
        """Determine the outcome of research."""
        if breakthrough_points > 0:
            return ResearchOutcome.BREAKTHROUGH

        target = cls.POINTS_NEEDED[project.research_type](project.target_level or project.target_spell.level)

        if points >= target * 1.5:
            return ResearchOutcome.SUCCESS
        elif points >= target:
            return ResearchOutcome.PARTIAL_SUCCESS
        else:
            return ResearchOutcome.FAILURE

    @classmethod
    def _handle_botch(cls, project: ResearchProject) -> ResearchResult:
        """Handle a botched research roll."""
        warping = random.randint(1, 3)
        return ResearchResult(
            outcome=ResearchOutcome.CATASTROPHIC_FAILURE,
            points_gained=0,
            notes=["Research botched! Laboratory accident occurred."],
            warping_points=warping,
        )

    @classmethod
    def _handle_experimentation(cls, project: ResearchProject, points: int, breakthrough_points: int) -> ResearchResult:
        """Handle experimental research outcomes."""
        # Implementation of experimental magic rules
        # This could be expanded significantly
        return ResearchResult(
            outcome=ResearchOutcome.SUCCESS if points > 0 else ResearchOutcome.FAILURE,
            points_gained=points,
            breakthrough_points=breakthrough_points,
            notes=["Experimental research conducted."],
        )

    @classmethod
    def _is_project_complete(cls, project: ResearchProject) -> bool:
        """Check if research project is complete."""
        target_points = cls.POINTS_NEEDED[project.research_type](project.target_level or project.target_spell.level)
        return project.research_points >= target_points

    @classmethod
    def _complete_project(cls, project: ResearchProject, character: Character) -> Optional[Spell]:
        """Complete a research project."""
        if project.research_type == ResearchType.SPELL_CREATION:
            # Create new spell
            params = SpellParameters(technique=project.technique, form=project.form, level=project.target_level)
            return Spell.create(params)
        elif project.research_type == ResearchType.SPELL_MODIFICATION:
            # Modify existing spell
            return project.target_spell.copy_with_modifications()

        return None

    @staticmethod
    def get_available_modifiers(character: Character, research_type: ResearchType) -> List[ResearchModifier]:
        """Get available research modifiers for a character."""
        # This could be expanded to include various sources of modifiers
        modifiers = []

        # Add virtue-based modifiers
        if "Inventive Genius" in character.virtues:
            modifiers.append(
                ResearchModifier(
                    name="Inventive Genius",
                    bonus=3,
                    description="Bonus from Inventive Genius virtue",
                    applicable_types=[ResearchType.SPELL_CREATION],
                )
            )

        return modifiers
