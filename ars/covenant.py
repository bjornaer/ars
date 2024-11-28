from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ars.events import EventRecorder, EventType
from ars.core.types import Season
from ars.serialization import Serializable
from ars.core.types import Form


class CovenantSize(Enum):
    """Size categories for covenants."""

    SMALL = "Small"  # Summer covenant
    MEDIUM = "Medium"  # Autumn covenant
    LARGE = "Large"  # Winter covenant
    GRAND = "Grand"  # Ancient covenant


class BuildingType(Enum):
    """Types of covenant buildings."""

    LIVING_QUARTERS = "Living Quarters"
    LIBRARY = "Library"
    LABORATORY = "Laboratory"
    COUNCIL_CHAMBER = "Council Chamber"
    CHAPEL = "Chapel"
    STORAGE = "Storage"
    KITCHEN = "Kitchen"
    GUEST_HOUSE = "Guest House"
    TOWER = "Tower"
    WALL = "Wall"
    GATE = "Gate"


@dataclass
class Building(Serializable):
    """A building within the covenant."""

    type: BuildingType
    name: str
    size: int
    quality: int
    description: str = ""
    occupants: List[str] = field(default_factory=list)
    maintenance_cost: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Building":
        data["type"] = BuildingType(data["type"])
        return cls(**data)


@dataclass
class Library(Serializable):
    """The covenant's library."""

    books: Dict[str, int] = field(default_factory=dict)  # Book name -> level
    summa: Dict[str, Dict[str, int]] = field(default_factory=dict)  # Art -> {level, quality}
    tractatus: Dict[str, List[str]] = field(default_factory=dict)  # Art -> list of tractatus
    capacity: int = 100
    organization: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Library":
        return cls(**data)


@dataclass
class VisSource(Serializable):
    """A source of vis."""

    name: str
    form: Form
    amount: int
    season: str
    description: str
    claimed: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisSource":
        data["form"] = Form(data["form"])
        return cls(**data)


@dataclass
class Covenant(Serializable, EventRecorder):
    """Represents a covenant in Ars Magica."""

    name: str
    size: CovenantSize
    age: int

    # Resources
    buildings: List[Building] = field(default_factory=list)
    library: Library = field(default_factory=Library)
    vis_sources: List[VisSource] = field(default_factory=list)

    # Characteristics
    aura: int = 3  # base aura
    vis_stocks: Dict[Form, int] = field(default_factory=lambda: {form: 0 for form in Form})
    aura_properties: List[str] = field(default_factory=list)
    aura_modifiers: Dict[str, int] = field(default_factory=dict)

    # Population
    magi: List[str] = field(default_factory=list)
    covenfolk: int = 0
    grogs: int = 0

    # Economics
    income: int = 0
    expenses: int = 0

    def __post_init__(self):
        """Ensure proper enum types after initialization."""
        super().__init__()
        if isinstance(self.size, str):
            self.size = CovenantSize(self.size)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Covenant":
        # Convert size to enum
        data["size"] = CovenantSize(data["size"])

        # Convert buildings
        data["buildings"] = [Building.from_dict(b) for b in data["buildings"]]

        # Convert library
        data["library"] = Library.from_dict(data["library"])

        # Convert vis sources
        data["vis_sources"] = [VisSource.from_dict(v) for v in data["vis_sources"]]

        # Convert vis stocks
        data["vis_stocks"] = {Form(k): v for k, v in data["vis_stocks"].items()}

        return cls(**data)

    def add_building(self, building: Building, year: Optional[int] = None, season: Optional[Season] = None) -> None:
        """Add a new building to the covenant."""
        self.buildings.append(building)
        self.expenses += building.maintenance_cost

        if self.event_manager:
            self.record_event(
                type=EventType.COVENANT_CHANGE,
                description=f"New building added: {building.name} ({building.type.value})",
                details={
                    "building_type": building.type.value,
                    "building_name": building.name,
                    "size": building.size,
                    "quality": building.quality,
                    "maintenance_cost": building.maintenance_cost,
                    "new_total_expenses": self.expenses,
                },
                year=year,
                season=season,
            )

    def add_vis_source(self, source: VisSource, year: Optional[int] = None, season: Optional[Season] = None) -> None:
        """Add a new vis source to the covenant."""
        self.vis_sources.append(source)

        if self.event_manager:
            self.record_event(
                type=EventType.VIS_COLLECTION,
                description=f"New vis source discovered: {source.name}",
                details={
                    "source_name": source.name,
                    "form": source.form.value,
                    "amount": source.amount,
                    "season": source.season,
                    "description": source.description,
                },
                year=year,
                season=season,
            )

    def collect_vis(self, season: str, year: Optional[int] = None) -> Dict[Form, int]:
        """Collect vis from available sources for the given season."""
        collected = {form: 0 for form in Form}

        for source in self.vis_sources:
            if source.season == season and not source.claimed:
                collected[source.form] += source.amount
                source.claimed = True
                self.vis_stocks[source.form] += source.amount

                if self.event_manager:
                    self.record_event(
                        type=EventType.VIS_COLLECTION,
                        description=f"Collected vis from {source.name}",
                        details={
                            "source": source.name,
                            "form": source.form.value,
                            "amount": source.amount,
                            "new_stock": self.vis_stocks[source.form],
                        },
                        year=year,
                        season=Season.from_string(season),
                    )

        return collected

    def add_book(self, name: str, level: int, year: Optional[int] = None, season: Optional[Season] = None) -> None:
        """Add a book to the library."""
        if len(self.library.books) < self.library.capacity:
            self.library.books[name] = level

            if self.event_manager:
                self.record_event(
                    type=EventType.COVENANT_CHANGE,
                    description=f"New book added to library: {name}",
                    details={
                        "book_name": name,
                        "level": level,
                        "library_size": len(self.library.books),
                        "remaining_capacity": self.library.capacity - len(self.library.books),
                    },
                    year=year,
                    season=season,
                )
        else:
            raise ValueError("Library capacity reached")

    def add_magus(self, name: str, year: Optional[int] = None, season: Optional[Season] = None) -> None:
        """Add a magus to the covenant."""
        if name not in self.magi:
            self.magi.append(name)

            if self.event_manager:
                self.record_event(
                    type=EventType.COVENANT_CHANGE,
                    description=f"New magus joined: {name}",
                    details={"magus_name": name, "total_magi": len(self.magi)},
                    year=year,
                    season=season,
                )

    def remove_magus(
        self, name: str, reason: str = "departed", year: Optional[int] = None, season: Optional[Season] = None
    ) -> None:
        """Remove a magus from the covenant."""
        if name in self.magi:
            self.magi.remove(name)

            if self.event_manager:
                self.record_event(
                    type=EventType.COVENANT_CHANGE,
                    description=f"Magus {reason}: {name}",
                    details={"magus_name": name, "reason": reason, "total_magi": len(self.magi)},
                    year=year,
                    season=season,
                )

    def calculate_income(self) -> int:
        """Calculate seasonal income."""
        return self.income

    def calculate_expenses(self) -> int:
        """Calculate seasonal expenses."""
        total = self.expenses
        for building in self.buildings:
            total += building.maintenance_cost
        return total

    def apply_aura_effects(self, effects: Dict[str, int]) -> None:
        """Apply aura effects to covenant."""
        for activity, modifier in effects.items():
            if activity == "magical_activities":
                self.aura = max(0, self.aura + modifier)
            elif activity == "vis_extraction":
                for source in self.vis_sources:
                    source.amount = max(1, source.amount + modifier)
