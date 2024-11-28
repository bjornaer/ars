from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ars.events import EventType, GameEvent
from ars.core.types import Season
from ars.core.types import Form
from ars.vis_aura import VisManager


def vis_transfer_message(amount: int, form: Form, source_name: str, destination_name: str):
    return f"Transferred {amount} pawns of {form.value} vis from {source_name} to {destination_name}"


@dataclass
class VisTransaction:
    """Represents a vis transaction (collection, use, or transfer)."""

    form: Form
    amount: int
    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    season: Season = Season.SPRING
    year: int = 1220


class EnhancedVisManager(VisManager):
    """Enhanced vis management with event tracking and detailed transactions."""

    def __init__(self, event_manager=None):
        super().__init__()
        self.event_manager = event_manager
        self.transactions: List[VisTransaction] = []
        self.reserved_vis: Dict[str, Dict[Form, int]] = {}  # Tracks vis reserved for specific purposes

    def collect_vis(
        self, source_name: str, year: int, season: str, aura_strength: int = 0, collector: Optional[str] = None
    ) -> Tuple[Form, int]:
        """Enhanced vis collection with event tracking."""
        form, amount = super().collect_vis(source_name, year, season, aura_strength)

        if amount > 0:
            # Record transaction
            transaction = VisTransaction(
                form=form,
                amount=amount,
                source=source_name,
                destination="covenant_stocks",
                season=Season(season),
                year=year,
            )
            self.transactions.append(transaction)

            # Create event
            if self.event_manager:
                event = GameEvent(
                    type=EventType.VIS_COLLECTION,
                    season=Season(season),
                    year=year,
                    description=f"Collected {amount} pawns of {form.value} vis from {source_name}",
                    details={
                        "form": form.value,
                        "amount": amount,
                        "source": source_name,
                        "collector": collector,
                        "aura_strength": aura_strength,
                    },
                )
                self.event_manager.add_event(event)

        return form, amount

    def reserve_vis(self, purpose: str, form: Form, amount: int, character: Optional[str] = None) -> bool:
        """Reserve vis for a specific purpose."""
        if self.stocks[form] >= amount:
            if purpose not in self.reserved_vis:
                self.reserved_vis[purpose] = {}

            self.reserved_vis[purpose][form] = self.reserved_vis[purpose].get(form, 0) + amount
            self.stocks[form] -= amount

            if self.event_manager:
                event = GameEvent(
                    type=EventType.VIS_RESERVATION,
                    description=f"Reserved {amount} pawns of {form.value} vis for {purpose}",
                    details={"form": form.value, "amount": amount, "purpose": purpose, "character": character},
                )
                self.event_manager.add_event(event)

            return True
        return False

    def use_reserved_vis(self, purpose: str, form: Form, amount: int, character: Optional[str] = None) -> bool:
        """Use previously reserved vis."""
        if (
            purpose in self.reserved_vis
            and form in self.reserved_vis[purpose]
            and self.reserved_vis[purpose][form] >= amount
        ):

            self.reserved_vis[purpose][form] -= amount
            if self.reserved_vis[purpose][form] == 0:
                del self.reserved_vis[purpose][form]
                if not self.reserved_vis[purpose]:
                    del self.reserved_vis[purpose]

            if self.event_manager:
                event = GameEvent(
                    type=EventType.VIS_USAGE,
                    description=f"Used {amount} pawns of {form.value} vis for {purpose}",
                    details={"form": form.value, "amount": amount, "purpose": purpose, "character": character},
                )
                self.event_manager.add_event(event)

            return True
        return False

    def transfer_vis(
        self,
        form: Form,
        amount: int,
        target_manager: "EnhancedVisManager",
        source_name: str = "covenant_stocks",
        destination_name: str = "personal_stocks",
    ) -> bool:
        """Enhanced vis transfer with tracking."""
        if super().transfer_vis(form, amount, target_manager):
            transaction = VisTransaction(form=form, amount=amount, source=source_name, destination=destination_name)
            self.transactions.append(transaction)

            if self.event_manager:
                event = GameEvent(
                    type=EventType.VIS_TRANSFER,
                    description=vis_transfer_message(amount, form, source_name, destination_name),
                    details={
                        "form": form.value,
                        "amount": amount,
                        "source": source_name,
                        "destination": destination_name,
                    },
                )
                self.event_manager.add_event(event)

            return True
        return False

    def get_available_vis(self, form: Form) -> int:
        """Get amount of available (unreserved) vis."""
        reserved = sum(stocks.get(form, 0) for stocks in self.reserved_vis.values())
        return self.stocks[form] - reserved

    def get_transactions(
        self, form: Optional[Form] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[VisTransaction]:
        """Get filtered transactions."""
        transactions = self.transactions

        if form:
            transactions = [t for t in transactions if t.form == form]
        if start_date:
            transactions = [t for t in transactions if t.timestamp >= start_date]
        if end_date:
            transactions = [t for t in transactions if t.timestamp <= end_date]

        return transactions
