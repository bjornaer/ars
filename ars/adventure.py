from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .character import Character
from .dice import DiceRoller


class AdventureType(Enum):
    """Types of adventures."""

    QUEST = "Quest"
    INVESTIGATION = "Investigation"
    POLITICAL = "Political"
    MAGICAL = "Magical"
    COMBAT = "Combat"
    SOCIAL = "Social"


class EncounterType(Enum):
    """Types of encounters."""

    COMBAT = "Combat"
    SOCIAL = "Social"
    MAGICAL = "Magical"
    PUZZLE = "Puzzle"
    CHALLENGE = "Challenge"
    DISCOVERY = "Discovery"


class RewardType(Enum):
    """Types of rewards."""

    VIS = "Vis"
    BOOKS = "Books"
    EQUIPMENT = "Equipment"
    REPUTATION = "Reputation"
    EXPERIENCE = "Experience"
    RESOURCES = "Resources"


@dataclass
class Encounter:
    """An encounter within an adventure."""

    type: EncounterType
    difficulty: int
    description: str
    requirements: Dict[str, int] = field(default_factory=dict)
    rewards: Dict[RewardType, Dict] = field(default_factory=dict)
    completed: bool = False
    results: Dict = field(default_factory=dict)


@dataclass
class Adventure:
    """An adventure with multiple encounters."""

    name: str
    type: AdventureType
    description: str
    location: str
    season: str
    year: int
    difficulty: int
    encounters: List[Encounter] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    rewards: Dict[RewardType, Dict] = field(default_factory=dict)
    status: str = "Not Started"
    results: Dict = field(default_factory=dict)


class AdventureManager:
    """Manages adventures and encounters."""

    def __init__(self):
        self.adventures: Dict[str, Adventure] = {}
        self.active_adventure: Optional[Adventure] = None
        self.dice = DiceRoller()

    def create_adventure(
        self, name: str, type: AdventureType, description: str, location: str, season: str, year: int, difficulty: int
    ) -> Adventure:
        """Create a new adventure."""
        adventure = Adventure(
            name=name,
            type=type,
            description=description,
            location=location,
            season=season,
            year=year,
            difficulty=difficulty,
        )
        self.adventures[name] = adventure
        return adventure

    def add_encounter(
        self,
        adventure_name: str,
        encounter_type: EncounterType,
        difficulty: int,
        description: str,
        requirements: Optional[Dict[str, int]] = None,
        rewards: Optional[Dict[RewardType, Dict]] = None,
    ) -> bool:
        """Add an encounter to an adventure."""
        if adventure_name not in self.adventures:
            return False

        encounter = Encounter(
            type=encounter_type,
            difficulty=difficulty,
            description=description,
            requirements=requirements or {},
            rewards=rewards or {},
        )

        self.adventures[adventure_name].encounters.append(encounter)
        return True

    def start_adventure(self, adventure_name: str, participants: List[Character]) -> Dict[str, any]:
        """Start an adventure with given participants."""
        if adventure_name not in self.adventures:
            return {"error": "Adventure not found"}

        adventure = self.adventures[adventure_name]
        if adventure.status != "Not Started":
            return {"error": "Adventure already in progress or completed"}

        # Check participant requirements
        for participant in participants:
            if not self._check_participant_requirements(participant, adventure):
                return {"error": f"Participant {participant.name} " "does not meet requirements"}

        adventure.status = "In Progress"
        adventure.participants = [p.name for p in participants]
        self.active_adventure = adventure

        return {"status": "started", "adventure": adventure.name, "participants": adventure.participants}

    def resolve_encounter(self, encounter_index: int, actions: Dict[str, Dict[str, any]]) -> Dict[str, any]:
        """Resolve an encounter with given actions."""
        if not self.active_adventure:
            return {"error": "No active adventure"}

        if encounter_index >= len(self.active_adventure.encounters):
            return {"error": "Invalid encounter index"}

        encounter = self.active_adventure.encounters[encounter_index]
        if encounter.completed:
            return {"error": "Encounter already completed"}

        results = {}
        success = True

        # Process each participant's actions
        for participant_name, action_data in actions.items():
            result = self._process_action(participant_name, action_data, encounter)
            results[participant_name] = result
            if not result.get("success", False):
                success = False

        # Update encounter status
        encounter.completed = success
        encounter.results = results

        # Check if adventure is completed
        if all(e.completed for e in self.active_adventure.encounters):
            self.active_adventure.status = "Completed"
            self._distribute_rewards()

        return {"success": success, "results": results, "adventure_status": self.active_adventure.status}

    def _check_participant_requirements(self, participant: Character, adventure: Adventure) -> bool:
        """Check if participant meets adventure requirements."""
        # Basic requirements based on adventure type
        if adventure.type == AdventureType.MAGICAL:
            if not hasattr(participant, "techniques"):
                return False
            # Check for minimum magic theory
            if participant.abilities.get("Magic Theory", 0) < adventure.difficulty // 2:
                return False

        elif adventure.type == AdventureType.COMBAT:
            # Check for combat abilities
            combat_ability = max(
                participant.abilities.get("Single Weapon", 0), participant.abilities.get("Brawling", 0)
            )
            if combat_ability < adventure.difficulty // 3:
                return False

        return True

    def _process_action(
        self, participant_name: str, action_data: Dict[str, any], encounter: Encounter
    ) -> Dict[str, any]:
        """Process a participant's action in an encounter."""
        # Get participant character
        participant = Character.load(participant_name)
        if not participant:
            return {"error": "Participant not found"}

        # Calculate base success chance
        base_chance = self._calculate_base_chance(participant, action_data, encounter)

        # Roll for success
        roll = self.dice.stress_roll()
        success = roll + base_chance >= encounter.difficulty * 3

        return {
            "success": success,
            "roll": roll,
            "total": roll + base_chance,
            "needed": encounter.difficulty * 3,
            "effects": self._calculate_effects(success, roll, base_chance, encounter),
        }

    def _calculate_base_chance(self, participant: Character, action_data: Dict[str, any], encounter: Encounter) -> int:
        """Calculate base success chance for an action."""
        base = 0

        if encounter.type == EncounterType.COMBAT:
            # Combat calculations
            weapon_ability = participant.abilities.get(action_data.get("weapon_ability", "Single Weapon"), 0)
            base = weapon_ability * 3

        elif encounter.type == EncounterType.MAGICAL:
            # Magical calculations
            technique = action_data.get("technique")
            form = action_data.get("form")
            if technique and form:
                base = participant.techniques.get(technique, 0) + participant.forms.get(form, 0)

        elif encounter.type == EncounterType.SOCIAL:
            # Social calculations
            relevant_ability = participant.abilities.get(action_data.get("ability", "Communication"), 0)
            base = relevant_ability * 2

        # Add characteristic bonuses
        if "characteristic" in action_data:
            char_value = getattr(participant, action_data["characteristic"].lower(), 0)
            base += char_value

        return base

    def _calculate_effects(self, success: bool, roll: int, base_chance: int, encounter: Encounter) -> Dict[str, any]:
        """Calculate effects of an action."""
        effects = {"botch": False, "critical": False}

        if roll == 0:
            # Check for botch
            botch_roll = self.dice.simple_roll(6)
            effects["botch"] = botch_roll <= 2
        elif roll >= 9:
            # Critical success
            effects["critical"] = True

        # Calculate magnitude of success/failure
        total = roll + base_chance
        magnitude = abs(total - (encounter.difficulty * 3)) // 3
        effects["magnitude"] = magnitude

        return effects

    def _distribute_rewards(self) -> None:
        """Distribute rewards for completed adventure."""
        if not self.active_adventure:
            return

        # Collect all rewards
        total_rewards = {}
        for encounter in self.active_adventure.encounters:
            if encounter.completed:
                for reward_type, reward_data in encounter.rewards.items():
                    if reward_type not in total_rewards:
                        total_rewards[reward_type] = {}
                    # Merge reward data
                    for key, value in reward_data.items():
                        if key in total_rewards[reward_type]:
                            total_rewards[reward_type][key] += value
                        else:
                            total_rewards[reward_type][key] = value

        # Add adventure-level rewards
        for reward_type, reward_data in self.active_adventure.rewards.items():
            if reward_type not in total_rewards:
                total_rewards[reward_type] = {}
            for key, value in reward_data.items():
                if key in total_rewards[reward_type]:
                    total_rewards[reward_type][key] += value
                else:
                    total_rewards[reward_type][key] = value

        # Distribute to participants
        for participant_name in self.active_adventure.participants:
            participant = Character.load(participant_name)
            if participant:
                self._apply_rewards(participant, total_rewards)
                participant.save()

    def _apply_rewards(self, character: Character, rewards: Dict[RewardType, Dict]) -> None:
        """Apply rewards to a character."""
        for reward_type, reward_data in rewards.items():
            if reward_type == RewardType.VIS:
                # Add vis to character's inventory
                if not hasattr(character, "vis"):
                    character.vis = {}
                for form, amount in reward_data.items():
                    if form in character.vis:
                        character.vis[form] += amount
                    else:
                        character.vis[form] = amount

            elif reward_type == RewardType.EXPERIENCE:
                # Add experience points
                for ability, xp in reward_data.items():
                    character.add_experience(ability, xp)

            elif reward_type == RewardType.REPUTATION:
                # Modify reputations
                if not hasattr(character, "reputations"):
                    character.reputations = {}
                for rep_type, value in reward_data.items():
                    if rep_type in character.reputations:
                        character.reputations[rep_type] += value
                    else:
                        character.reputations[rep_type] = value

    def save_state(self, filepath: Path) -> None:
        """Save adventure state."""
        data = {
            "adventures": {name: self._serialize_adventure(adv) for name, adv in self.adventures.items()},
            "active_adventure": (self.active_adventure.name if self.active_adventure else None),
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load_state(cls, filepath: Path) -> "AdventureManager":
        """Load adventure state."""
        manager = cls()

        with filepath.open("r") as f:
            data = yaml.safe_load(f)

            for name, adv_data in data.get("adventures", {}).items():
                manager.adventures[name] = cls._deserialize_adventure(adv_data)

            active_name = data.get("active_adventure")
            if active_name:
                manager.active_adventure = manager.adventures.get(active_name)

        return manager

    @staticmethod
    def _serialize_adventure(adventure: Adventure) -> Dict:
        """Serialize adventure data."""
        return {
            "name": adventure.name,
            "type": adventure.type.value,
            "description": adventure.description,
            "location": adventure.location,
            "season": adventure.season,
            "year": adventure.year,
            "difficulty": adventure.difficulty,
            "encounters": [
                {
                    "type": e.type.value,
                    "difficulty": e.difficulty,
                    "description": e.description,
                    "requirements": e.requirements,
                    "rewards": {k.value: v for k, v in e.rewards.items()},
                    "completed": e.completed,
                    "results": e.results,
                }
                for e in adventure.encounters
            ],
            "participants": adventure.participants,
            "rewards": {k.value: v for k, v in adventure.rewards.items()},
            "status": adventure.status,
            "results": adventure.results,
        }

    @staticmethod
    def _deserialize_adventure(data: Dict) -> Adventure:
        """Deserialize adventure data."""
        adventure = Adventure(
            name=data["name"],
            type=AdventureType(data["type"]),
            description=data["description"],
            location=data["location"],
            season=data["season"],
            year=data["year"],
            difficulty=data["difficulty"],
        )

        adventure.encounters = [
            Encounter(
                type=EncounterType(e["type"]),
                difficulty=e["difficulty"],
                description=e["description"],
                requirements=e["requirements"],
                rewards={RewardType(k): v for k, v in e["rewards"].items()},
                completed=e["completed"],
                results=e["results"],
            )
            for e in data["encounters"]
        ]

        adventure.participants = data["participants"]
        adventure.rewards = {RewardType(k): v for k, v in data["rewards"].items()}
        adventure.status = data["status"]
        adventure.results = data["results"]

        return adventure
