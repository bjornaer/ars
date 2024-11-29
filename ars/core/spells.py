from dataclasses import dataclass, field
from typing import Dict, List
# from enum import Enum

from ars.core.character import Character
from ars.core.types import (
    Duration, Form, Range, Target, Technique, FatigueLevel
)
from ars.core.dice import DiceRoller


class CastingResult:
    """Result of a spell casting attempt."""
    def __init__(
        self,
        success: bool,
        total: int,
        rolls: List[int],
        botch: bool = False,
        botch_dice: int = 0,
        fatigue_cost: int = 0,
        warping_gained: int = 0,
        aura_modifier: int = 0
    ):
        self.success = success
        self.total = total
        self.rolls = rolls
        self.botch = botch
        self.botch_dice = botch_dice
        self.fatigue_cost = fatigue_cost
        self.warping_gained = warping_gained
        self.aura_modifier = aura_modifier


@dataclass
class SpellEffect:
    """Represents a magical effect."""
    base_effect: str
    magnitude: int
    special_modifiers: Dict[str, int] = field(default_factory=dict)

    def calculate_magnitude(self) -> int:
        """Calculate total magnitude including modifiers."""
        return self.magnitude + sum(self.special_modifiers.values())

    def to_dict(self) -> dict:
        return {
            "base_effect": self.base_effect,
            "magnitude": self.magnitude,
            "special_modifiers": self.special_modifiers
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpellEffect":
        return cls(
            base_effect=data["base_effect"],
            magnitude=data["magnitude"],
            special_modifiers=data.get("special_modifiers", {})
        )


@dataclass
class Spell:
    """Represents a spell in Ars Magica."""
    name: str
    technique: Technique
    form: Form
    level: int
    range: Range
    duration: Duration
    target: Target
    description: str
    effects: List[SpellEffect] = field(default_factory=list)
    mastery_level: int = 0
    ritual: bool = False

    def calculate_casting_total(self, technique_score: int, form_score: int) -> int:
        """Calculate the base casting total for this spell."""
        return technique_score + form_score + self.mastery_level

    def get_magnitude(self) -> int:
        """Get total magnitude of all spell effects."""
        return sum(effect.calculate_magnitude() for effect in self.effects)

    def calculate_fatigue_cost(self) -> int:
        """Calculate base fatigue cost for casting."""
        if self.ritual:
            return 0  # Ritual spells don't cause fatigue
        return max(1, self.level // 5)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "technique": self.technique.value,
            "form": self.form.value,
            "level": self.level,
            "range": self.range.value,
            "duration": self.duration.value,
            "target": self.target.value,
            "description": self.description,
            "effects": [effect.to_dict() for effect in self.effects],
            "mastery_level": self.mastery_level,
            "ritual": self.ritual
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Spell":
        return cls(
            name=data["name"],
            technique=Technique(data["technique"]),
            form=Form(data["form"]),
            level=data["level"],
            range=Range(data["range"]),
            duration=Duration(data["duration"]),
            target=Target(data["target"]),
            description=data["description"],
            effects=[SpellEffect.from_dict(e) for e in data.get("effects", [])],
            mastery_level=data.get("mastery_level", 0),
            ritual=data.get("ritual", False)
        )


class SpellCaster:
    """Base class for spell casting mechanics."""

    @staticmethod
    def cast_spell(
        spell: Spell,
        caster: Character,
        aura: int = 0,
        modifiers: int = 0,
        stress: bool = True
    ) -> CastingResult:
        """Cast a spell using character's abilities."""
        
        # Calculate base casting total
        technique_score = getattr(caster, 'techniques', {}).get(spell.technique, 0)
        form_score = getattr(caster, 'forms', {}).get(spell.form, 0)
        casting_total = spell.calculate_casting_total(technique_score, form_score)

        # Apply fatigue and other modifiers
        fatigue_penalty = FatigueLevel.get_penalty(caster.fatigue_level)
        total_modifiers = modifiers + fatigue_penalty + aura

        # Perform casting roll
        if stress:
            roll = DiceRoller.stress_die()
            botch_dice = 0 if roll.roll != 0 else max(1, (spell.level // 5))
            botch_rolls = [DiceRoller.simple_die() for _ in range(botch_dice)]
            botched = roll.roll == 0 and all(r == 0 for r in botch_rolls)
        else:
            roll = DiceRoller.simple_die()
            botch_rolls = []
            botched = False

        # Calculate final total
        final_total = casting_total + roll.total + total_modifiers

        # Determine success and calculate warping
        success = final_total >= spell.level
        warping = 0
        if botched or (aura < 0 and roll.roll == 1):
            warping = 1

        # Calculate fatigue cost
        fatigue_cost = spell.calculate_fatigue_cost()
        if success:
            caster.modify_fatigue(fatigue_cost)

        return CastingResult(
            success=success,
            total=final_total,
            rolls=[roll.roll] + botch_rolls,
            botch=botched,
            fatigue_cost=fatigue_cost,
            warping_gained=warping,
            aura_modifier=aura
        )

    @staticmethod
    def calculate_penetration(
        casting_total: int,
        spell_level: int,
        penetration_bonus: int = 0
    ) -> int:
        """Calculate spell's penetration total."""
        return max(0, casting_total - spell_level + penetration_bonus)

    @staticmethod
    def calculate_ritual_time(spell_level: int) -> int:
        """Calculate time needed for ritual spell in minutes."""
        return spell_level * 15

    @staticmethod
    def calculate_lab_total(
        technique_score: int,
        form_score: int,
        intelligence: int,
        theory: int,
        modifiers: int = 0
    ) -> int:
        """Calculate laboratory total for spell related activities."""
        return technique_score + form_score + intelligence + theory + modifiers 

# ... (previous SpellCaster code) ...

    @staticmethod
    def cast_spontaneous(
        technique: Technique,
        form: Form,
        caster: 'Character',
        target_level: int,
        range: Range = Range.VOICE,
        duration: Duration = Duration.DIAMETER,
        target: Target = Target.INDIVIDUAL,
        modifiers: int = 0
    ) -> CastingResult:
        """Cast a spontaneous spell."""
        # Spontaneous magic uses half art scores
        technique_score = getattr(caster, 'techniques', {}).get(technique, 0) // 2
        form_score = getattr(caster, 'forms', {}).get(form, 0) // 2

        temp_spell = Spell(
            name=f"Spontaneous {technique.value} {form.value}",
            technique=technique,
            form=form,
            level=target_level,
            range=range,
            duration=duration,
            target=target,
            description="Spontaneous magic"
        )

        return SpellCaster.cast_spell(
            spell=temp_spell,
            caster=caster,
            modifiers=modifiers,
            stress=True  # Spontaneous magic is always stressful
        )

    @staticmethod
    def cast_ceremonial(
        spell: Spell,
        primary_caster: 'Character',
        participants: List['Character'],
        aura: int = 0,
        modifiers: int = 0
    ) -> CastingResult:
        """Cast a ceremonial version of a spell with multiple participants."""
        if not spell.ritual:
            raise ValueError("Only ritual spells can be cast ceremonially")

        # Calculate participant bonuses
        participant_bonus = sum(
            min(
                getattr(p, 'techniques', {}).get(spell.technique, 0),
                getattr(p, 'forms', {}).get(spell.form, 0)
            ) for p in participants
        ) // 5

        # Cast with combined power
        return SpellCaster.cast_spell(
            spell=spell,
            caster=primary_caster,
            aura=aura,
            modifiers=modifiers + participant_bonus,
            stress=True
        )

    @staticmethod
    def cast_with_arcane_connection(
        spell: Spell,
        caster: 'Character',
        connection_strength: int,
        aura: int = 0,
        modifiers: int = 0
    ) -> CastingResult:
        """Cast a spell using an arcane connection."""
        if spell.range != Range.ARCANE_CONNECTION:
            raise ValueError("Spell must be designed for arcane connection range")

        # Arcane connections provide a bonus based on their strength
        connection_bonus = min(connection_strength, 3)

        return SpellCaster.cast_spell(
            spell=spell,
            caster=caster,
            aura=aura,
            modifiers=modifiers + connection_bonus,
            stress=True
        )

    @staticmethod
    def cast_defiant(
        spell: Spell,
        caster: 'Character',
        aura: int = 0,
        modifiers: int = 0
    ) -> CastingResult:
        """Cast a spell defiantly, risking warping but increasing power."""
        # Defiant casting adds power but guarantees warping
        defiant_bonus = 5
        
        result = SpellCaster.cast_spell(
            spell=spell,
            caster=caster,
            aura=aura,
            modifiers=modifiers + defiant_bonus,
            stress=True
        )
        
        # Force warping gain
        result.warping_gained += 1
        
        return result