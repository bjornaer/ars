from pathlib import Path
from typing import Dict

from ars.adventure import AdventureManager, RewardType
from ars.character import Character
from ars.laboratory import Laboratory
from ars.magic_items import ItemCreationManager
from ars.seasons import ActivityType, SeasonalActivity
from ars.vis_aura import AuraManager, VisManager

from .covenant_economy import Book, CovenantEconomy, MagicalResource, MundaneResource, ResourceCategory


class IntegratedCovenantManager:
    """Manages covenant systems integration."""

    def __init__(self, covenant_name: str):
        self.covenant_name = covenant_name
        self.economy = CovenantEconomy(covenant_name)
        self.vis_manager = VisManager()
        self.aura_manager = AuraManager()
        self.item_manager = ItemCreationManager()
        self.adventure_manager = AdventureManager()

    def process_laboratory_integration(self, lab: Laboratory, season: str, year: int) -> Dict[str, any]:
        """Process laboratory effects on economy."""
        results = {"maintenance_cost": 0.0, "resources_used": [], "improvements": []}

        # Calculate maintenance costs
        base_cost = lab.size * 0.5
        specialization_cost = len(lab.specializations) * 0.2
        equipment_cost = sum(eq.maintenance_cost for eq in lab.equipment)

        total_cost = base_cost + specialization_cost + equipment_cost
        results["maintenance_cost"] = total_cost

        # Add as covenant expense
        self.economy.add_expense(f"Laboratory {lab.owner}", total_cost)

        # Check for resource requirements
        for equipment in lab.equipment:
            resource_name = f"Lab Equipment: {equipment.name}"
            if resource_name not in self.economy.resources:
                # Add as magical resource
                resource = MagicalResource(
                    name=resource_name,
                    category=ResourceCategory.MAGICAL,
                    quality=equipment.quality,
                    maintenance_cost=equipment.maintenance_cost,
                    magical_bonus=equipment.bonus,
                )
                self.economy.add_resource(resource)

            results["resources_used"].append(resource_name)

        return results

    def process_character_integration(self, character: Character, season: str, year: int) -> Dict[str, any]:
        """Process character effects on economy."""
        results = {"living_cost": 0.0, "activities": [], "resources_used": []}

        # Calculate living costs
        base_cost = 2.0  # Base living cost
        status_modifier = max(0, character.status - 2)
        total_cost = base_cost + (status_modifier * 0.5)

        results["living_cost"] = total_cost
        self.economy.add_expense(f"Living Cost {character.name}", total_cost)

        # Process seasonal activities
        current_activity = character.get_seasonal_activity(season, year)
        if current_activity:
            activity_results = self._process_activity(character, current_activity)
            results["activities"].append(activity_results)

        return results

    def process_vis_integration(self, season: str, year: int) -> Dict[str, any]:
        """Process vis sources and storage."""
        results = {"vis_gained": {}, "storage_cost": 0.0, "maintenance_issues": []}

        # Process vis sources
        for source in self.vis_manager.get_sources(self.covenant_name):
            if source.season == season:
                vis_gained = self.vis_manager.collect_vis(self.covenant_name, source)
                results["vis_gained"][source.form] = vis_gained

        # Calculate storage costs
        total_vis = sum(amount for amount in self.economy.stored_vis.values())
        storage_cost = total_vis * 0.1  # Cost per pawn of vis

        results["storage_cost"] = storage_cost
        self.economy.add_expense("Vis Storage", storage_cost)

        return results

    def process_magical_items(self, season: str, year: int) -> Dict[str, any]:
        """Process magical item maintenance."""
        results = {"maintenance_cost": 0.0, "items_maintained": [], "issues": []}

        for item in self.item_manager.get_covenant_items(self.covenant_name):
            # Calculate maintenance cost
            base_cost = item.level * 0.1
            effect_cost = len(item.effects) * 0.2
            total_cost = base_cost + effect_cost

            results["maintenance_cost"] += total_cost
            results["items_maintained"].append(item.name)

            # Add as magical resource if not exists
            if item.name not in self.economy.resources:
                resource = MagicalResource(
                    name=item.name,
                    category=ResourceCategory.MAGICAL,
                    quality=item.level,
                    maintenance_cost=total_cost,
                    magical_bonus=item.level // 5,
                )
                self.economy.add_resource(resource)

        self.economy.add_expense("Magical Items Maintenance", results["maintenance_cost"])

        return results

    def process_adventure_rewards(self, adventure_name: str) -> Dict[str, any]:
        """Process adventure rewards into economy."""
        results = {"resources_gained": [], "vis_gained": {}, "books_gained": [], "income_gained": 0.0}

        adventure = self.adventure_manager.get_adventure(adventure_name)
        if not adventure or adventure.status != "Completed":
            return results

        # Process rewards
        for reward_type, rewards in adventure.rewards.items():
            if reward_type == RewardType.VIS:
                for form, amount in rewards.items():
                    if form not in results["vis_gained"]:
                        results["vis_gained"][form] = 0
                    results["vis_gained"][form] += amount
                    self.economy.stored_vis[form] = self.economy.stored_vis.get(form, 0) + amount

            elif reward_type == RewardType.BOOKS:
                for book_data in rewards:
                    book = Book(
                        name=book_data["name"],
                        category=ResourceCategory.BOOKS,
                        quality=book_data["quality"],
                        level=book_data["level"],
                        subject=book_data["subject"],
                    )
                    self.economy.add_resource(book)
                    results["books_gained"].append(book.name)

            elif reward_type == RewardType.RESOURCES:
                self.economy.treasury += rewards.get("money", 0)
                results["income_gained"] += rewards.get("money", 0)

                for resource_data in rewards.get("items", []):
                    resource = MundaneResource(
                        name=resource_data["name"],
                        category=ResourceCategory.MUNDANE,
                        quality=resource_data["quality"],
                        resource_type=resource_data["type"],
                    )
                    self.economy.add_resource(resource)
                    results["resources_gained"].append(resource.name)

        return results

    def _process_activity(self, character: Character, activity: SeasonalActivity) -> Dict[str, any]:
        """Process a character's seasonal activity."""
        results = {"type": activity.type.value, "resources_used": [], "cost": 0.0}

        if activity.type == ActivityType.STUDY:
            # Check if studying from covenant books
            if "book" in activity.details:
                book_name = activity.details["book"]
                if book_name in self.economy.resources:
                    results["resources_used"].append(book_name)

        elif activity.type == ActivityType.LABORATORY:
            # Process lab maintenance
            if hasattr(character, "laboratory"):
                lab_results = self.process_laboratory_integration(character.laboratory, activity.season, activity.year)
                results.update(lab_results)

        elif activity.type == ActivityType.SERVICE:
            # Add income from covenant service
            service_payment = 2.0  # Base payment for covenant service
            self.economy.add_income_source(f"Service: {character.name}", service_payment)

        return results

    def save_state(self) -> None:
        """Save all integrated systems state."""
        base_path = Path("ars/data")
        self.economy.save_state(base_path / f"economy_{self.covenant_name}.yml")
        self.vis_manager.save_state(base_path / f"vis_{self.covenant_name}.yml")
        self.aura_manager.save_state(base_path / f"aura_{self.covenant_name}.yml")
        self.item_manager.save_state(base_path / f"items_{self.covenant_name}.yml")

    @classmethod
    def load_state(cls, covenant_name: str) -> "IntegratedCovenantManager":
        """Load all integrated systems state."""
        manager = cls(covenant_name)
        base_path = Path("ars/data")

        # Load each subsystem
        manager.economy = CovenantEconomy.load_state(base_path / f"economy_{covenant_name}.yml")
        manager.vis_manager = VisManager.load_state(base_path / f"vis_{covenant_name}.yml")
        manager.aura_manager = AuraManager.load_state(base_path / f"aura_{covenant_name}.yml")
        manager.item_manager = ItemCreationManager.load_state(base_path / f"items_{covenant_name}.yml")

        return manager
