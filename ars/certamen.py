from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ars.character import Character

from .dice import DiceRoller
from .events import EventRecorder, EventType
from ars.core.types import Season
from .core.types import Form, Technique


class CertamenStage(Enum):
    OPENING = "Opening"
    EXCHANGE = "Exchange"
    RESOLUTION = "Resolution"


@dataclass
class CertamenResult:
    winner: str
    loser: str
    winning_score: int
    losing_score: int
    rounds: int
    fatigue_costs: Dict[str, int]
    warping_gained: Dict[str, int]
    details: List[str]


class CertamenManager(EventRecorder):
    """Manages magical duels (Certamen)."""

    def __init__(self, event_manager=None):
        super().__init__(event_manager)
        self.current_stage = CertamenStage.OPENING
        self.rounds_completed = 0
        self.scores: Dict[str, int] = {}
        self.techniques_used: Dict[str, Technique] = {}
        self.forms_used: Dict[str, Form] = {}
        self.fatigue_costs: Dict[str, int] = {}

    def initiate_certamen(
        self,
        challenger: "Character",
        defender: "Character",
        technique: Technique,
        form: Form,
        year: Optional[int] = None,
        season: Optional[Season] = None,
    ) -> Dict[str, any]:
        """Initiate a Certamen contest."""
        self.scores = {challenger.name: 0, defender.name: 0}
        self.techniques_used = {challenger.name: technique}
        self.forms_used = {challenger.name: form}
        self.fatigue_costs = {challenger.name: 0, defender.name: 0}

        # Record initiation
        if self.event_manager:
            self.record_event(
                type=EventType.CERTAMEN,
                description=f"Certamen initiated: {challenger.name} vs {defender.name}",
                details={
                    "challenger": challenger.name,
                    "defender": defender.name,
                    "technique": technique.value,
                    "form": form.value,
                    "stage": CertamenStage.OPENING.value,
                },
                year=year,
                season=season,
            )

        return {
            "stage": CertamenStage.OPENING,
            "challenger": challenger.name,
            "defender": defender.name,
            "technique": technique,
            "form": form,
        }

    def respond_to_challenge(self, defender: "Character", technique: Technique, form: Form) -> Dict[str, any]:
        """Defender chooses their Arts for the contest."""
        self.techniques_used[defender.name] = technique
        self.forms_used[defender.name] = form
        self.current_stage = CertamenStage.EXCHANGE

        return {"stage": self.current_stage, "technique": technique, "form": form}

    def resolve_exchange(
        self, character1: "Character", character2: "Character", modifiers: Dict[str, int] = None
    ) -> Dict[str, any]:
        """Resolve one exchange of the Certamen."""
        modifiers = modifiers or {}

        # Calculate totals for each character
        results = {}
        for char in [character1, character2]:
            technique_score = char.techniques[self.techniques_used[char.name].value]
            form_score = char.forms[self.forms_used[char.name].value]

            roll = DiceRoller.stress_die()
            total = roll.total + technique_score + form_score + modifiers.get(char.name, 0)

            # Apply fatigue
            fatigue_cost = max(1, (technique_score + form_score) // 10)
            self.fatigue_costs[char.name] += fatigue_cost
            char.add_fatigue(fatigue_cost)

            results[char.name] = {"roll": roll, "total": total, "fatigue_cost": fatigue_cost}

            # Update scores
            self.scores[char.name] += total

        self.rounds_completed += 1

        # Check for victory
        victor = None
        if abs(self.scores[character1.name] - self.scores[character2.name]) >= 10:
            self.current_stage = CertamenStage.RESOLUTION
            victor = character1.name if self.scores[character1.name] > self.scores[character2.name] else character2.name

        return {"results": results, "scores": self.scores.copy(), "stage": self.current_stage, "victor": victor}

    def end_certamen(
        self,
        character1: "Character",
        character2: "Character",
        year: Optional[int] = None,
        season: Optional[Season] = None,
    ) -> CertamenResult:
        """End the Certamen and determine final results."""
        winner = character1.name if self.scores[character1.name] > self.scores[character2.name] else character2.name
        loser = character2.name if winner == character1.name else character1.name

        # Calculate warping
        warping = {character1.name: self.rounds_completed // 5, character2.name: self.rounds_completed // 5}

        # Apply warping
        for char in [character1, character2]:
            if warping[char.name] > 0:
                char.add_warping(warping[char.name])

        result = CertamenResult(
            winner=winner,
            loser=loser,
            winning_score=self.scores[winner],
            losing_score=self.scores[loser],
            rounds=self.rounds_completed,
            fatigue_costs=self.fatigue_costs.copy(),
            warping_gained=warping,
            details=[
                f"Contest lasted {self.rounds_completed} rounds",
                f"Final score - {winner}: {self.scores[winner]}, {loser}: {self.scores[loser]}",
                f"Fatigue costs - {winner}: {self.fatigue_costs[winner]}, {loser}: {self.fatigue_costs[loser]}",
                f"Warping gained - {winner}: {warping[winner]}, {loser}: {warping[loser]}",
            ],
        )

        # Record final result
        if self.event_manager:
            self.record_event(
                type=EventType.CERTAMEN,
                description=f"Certamen concluded: {winner} defeats {loser}",
                details={
                    "winner": winner,
                    "loser": loser,
                    "rounds": self.rounds_completed,
                    "final_scores": self.scores,
                    "fatigue_costs": self.fatigue_costs,
                    "warping_gained": warping,
                },
                year=year,
                season=season,
            )

        return result
