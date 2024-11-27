from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ars.character import Character
from ars.covenant import Covenant
from ars.laboratory import Laboratory
from ars.spell_research import ResearchProject
from ars.types import Form
from ars.vis_aura import AuraManager, AuraProperties, AuraType, VisManager


class IntegratedVisAuraManager:
    """Manages vis and aura interactions with other systems."""

    def __init__(self, saga_name: str):
        self.saga_name = saga_name
        self.aura_manager = AuraManager()
        self.vis_manager = VisManager()

    def integrate_with_covenant(self, covenant: Covenant, season: Optional[str] = None) -> None:
        """Integrate aura and vis systems with covenant."""
        # Register covenant's aura
        covenant_aura = AuraProperties(
            type=AuraType.MAGIC,
            strength=covenant.aura,
            properties=covenant.aura_properties,
            modifiers=covenant.aura_modifiers,
        )
        self.aura_manager.register_aura(covenant.name, covenant_aura)

        # Register covenant's vis sources
        for source in covenant.vis_sources:
            self.vis_manager.register_source(f"{covenant.name}_{source.location}", source)

        # Update covenant's vis stocks
        covenant.vis_stocks = self.vis_manager.stocks

        # Apply seasonal aura effects
        if season:
            effects = self.aura_manager.calculate_aura_effects(covenant.name, "covenant_activities", season)
            covenant.apply_aura_effects(effects)

    def integrate_with_laboratory(self, laboratory: Laboratory, covenant: Optional[Covenant] = None) -> None:
        """Integrate aura effects with laboratory."""
        if covenant:
            aura = self.aura_manager.get_aura(covenant.name)
            if aura:
                laboratory.magical_aura = aura.strength

                # Apply aura effects to lab
                effects = self.aura_manager.calculate_aura_effects(covenant.name, "laboratory_activities")
                for activity, modifier in effects.items():
                    if activity in laboratory.activity_modifiers:
                        laboratory.activity_modifiers[activity] += modifier
                    else:
                        laboratory.activity_modifiers[activity] = modifier

    def integrate_with_research(
        self, project: ResearchProject, laboratory: Laboratory, covenant: Covenant, season: str
    ) -> Dict[str, int]:
        """Calculate vis and aura effects for research."""
        effects = {}

        # Get aura effects
        aura_effects = self.aura_manager.calculate_aura_effects(covenant.name, "magical_research", season)
        effects.update(aura_effects)

        # Calculate vis requirements
        vis_required = self._calculate_research_vis_requirements(project)

        # Check if sufficient vis is available
        vis_available = all(self.vis_manager.stocks.get(form, 0) >= amount for form, amount in vis_required.items())

        if vis_available:
            # Use vis and apply bonuses
            for form, amount in vis_required.items():
                if self.vis_manager.use_vis(form, amount):
                    effects[f"{form.value}_bonus"] = amount

        return effects

    def _calculate_research_vis_requirements(self, project: ResearchProject) -> Dict[Form, int]:
        """Calculate vis requirements for research project."""
        requirements = {}

        if project.technique:
            requirements[project.technique] = max(1, project.target_level // 5)
        if project.form:
            requirements[project.form] = max(1, project.target_level // 10)

        return requirements

    def process_vis_extraction(
        self, character: Character, laboratory: Laboratory, covenant: Covenant, season: str, year: int
    ) -> List[Tuple[Form, int]]:
        """Process vis extraction activities."""
        results = []

        # Get aura effects for vis extraction
        effects = self.aura_manager.calculate_aura_effects(covenant.name, "vis_extraction", season)

        # Calculate laboratory bonus
        lab_bonus = laboratory.calculate_extraction_bonus()

        # Process each available source
        for source_name, source in self.vis_manager.sources.items():
            if source.location == laboratory.location:
                form, amount = self.vis_manager.collect_vis(
                    source_name, year, season, effects.get("vis_extraction", 0) + lab_bonus
                )
                if amount > 0:
                    results.append((form, amount))

        return results

    def save_state(self, directory: Path = Path("ars/data")) -> None:
        """Save current state of vis and aura systems."""
        vis_path = directory / f"{self.saga_name}_vis.yml"
        self.vis_manager.save(vis_path)

    @classmethod
    def load_state(cls, saga_name: str, directory: Path = Path("ars/data")) -> "IntegratedVisAuraManager":
        """Load vis and aura state for a saga."""
        manager = cls(saga_name)

        try:
            vis_path = directory / f"{saga_name}_vis.yml"
            manager.vis_manager = VisManager.load(vis_path)
        except FileNotFoundError:
            pass  # New saga

        return manager


# Update existing classes to work with the integrated manager


class Laboratory:
    def calculate_extraction_bonus(self) -> int:
        """Calculate laboratory's bonus to vis extraction."""
        bonus = 0
        if hasattr(self, "activity_modifiers"):
            bonus += self.activity_modifiers.get("vis_extraction", 0)
        if hasattr(self, "magical_aura"):
            bonus += self.magical_aura // 2
        return bonus


class Covenant:
    def apply_aura_effects(self, effects: Dict[str, int]) -> None:
        """Apply aura effects to covenant."""
        for activity, modifier in effects.items():
            if activity == "magical_activities":
                self.aura = max(0, self.aura + modifier)
            elif activity == "vis_extraction":
                for source in self.vis_sources:
                    source.amount = max(1, source.amount + modifier)


class ResearchProject:
    def apply_vis_effects(self, effects: Dict[str, int]) -> None:
        """Apply vis effects to research project."""
        for effect, value in effects.items():
            if effect.endswith("_bonus"):
                form = effect.replace("_bonus", "")
                if hasattr(self, "research_bonuses"):
                    self.research_bonuses[form] = value
