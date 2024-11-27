from dataclasses import dataclass, field

from ars.dice import ArtRoller, DiceResult
from ars.types import Duration, Form, Range, Target, Technique


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
    range: str
    duration: str
    target: str
    description: str
    effects: list[SpellEffect] = field(default_factory=list)
    mastery_level: int = 0

    def casting_total(self, technique_score: int, form_score: int) -> int:
        """Calculate the casting total for this spell."""
        return technique_score + form_score + self.mastery_level

    def get_magnitude(self) -> int:
        """Get total magnitude of all spell effects."""
        return sum(effect.calculate_magnitude() for effect in self.effects)


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


class SpellCaster:
    """Handles spell casting mechanics."""

    @staticmethod
    def cast_spell(
        spell: "Spell", technique_score: int, form_score: int, aura: int = 0, modifiers: int = 0, stress: bool = True
    ) -> tuple[bool, DiceResult]:
        """Attempt to cast a spell.

        Args:
            spell: The spell being cast
            technique_score: Caster's technique score
            form_score: Caster's form score
            aura: Magical aura modifier
            modifiers: Additional situational modifiers
            stress: Whether to use stress die

        Returns:
            Tuple of (success: bool, roll_result: DiceResult)
        """
        roll = ArtRoller.cast_spell(
            technique_score, form_score, aura=aura, stress=stress, modifiers=modifiers + spell.mastery_level
        )

        success = roll.total >= spell.level
        return success, roll

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
