from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ars.character import Character
from ars.dice import DiceRoller, DiceResult
from ars.core.types import Duration, Form, Range, Target, Technique


@dataclass
class SpellEffect:
    """Represents a magical effect."""

    base_effect: str
    magnitude: int
    special_modifiers: dict[str, int] = field(default_factory=dict)

    def calculate_magnitude(self) -> int:
        """Calculate total magnitude including modifiers."""
        return self.magnitude + sum(self.special_modifiers.values())


@dataclass
class Spell:
    """Represents a spell in Ars Magica."""

    name: str
    technique: str
    form: str
    level: int
    range: Range
    duration: Duration
    target: Target
    description: str
    effects: list[SpellEffect] = field(default_factory=list)
    mastery_level: int = 0

    def casting_total(self, technique_score: int, form_score: int) -> int:
        """Calculate the casting total for this spell."""
        return technique_score + form_score + self.mastery_level

    def get_magnitude(self) -> int:
        """Get total magnitude of all spell effects."""
        return sum(effect.calculate_magnitude() for effect in self.effects)

    @classmethod
    def create(cls, params: "SpellParameters", effects: list[SpellEffect] | None = None) -> "Spell":
        """Create a spell from parameters."""
        if effects is None:
            base_effect = f"{params.technique} {params.form}"
            default_effects = [SpellEffect(base_effect, 5, {"size": 2, "heat": 3})]
        else:
            default_effects = effects

        return cls(
            name=params.name,
            technique=params.technique,
            form=params.form,
            level=params.level,
            range=params.range,
            duration=params.duration,
            target=params.target,
            description=params.description,
            effects=default_effects,
        )


@dataclass
class SpellParameters:
    """Parameters for spell casting."""

    technique: str
    form: str
    range: Range
    duration: Duration
    target: Target
    level: int
    aura: int = 0
    modifiers: int = 0
    name: str = "Unnamed Spell"
    mastery_level: int = 0
    description: str = "Undescribed spell"


@dataclass
class SpellTemplate:
    """Template for creating spells of similar effects."""

    name_pattern: str
    technique: Technique
    form: Form
    base_level: int
    effects: list[SpellEffect]
    description_pattern: str

    def create_spell(
        self, specific_name: str, range: Range, duration: Duration, target: Target, modifiers: dict[str, int] = None
    ) -> "Spell":
        """Create a specific spell from this template."""
        # Extract the element name from the specific_name
        # For example, from "Ball of Intense Fire" we get "Intense" as the element
        element = specific_name.replace("Ball of ", "").replace(" Fire", "")

        params = SpellParameters(
            technique=self.technique.value,
            form=self.form.value,
            range=range,
            duration=duration,
            target=target,
            level=self.base_level,
        )

        if modifiers:
            params.modifiers = sum(modifiers.values())

        return Spell(
            name=specific_name,
            technique=self.technique.value,
            form=self.form.value,
            level=SpellCaster.calculate_spell_level(params),
            range=range.value,
            duration=duration.value,
            target=target.value,
            description=self.description_pattern.format(element=element),  # Use element instead of name
            effects=[SpellEffect(e.base_effect, e.magnitude, modifiers if modifiers else {}) for e in self.effects],
        )


class SpellRegistry:
    """Registry of common spell templates."""

    @staticmethod
    def get_template(name: str) -> SpellTemplate | None:
        """Get a spell template by name."""
        templates = {
            "ball_of_fire": SpellTemplate(
                name_pattern="Ball of {element} Fire",
                technique=Technique.CREO,
                form=Form.IGNEM,
                base_level=10,
                effects=[SpellEffect("Create fire", 5, {"size": 2, "heat": 3})],
                description_pattern="Creates a ball of magical fire that can be hurled at targets.",
            ),
            "shield_of_protection": SpellTemplate(
                name_pattern="Shield of {element} Protection",
                technique=Technique.REGO,
                form=Form.VIM,
                base_level=15,
                effects=[SpellEffect("Magical shield", 5, {"duration": 2})],
                description_pattern="Creates a protective shield against magical effects.",
            ),
            # Add more templates as needed
        }
        return templates.get(name)


class FatigueLevel(Enum):
    FRESH = 0
    WINDED = 1
    WEARY = 2
    TIRED = 3
    DAZED = 4
    UNCONSCIOUS = 5


@dataclass
class CastingResult:
    success: bool
    roll_result: DiceResult
    fatigue_cost: int
    warping_gained: int = 0
    botch_details: Optional[str] = None


class SpellCaster:
    """Enhanced spell casting mechanics."""

    @staticmethod
    def cast_spell(
        spell: "Spell", character: "Character", aura: int = 0, modifiers: int = 0, stress: bool = True
    ) -> CastingResult:
        """Enhanced spell casting with fatigue tracking."""
        # Calculate fatigue cost
        base_fatigue = max(1, spell.level // 5)
        fatigue_reduction = character.get_fatigue_reduction()  # From virtues/equipment
        final_fatigue = max(0, base_fatigue - fatigue_reduction)

        # Check if character can cast
        current_fatigue = character.get_fatigue_level()
        if current_fatigue.value + final_fatigue >= FatigueLevel.UNCONSCIOUS.value:
            return CastingResult(
                success=False,
                roll_result=DiceResult(rolls=[0], multiplier=1, botch=False),
                fatigue_cost=final_fatigue,
                botch_details="Too fatigued to cast",
            )

        # Perform casting roll
        roll = DiceRoller.spell_check(
            casting_total=character.techniques[spell.technique] + character.forms[spell.form] + spell.mastery_level,
            aura_modifier=aura,
            fatigue_level=current_fatigue.value,
            stress=stress,
            botch_dice=0,
        )

        # Calculate warping
        warping = 0
        if roll.botch or (aura > 5 and roll.rolls[0] == 1):
            warping = 1

        # Apply fatigue if cast successful
        success = roll.total >= spell.level
        if success:
            character.add_fatigue(final_fatigue)

        return CastingResult(
            success=success,
            roll_result=roll,
            fatigue_cost=final_fatigue,
            warping_gained=warping,
            botch_details="Magical botch!" if roll.botch else None,
        )

    @staticmethod
    def calculate_spell_level(params: SpellParameters) -> int:
        """Calculate base spell level from parameters.

        Args:
            params: Spell parameters

        Returns:
            Base spell level
        """
        base = 0

        # Range modifiers
        range_mods = {Range.PERSONAL: 0, Range.TOUCH: 0, Range.VOICE: 2, Range.SIGHT: 3, Range.ARCANE_CONNECTION: 4}
        base += range_mods[params.range]

        # Duration modifiers
        duration_mods = {
            Duration.MOMENTARY: 0,
            Duration.CONCENTRATION: 1,
            Duration.DIAMETER: 2,
            Duration.SUN: 3,
            Duration.MOON: 4,
            Duration.YEAR: 5,
        }
        base += duration_mods[params.duration]

        # Target modifiers
        target_mods = {Target.INDIVIDUAL: 0, Target.GROUP: 2, Target.ROOM: 2, Target.STRUCTURE: 3, Target.BOUNDARY: 4}
        base += target_mods[params.target]

        return base + params.level
