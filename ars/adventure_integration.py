from typing import Dict, List

from .adventure import Adventure, AdventureManager, EncounterType, RewardType
from .character import Character
from .covenant import Covenant
from .laboratory import Laboratory
from .magic_items import ItemCreationManager
from .seasons import ActivityType, SeasonalActivity
from .vis_aura import AuraManager, VisManager


class IntegratedAdventureManager:
    """Manages adventures with full system integration."""

    def __init__(self, saga_name: str):
        self.saga_name = saga_name
        self.adventure_manager = AdventureManager()
        self.vis_manager = VisManager()
        self.aura_manager = AuraManager()
        self.item_manager = ItemCreationManager()

    def start_seasonal_adventure(
        self, adventure_name: str, participants: List[Character], season: str, year: int
    ) -> Dict[str, any]:
        """Start an adventure as a seasonal activity."""
        # Check if participants are available this season
        for participant in participants:
            if not self._check_seasonal_availability(participant, season, year):
                return {"error": f"Participant {participant.name} " f"is busy in {season} {year}"}

        # Start the adventure
        result = self.adventure_manager.start_adventure(adventure_name, participants)

        if "error" in result:
            return result

        # Register seasonal activity for each participant
        for participant in participants:
            activity = SeasonalActivity(
                character=participant.name,
                type=ActivityType.ADVENTURE,
                season=season,
                year=year,
                details={"adventure": adventure_name, "role": "participant"},
            )
            participant.add_seasonal_activity(activity)
            participant.save()

        return result

    def apply_covenant_effects(self, adventure: Adventure, covenant: Covenant) -> None:
        """Apply covenant effects to adventure."""
        # Apply aura effects
        local_aura = self.aura_manager.get_aura(covenant.location, adventure.season)
        if local_aura:
            adventure.aura_bonus = local_aura.strength

        # Add covenant resources as potential rewards
        if covenant.resources.get("vis_sources"):
            for source in covenant.resources["vis_sources"]:
                if source.season == adventure.season:
                    adventure.rewards[RewardType.VIS] = {source.form: source.amount}

        # Apply covenant defensive bonuses to combat encounters
        if covenant.defenses:
            for encounter in adventure.encounters:
                if encounter.type == EncounterType.COMBAT:
                    encounter.difficulty -= min(covenant.defenses // 2, 2)

    def apply_laboratory_effects(self, adventure: Adventure, participant: Character) -> None:
        """Apply laboratory effects to magical encounters."""
        if not hasattr(participant, "laboratory"):
            return

        lab = Laboratory.load(participant.laboratory)
        if not lab:
            return

        for encounter in adventure.encounters:
            if encounter.type == EncounterType.MAGICAL:
                # Apply specialization bonuses
                for spec, bonus in lab.specializations.items():
                    if spec.lower() in encounter.description.lower():
                        encounter.lab_bonus = bonus
                        break

                # Add lab equipment as backup resources
                if lab.equipment:
                    encounter.backup_equipment = True

    def process_adventure_vis(self, adventure: Adventure, covenant: Covenant) -> None:
        """Process vis gains and losses during adventure."""
        vis_changes = {}

        # Track vis used in magical encounters
        for encounter in adventure.encounters:
            if encounter.type == EncounterType.MAGICAL:
                vis_used = encounter.results.get("vis_used", {})
                for form, amount in vis_used.items():
                    if form not in vis_changes:
                        vis_changes[form] = 0
                    vis_changes[form] -= amount

        # Add vis rewards
        if RewardType.VIS in adventure.rewards:
            for form, amount in adventure.rewards[RewardType.VIS].items():
                if form not in vis_changes:
                    vis_changes[form] = 0
                vis_changes[form] += amount

        # Update covenant vis stores
        for form, change in vis_changes.items():
            self.vis_manager.modify_vis(covenant.name, form, change)

    def handle_magical_discoveries(self, adventure: Adventure, participant: Character) -> None:
        """Process magical discoveries during adventure."""
        for encounter in adventure.encounters:
            if encounter.type == EncounterType.DISCOVERY and encounter.completed:
                discovery = encounter.results.get("magical_discovery")
                if discovery:
                    if discovery.get("type") == "vis_source":
                        self.vis_manager.add_vis_source(
                            location=adventure.location,
                            form=discovery["form"],
                            amount=discovery["amount"],
                            season=discovery["season"],
                        )
                    elif discovery.get("type") == "magical_item":
                        self.item_manager.register_found_item(
                            name=discovery["name"], type=discovery["item_type"], effects=discovery["effects"]
                        )

    def apply_seasonal_effects(self, adventure: Adventure, season: str) -> None:
        """Apply seasonal effects to adventure."""
        season_effects = {
            "Spring": {"magical_bonus": 1, "vis_bonus": True},
            "Summer": {"combat_bonus": 1, "fatigue_penalty": -1},
            "Autumn": {"discovery_bonus": 1, "resource_bonus": True},
            "Winter": {"difficulty_increase": 1, "survival_check": True},
        }

        effects = season_effects.get(season, {})

        for encounter in adventure.encounters:
            if "magical_bonus" in effects and encounter.type == EncounterType.MAGICAL:
                encounter.difficulty -= effects["magical_bonus"]

            if "combat_bonus" in effects and encounter.type == EncounterType.COMBAT:
                encounter.difficulty -= effects["combat_bonus"]

            if "difficulty_increase" in effects:
                encounter.difficulty += effects["difficulty_increase"]

            if "discovery_bonus" in effects and encounter.type == EncounterType.DISCOVERY:
                if RewardType.VIS in encounter.rewards:
                    for form in encounter.rewards[RewardType.VIS]:
                        encounter.rewards[RewardType.VIS][form] += 1

    def record_adventure_history(self, adventure: Adventure, covenant: Covenant) -> None:
        """Record adventure in covenant's history."""
        history_entry = {
            "date": f"{adventure.season}, {adventure.year}",
            "type": "Adventure",
            "name": adventure.name,
            "participants": adventure.participants,
            "location": adventure.location,
            "outcome": adventure.status,
            "discoveries": [],
            "rewards": {},
        }

        # Record discoveries
        for encounter in adventure.encounters:
            if encounter.completed and encounter.type == EncounterType.DISCOVERY:
                discovery = encounter.results.get("magical_discovery")
                if discovery:
                    history_entry["discoveries"].append(discovery)

        # Record rewards
        for reward_type, rewards in adventure.rewards.items():
            history_entry["rewards"][reward_type.value] = rewards

        covenant.add_history_entry(history_entry)
        covenant.save()

    def _check_seasonal_availability(self, character: Character, season: str, year: int) -> bool:
        """Check if character is available for adventure this season."""
        if not hasattr(character, "seasonal_activities"):
            return True

        for activity in character.seasonal_activities:
            if activity.season == season and activity.year == year and activity.type != ActivityType.ADVENTURE:
                return False
        return True
