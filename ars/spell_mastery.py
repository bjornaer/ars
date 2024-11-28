from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ars.spells import Spell


class MasteryCategory(Enum):
    CONTROL = "Control"
    FINESSE = "Finesse"
    POWER = "Power"
    EFFICIENCY = "Efficiency"


@dataclass
class MasteryEffect:
    name: str
    description: str
    level_required: int
    category: MasteryCategory
    effect: Dict[str, any]


class SpellMasteryEffects:
    """Enhanced registry of available mastery effects."""

    EFFECTS = {
        # Control Effects
        "fast_cast": MasteryEffect(
            name="Fast Cast",
            description="Cast spell as a fast action",
            level_required=1,
            category=MasteryCategory.CONTROL,
            effect={"initiative_bonus": 3},
        ),
        "quiet_casting": MasteryEffect(
            name="Quiet Casting",
            description="Cast without voice",
            level_required=2,
            category=MasteryCategory.CONTROL,
            effect={"silent": True},
        ),
        "subtle_casting": MasteryEffect(
            name="Subtle Casting",
            description="Cast without obvious gestures",
            level_required=2,
            category=MasteryCategory.CONTROL,
            effect={"subtle": True},
        ),
        # Finesse Effects
        "precise_targeting": MasteryEffect(
            name="Precise Targeting",
            description="Better accuracy with targeted spells",
            level_required=1,
            category=MasteryCategory.FINESSE,
            effect={"targeting_bonus": 3},
        ),
        "controlled_effect": MasteryEffect(
            name="Controlled Effect",
            description="Fine control over spell's manifestation",
            level_required=2,
            category=MasteryCategory.FINESSE,
            effect={"control_bonus": 3},
        ),
        # Power Effects
        "penetration": MasteryEffect(
            name="Penetration",
            description="Improved magic resistance penetration",
            level_required=1,
            category=MasteryCategory.POWER,
            effect={"penetration_bonus": 3},
        ),
        "multiple_casting": MasteryEffect(
            name="Multiple Casting",
            description="Cast spell multiple times per round",
            level_required=2,
            category=MasteryCategory.POWER,
            effect={"max_casts": 2},
        ),
        "boosted_casting": MasteryEffect(
            name="Boosted Casting",
            description="Increase spell level at cost of fatigue",
            level_required=3,
            category=MasteryCategory.POWER,
            effect={"level_boost": 5, "extra_fatigue": 2},
        ),
        # Efficiency Effects
        "fatigue_reduction": MasteryEffect(
            name="Fatigue Reduction",
            description="Reduce fatigue cost of casting",
            level_required=1,
            category=MasteryCategory.EFFICIENCY,
            effect={"fatigue_reduction": 1},
        ),
        "mastered_concentration": MasteryEffect(
            name="Mastered Concentration",
            description="Maintain concentration with less effort",
            level_required=2,
            category=MasteryCategory.EFFICIENCY,
            effect={"concentration_bonus": 3},
        ),
    }

    @classmethod
    def get_available_effects(
        cls, mastery_level: int, category: Optional[MasteryCategory] = None
    ) -> List[MasteryEffect]:
        """Get available mastery effects for a given level and optional category."""
        effects = []
        for effect in cls.EFFECTS.values():
            if effect.level_required <= mastery_level:
                if category is None or effect.category == category:
                    effects.append(effect)
        return effects

    @classmethod
    def apply_mastery_effects(cls, spell: "Spell", effects: List[str]) -> Dict[str, any]:
        """Apply selected mastery effects to spell casting."""
        modifiers = {}
        for effect_name in effects:
            if effect_name in cls.EFFECTS:
                effect = cls.EFFECTS[effect_name]
                modifiers.update(effect.effect)
        return modifiers
