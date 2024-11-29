from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ars.core.character import Character
from ars.core.types import (
    Duration, Form, House, Range, Target, Technique
)
from ars.core.spells import CastingResult, Spell, SpellCaster


@dataclass
class Magus(Character, SpellCaster):
    """Represents a magical character (Magus) in Ars Magica."""
    
    # Magic-specific attributes
    house: House = House.EX_MISCELLANEA
    parma_magica: int = 0
    magic_resistance: int = 0
    warping_score: int = 0
    warping_points: int = 0
    
    # Magical arts
    techniques: Dict[Technique, int] = field(default_factory=dict)
    forms: Dict[Form, int] = field(default_factory=dict)
    
    # Spells and mastery
    spells: Dict[str, Spell] = field(default_factory=dict)
    mastered_spells: Dict[str, int] = field(default_factory=dict)  # spell_name -> mastery level

    def __post_init__(self):
        """Initialize magical attributes."""
        super().__post_init__()
        
        # Initialize arts if not present
        for technique in Technique:
            if technique not in self.techniques:
                self.techniques[technique] = 0
                
        for form in Form:
            if form not in self.forms:
                self.forms[form] = 0

    def add_warping_points(self, points: int, source: str) -> None:
        """Add warping points and check for score increase."""
        self.warping_points += points
        old_score = self.warping_score
        
        # Check for warping score increase
        self.warping_score = self.warping_points // 5
        gained_score = self.warping_score - old_score

    def activate_parma_magica(self) -> None:
        """Activate Parma Magica protection."""
        self.magic_resistance = self.parma_magica * 5

    def learn_spell(self, spell: Spell) -> None:
        """Add a spell to the character's repertoire."""
        self.spells[spell.name] = spell

    def add_spell_mastery(self, spell_name: str, points: int) -> None:
        """Add or update spell mastery."""
        if spell_name not in self.spells:
            raise ValueError(f"Spell {spell_name} not in repertoire")
            
        self.mastered_spells[spell_name] = points
        self.spells[spell_name].mastery_level = points

    def get_casting_total(self, technique: Technique, form: Form) -> int:
        """Calculate casting total for a technique + form combination."""
        technique_score = self.techniques.get(technique, 0)
        form_score = self.forms.get(form, 0)
        stamina_bonus = max(0, self.characteristics.get('Stamina', 0))
        
        return technique_score + form_score + stamina_bonus

    def get_magic_resistance(self, against_technique: Optional[Technique] = None) -> int:
        """Calculate total magic resistance."""
        base_resistance = self.magic_resistance
        
        # Add Form resistance if applicable
        if against_technique:
            form_score = self.forms.get(Form.VIM, 0)
            base_resistance += form_score
            
        return base_resistance

    def to_dict(self) -> dict:
        """Convert magus to dictionary for saving."""
        base_dict = super().to_dict()
        magic_dict = {
            "house": self.house.value,
            "parma_magica": self.parma_magica,
            "magic_resistance": self.magic_resistance,
            "warping_score": self.warping_score,
            "warping_points": self.warping_points,
            "techniques": {tech.value: score for tech, score in self.techniques.items()},
            "forms": {form.value: score for form, score in self.forms.items()},
            "spells": {name: spell.to_dict() for name, spell in self.spells.items()},
            "mastered_spells": self.mastered_spells
        }
        return {**base_dict, **magic_dict}

    @classmethod
    def from_dict(cls, data: dict) -> "Magus":
        """Create magus from dictionary data."""
        # Convert string keys back to enums
        techniques = {Technique(key): value for key, value in data.get("techniques", {}).items()}
        forms = {Form(key): value for key, value in data.get("forms", {}).items()}
        
        # Create spells
        spells = {
            name: Spell.from_dict(spell_data) 
            for name, spell_data in data.get("spells", {}).items()
        }
        
        # Create base character first
        base_char = super().from_dict(data)
        
        return cls(
            **{k: v for k, v in base_char.__dict__.items()},
            house=House(data["house"]),
            parma_magica=data.get("parma_magica", 0),
            magic_resistance=data.get("magic_resistance", 0),
            warping_score=data.get("warping_score", 0),
            warping_points=data.get("warping_points", 0),
            techniques=techniques,
            forms=forms,
            spells=spells,
            mastered_spells=data.get("mastered_spells", {})
        ) 

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
