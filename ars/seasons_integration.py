from typing import Dict

from ars.character import Character
from ars.laboratory import Laboratory
from ars.seasons import ActivityType, SeasonalActivity, SeasonManager
from ars.spell_research import ResearchProject


class IntegratedSeasonManager(SeasonManager):
    """Extended season manager with integrated system handling."""

    def __init__(self, saga_name: str):
        super().__init__(saga_name)
        self.laboratories: Dict[str, Laboratory] = {}
        self.research_projects: Dict[str, ResearchProject] = {}

    def register_laboratory(self, laboratory: Laboratory) -> None:
        """Register a laboratory for seasonal activities."""
        self.laboratories[laboratory.owner] = laboratory

    def register_research_project(self, project: ResearchProject) -> None:
        """Register a research project for tracking."""
        self.research_projects[project.researcher] = project

    def _execute_activity(self, activity: SeasonalActivity, character: Character) -> Dict:
        """Enhanced activity execution with integrated systems."""
        # Get character's laboratory if needed
        laboratory = self.laboratories.get(character.name)

        if activity.type == ActivityType.RESEARCH:
            if character.name not in self.research_projects:
                return {"error": "No active research project"}
            project = self.research_projects[character.name]

            from .spell_research_manager import SpellResearchManager

            result = SpellResearchManager.conduct_research(project, character, laboratory)

            # Update project state
            self.research_projects[character.name] = project
            project.save()

            return {
                "outcome": result.outcome.value,
                "points": result.points_gained,
                "breakthrough": result.breakthrough_points,
            }

        elif activity.type == ActivityType.EXTRACT_VIS:
            if not laboratory:
                return {"error": "No laboratory available"}

            if not self.covenant:
                return {"error": "No covenant registered"}

            vis_gained = self.covenant.collect_vis(self.current_year.current_season.value)
            return {"vis_gained": vis_gained}

        elif activity.type == ActivityType.ENCHANT_ITEM:
            if not laboratory:
                return {"error": "No laboratory available"}

            # Handle item enchantment
            pass

        return super()._execute_activity(activity, character)

    def execute_season(self) -> Dict[str, Dict]:
        """Enhanced season execution with integrated systems."""
        results = super().execute_season()

        # Update laboratory maintenance
        for lab in self.laboratories.values():
            lab.save()

        # Update covenant
        if self.covenant:
            self.covenant.save()

        # Update character states
        for character in self.characters.values():
            character.save()

        return results
