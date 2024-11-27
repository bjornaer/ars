from dataclasses import dataclass

from .character import Character
from .laboratory import Laboratory
from .types import Form, Technique


@dataclass
class LabActivity:
    """Base class for laboratory activities."""

    name: str
    season: int
    year: int
    magus: Character
    laboratory: Laboratory

    def calculate_lab_total(self, technique: Technique, form: Form) -> int:
        """Calculate total for lab activity."""
        art_score = self.magus.techniques[technique.value] + self.magus.forms[form.value]
        lab_bonus = self.laboratory.calculate_total_bonus(technique, form)
        return art_score + lab_bonus


class VisExtraction(LabActivity):
    """Vis extraction activity."""

    def execute(self, source_form: Form) -> int:
        """Perform vis extraction."""
        lab_total = self.calculate_lab_total(Technique.CREO, source_form)
        return lab_total // 10  # Basic vis extraction rules


class ItemEnchantment(LabActivity):
    """Enchant magical items."""

    def execute(self, technique: Technique, form: Form, effect_level: int) -> bool:
        """Attempt to enchant an item."""
        lab_total = self.calculate_lab_total(technique, form)
        return lab_total >= effect_level


class LongevityRitual(LabActivity):
    """Create or improve longevity ritual."""

    def execute(self) -> int:
        """Create longevity ritual."""
        lab_total = self.calculate_lab_total(Technique.CREO, Form.CORPUS)
        return lab_total  # Returns ritual strength
