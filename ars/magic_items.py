from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import yaml

from ars.events import EventRecorder
from ars.laboratory import Laboratory
from ars.core.types import Form, InstallationType, ItemType, Technique, EventType, Season
from ars.vis_aura import VisManager
from ars.core.base_types import BaseMagicItem
from ars.character import Character
# if TYPE_CHECKING:

@dataclass
class ItemEffect:
    """A magical effect installed in an item."""

    name: str
    technique: Technique
    form: Form
    level: int = 0
    penetration: int = 0
    installation_type: InstallationType = InstallationType.EFFECT
    uses_per_day: Optional[int] = None
    trigger_condition: Optional[str] = None
    lab_total: int = 0
    seasons_required: int = 1
    vis_required: Dict[Form, int] = field(default_factory=dict)
    description: str = ""


@dataclass
class MagicItem(BaseMagicItem):
    """A magical item with enchantments."""

    name: str = ""
    type: ItemType = ItemType.CHARGED
    creator: str = ""
    base_material: str = ""
    size: int = 0
    shape_bonus: int = 0
    material_bonus: int = 0
    effects: List[ItemEffect] = field(default_factory=list)
    attunement_bonus: int = 0
    aura_bonus: int = 0
    vis_capacity: int = 0
    current_capacity: int = 0
    description: str = ""

    def calculate_total_bonus(self) -> int:
        """Calculate total bonus for item creation."""
        return self.shape_bonus + self.material_bonus + self.attunement_bonus + self.aura_bonus

    def calculate_remaining_capacity(self) -> int:
        """Calculate remaining vis capacity."""
        return self.vis_capacity - self.current_capacity

    def can_add_effect(self, effect: ItemEffect) -> bool:
        """Check if effect can be added to item."""
        if self.type == ItemType.CHARGED:
            return len(self.effects) == 0

        vis_needed = sum(effect.vis_required.values())
        return vis_needed <= self.calculate_remaining_capacity()


class ItemCreationManager(EventRecorder):
    """Manages magic item creation process."""

    def __init__(self, event_manager=None):
        super().__init__(event_manager)
        self.material_bonuses: Dict[str, int] = {}
        self.shape_bonuses: Dict[str, int] = {}
        self.current_projects: Dict[str, Tuple[MagicItem, ItemEffect]] = {}

    def start_project(
        self,
        character: Character,
        laboratory: Laboratory,
        item: MagicItem,
        effect: ItemEffect,
        year: int,
        season: Season,
    ) -> bool:
        """Start a new item creation project."""
        if not item.can_add_effect(effect):
            self.record_event(
                type=EventType.ITEM_CREATION,
                description=f"Failed to start item creation: {item.name} cannot accept effect {effect.name}",
                details={
                    "character": character.name,
                    "item_name": item.name,
                    "effect_name": effect.name,
                    "reason": "Capacity exceeded or incompatible effect",
                },
                year=year,
                season=season,
            )
            return False

        # Calculate lab total for effect
        art_score = character.techniques.get(effect.technique.value, 0) + character.forms.get(effect.form.value, 0)
        lab_total = art_score + laboratory.magical_aura + item.calculate_total_bonus()
        effect.lab_total = lab_total

        # Calculate seasons required
        effect.seasons_required = max(1, effect.level // lab_total)

        # Calculate vis requirements
        if item.type != ItemType.LESSER:
            effect.vis_required = self._calculate_vis_requirements(effect, item.type)

        self.current_projects[character.name] = (item, effect)

        self.record_event(
            type=EventType.ITEM_CREATION,
            description=f"Started creation of {effect.name} in {item.name}",
            details={
                "character": character.name,
                "item_name": item.name,
                "effect_name": effect.name,
                "lab_total": lab_total,
                "seasons_required": effect.seasons_required,
                "vis_required": {k.value: v for k, v in effect.vis_required.items()},
                "laboratory_conditions": {
                    "aura": laboratory.magical_aura,
                    "art_score": art_score,
                    "total_bonus": item.calculate_total_bonus(),
                },
            },
            year=year,
            season=season,
        )
        return True

    def _calculate_vis_requirements(self, effect: ItemEffect, item_type: ItemType) -> Dict[Form, int]:
        """Calculate vis requirements for effect installation."""
        vis_requirements = {}

        base_vis = max(1, effect.level // 5)
        if item_type == ItemType.CHARGED:
            vis_requirements[effect.technique] = base_vis
            vis_requirements[effect.form] = base_vis // 2
        elif item_type == ItemType.INVESTED:
            vis_requirements[effect.technique] = base_vis * 2
            vis_requirements[effect.form] = base_vis
        elif item_type == ItemType.GREATER:
            vis_requirements[effect.technique] = base_vis * 3
            vis_requirements[effect.form] = base_vis * 2
        elif item_type == ItemType.TALISMAN:
            vis_requirements[effect.technique] = base_vis * 2
            vis_requirements[effect.form] = base_vis * 2

        return vis_requirements

    def continue_project(
        self,
        character: Character,
        laboratory: Laboratory,
        vis_manager: Optional[VisManager] = None,
        year: int = None,
        season: Season = None,
    ) -> Dict[str, any]:
        """Continue work on current project."""
        if character.name not in self.current_projects:
            return {"error": "No active project"}

        item, effect = self.current_projects[character.name]

        # Check for vis requirements if first season
        if effect.seasons_required > 0 and vis_manager:
            for form, amount in effect.vis_required.items():
                if not vis_manager.use_vis(form, amount):
                    self.record_event(
                        type=EventType.ITEM_CREATION,
                        description="Failed to continue project: insufficient vis",
                        details={
                            "character": character.name,
                            "item_name": item.name,
                            "effect_name": effect.name,
                            "missing_vis": {form.value: amount},
                        },
                        year=year,
                        season=season,
                    )
                    return {"error": f"Insufficient {form.value} vis"}

        # Progress project
        effect.seasons_required -= 1

        if effect.seasons_required <= 0:
            # Complete effect installation
            item.effects.append(effect)
            item.current_capacity += sum(effect.vis_required.values())
            del self.current_projects[character.name]

            self.record_event(
                type=EventType.ITEM_CREATION,
                description=f"Completed installation of {effect.name} in {item.name}",
                details={
                    "character": character.name,
                    "item_name": item.name,
                    "effect_name": effect.name,
                    "final_capacity": item.current_capacity,
                    "remaining_capacity": item.calculate_remaining_capacity(),
                },
                year=year,
                season=season,
            )

            return {"status": "completed", "item": item, "effect": effect}

        self.record_event(
            type=EventType.ITEM_CREATION,
            description=f"Continued work on {effect.name} in {item.name}",
            details={
                "character": character.name,
                "item_name": item.name,
                "effect_name": effect.name,
                "seasons_remaining": effect.seasons_required,
            },
            year=year,
            season=season,
        )

        return {"status": "in_progress", "seasons_remaining": effect.seasons_required}

    def save_state(self, filepath: Path) -> None:
        """Save current projects state."""
        data = {
            "projects": {
                char: {"item": self._serialize_item(item), "effect": self._serialize_effect(effect)}
                for char, (item, effect) in self.current_projects.items()
            }
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load_state(cls, filepath: Path) -> "ItemCreationManager":
        """Load projects state."""
        manager = cls()

        with filepath.open("r") as f:
            data = yaml.safe_load(f)

            for char, project in data.get("projects", {}).items():
                item = cls._deserialize_item(project["item"])
                effect = cls._deserialize_effect(project["effect"])
                manager.current_projects[char] = (item, effect)

        return manager

    @staticmethod
    def _serialize_item(item: MagicItem) -> Dict:
        """Serialize item data."""
        return {
            "name": item.name,
            "type": item.type.value,
            "creator": item.creator,
            "base_material": item.base_material,
            "size": item.size,
            "shape_bonus": item.shape_bonus,
            "material_bonus": item.material_bonus,
            "effects": [ItemCreationManager._serialize_effect(e) for e in item.effects],
            "attunement_bonus": item.attunement_bonus,
            "aura_bonus": item.aura_bonus,
            "vis_capacity": item.vis_capacity,
            "current_capacity": item.current_capacity,
            "description": item.description,
        }

    @staticmethod
    def _deserialize_item(data: Dict) -> MagicItem:
        """Deserialize item data."""
        effects = [ItemCreationManager._deserialize_effect(e) for e in data.pop("effects", [])]
        return MagicItem(**{**data, "type": ItemType(data["type"]), "effects": effects})

    @staticmethod
    def _serialize_effect(effect: ItemEffect) -> Dict:
        """Serialize effect data."""
        return {
            "name": effect.name,
            "technique": effect.technique.value,
            "form": effect.form.value,
            "level": effect.level,
            "penetration": effect.penetration,
            "installation_type": effect.installation_type.value,
            "uses_per_day": effect.uses_per_day,
            "trigger_condition": effect.trigger_condition,
            "lab_total": effect.lab_total,
            "seasons_required": effect.seasons_required,
            "vis_required": {k.value: v for k, v in effect.vis_required.items()},
            "description": effect.description,
        }

    @staticmethod
    def _deserialize_effect(data: Dict) -> ItemEffect:
        """Deserialize effect data."""
        return ItemEffect(
            **{
                **data,
                "technique": Technique(data["technique"]),
                "form": Form(data["form"]),
                "installation_type": InstallationType(data["installation_type"]),
                "vis_required": {Form(k): v for k, v in data.get("vis_required", {}).items()},
            }
        )
