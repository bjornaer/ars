from pathlib import Path
from typing import Dict, Optional

from ars.character import Character
from ars.covenant import Covenant
from ars.laboratory import Laboratory
from ars.magic_items import ItemCreationManager, ItemEffect, ItemType, MagicItem
from ars.seasons import Season
from ars.vis_aura import AuraManager, VisManager


class IntegratedItemCreationManager:
    """Manages magic item creation with integrated systems."""

    def __init__(self, saga_name: str):
        self.saga_name = saga_name
        self.item_manager = ItemCreationManager()
        self.vis_manager = VisManager()
        self.aura_manager = AuraManager()
        self.active_projects: Dict[str, Dict] = {}

    def start_enchantment_season(
        self,
        character: Character,
        laboratory: Laboratory,
        covenant: Covenant,
        item: MagicItem,
        effect: ItemEffect,
        season: Season,
    ) -> Dict[str, any]:
        """Start a seasonal enchantment activity."""
        try:
            # Apply laboratory conditions
            lab_conditions = self._calculate_lab_conditions(laboratory, covenant, season)

            # Apply character's enchantment abilities
            enchantment_bonus = self._calculate_enchantment_bonus(character)

            # Modify item and effect based on conditions
            item.aura_bonus = lab_conditions.get("aura_bonus", 0)
            effect.lab_total += lab_conditions.get("lab_bonus", 0) + enchantment_bonus

            # Start the project
            if self.item_manager.start_project(character, laboratory, item, effect):
                self.active_projects[character.name] = {
                    "item": item,
                    "effect": effect,
                    "conditions": lab_conditions,
                    "season_started": season,
                }

                return {
                    "status": "started",
                    "lab_total": effect.lab_total,
                    "seasons_required": effect.seasons_required,
                    "vis_required": effect.vis_required,
                }

            return {"error": "Could not start project"}

        except Exception as e:
            return {"error": str(e)}

    def _calculate_lab_conditions(self, laboratory: Laboratory, covenant: Covenant, season: Season) -> Dict[str, int]:
        """Calculate laboratory conditions for enchantment."""
        conditions = {}

        # Base laboratory bonus
        conditions["lab_bonus"] = laboratory.calculate_enchantment_bonus()

        # Aura effects
        if covenant:
            aura = self.aura_manager.get_aura(covenant.name)
            if aura:
                aura_effects = self.aura_manager.calculate_aura_effects(covenant.name, "enchantment", season.value)
                conditions["aura_bonus"] = aura_effects.get("magical_activities", 0)

        # Seasonal effects
        seasonal_modifier = {Season.SPRING: 1, Season.WINTER: -1}.get(  # Bonus to creation  # Penalty to creation
            season, 0
        )
        conditions["seasonal_modifier"] = seasonal_modifier

        return conditions

    def _calculate_enchantment_bonus(self, character: Character) -> int:
        """Calculate character's enchantment bonus."""
        bonus = 0

        # Magic Theory bonus
        if hasattr(character, "abilities"):
            bonus += character.abilities.get("Magic Theory", 0) // 2

        # Enchantment specialization
        if hasattr(character, "specializations"):
            bonus += character.specializations.get("Enchantment", 0)

        # Virtues and Flaws effects
        if hasattr(character, "virtues"):
            if "Enchanting Magic" in character.virtues:
                bonus += 3
            if "Magical Focus (Enchantment)" in character.virtues:
                bonus += 2

        return bonus

    def continue_enchantment_season(
        self, character: Character, laboratory: Laboratory, covenant: Optional[Covenant] = None
    ) -> Dict[str, any]:
        """Continue enchantment work for a season."""
        if character.name not in self.active_projects:
            return {"error": "No active enchantment project"}

        # project = self.active_projects[character.name]

        # Check for vis requirements
        result = self.item_manager.continue_project(character, laboratory, self.vis_manager)

        if result.get("status") == "completed":
            # Update character experience
            if hasattr(character, "add_experience"):
                character.add_experience("Magic Theory", 2)

            # Update laboratory specialization
            if hasattr(laboratory, "add_experience"):
                laboratory.add_experience("enchantment", 1)

            # Clean up project
            del self.active_projects[character.name]

            # Save all states
            self._save_states()

        return result

    def check_enchantment_requirements(
        self, character: Character, item: MagicItem, effect: ItemEffect
    ) -> Dict[str, any]:
        """Check if all requirements for enchantment are met."""
        requirements = {"met": True, "issues": []}

        # Check Magic Theory requirement
        magic_theory = getattr(character, "abilities", {}).get("Magic Theory", 0)
        if magic_theory < effect.level // 5:
            requirements["met"] = False
            requirements["issues"].append(f"Insufficient Magic Theory (need {effect.level // 5})")

        # Check Art requirements
        art_total = character.techniques.get(effect.technique.value, 0) + character.forms.get(effect.form.value, 0)
        if art_total < effect.level:
            requirements["met"] = False
            requirements["issues"].append(f"Insufficient Art scores (have {art_total}, need {effect.level})")

        # Check vis availability
        vis_reqs = self.item_manager._calculate_vis_requirements(effect, item.type)
        for form, amount in vis_reqs.items():
            if self.vis_manager.stocks.get(form, 0) < amount:
                requirements["met"] = False
                requirements["issues"].append(f"Insufficient {form.value} vis (need {amount})")

        return requirements

    def get_enchantment_progress(self, character_name: str) -> Optional[Dict[str, any]]:
        """Get current enchantment progress for a character."""
        if character_name not in self.active_projects:
            return None

        project = self.active_projects[character_name]
        return {
            "item_name": project["item"].name,
            "effect_name": project["effect"].name,
            "seasons_remaining": project["effect"].seasons_required,
            "season_started": project["season_started"].value,
            "conditions": project["conditions"],
        }

    def _save_states(self) -> None:
        """Save all related states."""
        base_path = Path(f"ars/data/sagas/{self.saga_name}")
        base_path.mkdir(parents=True, exist_ok=True)

        # Save enchantment projects
        self.item_manager.save_state(base_path / "enchantment_projects.yml")

        # Save vis stocks
        self.vis_manager.save(base_path / "vis_stocks.yml")

    @classmethod
    def load_state(cls, saga_name: str, base_path: Path = Path("ars/data/sagas")) -> "IntegratedItemCreationManager":
        """Load integrated manager state."""
        manager = cls(saga_name)
        saga_path = base_path / saga_name

        try:
            # Load enchantment projects
            manager.item_manager = ItemCreationManager.load_state(saga_path / "enchantment_projects.yml")

            # Load vis stocks
            manager.vis_manager = VisManager.load(saga_path / "vis_stocks.yml")

        except FileNotFoundError:
            # New saga
            pass

        return manager


# Update Laboratory class
class Laboratory:
    def calculate_enchantment_bonus(self) -> int:
        """Calculate laboratory's enchantment bonus."""
        bonus = 0

        # Base enchantment bonus
        if hasattr(self, "specializations"):
            bonus += self.specializations.get("enchantment", 0)

        # Equipment bonus
        if hasattr(self, "equipment"):
            bonus += sum(item.bonus for item in self.equipment if "enchantment" in item.specialties)

        # Size bonus
        if hasattr(self, "size"):
            bonus += max(0, self.size - 2)

        return bonus


# Update Character class
class Character:
    def can_enchant(self, item_type: ItemType) -> bool:
        """Check if character can create given type of magic item."""
        if not hasattr(self, "abilities"):
            return False

        magic_theory = self.abilities.get("Magic Theory", 0)

        requirements = {
            ItemType.CHARGED: 3,
            ItemType.INVESTED: 5,
            ItemType.LESSER: 8,
            ItemType.GREATER: 12,
            ItemType.TALISMAN: 15,
        }

        return magic_theory >= requirements[item_type]
