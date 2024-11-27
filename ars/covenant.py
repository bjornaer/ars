from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List

import yaml

from .types import Form


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
class Building:
    """A building within the covenant."""

    type: BuildingType
    name: str
    size: int
    quality: int
    description: str = ""
    occupants: List[str] = field(default_factory=list)
    maintenance_cost: int = 0


@dataclass
class Library:
    """The covenant's library."""

    books: Dict[str, int] = field(default_factory=dict)  # Book name -> level
    summa: Dict[str, Dict[str, int]] = field(default_factory=dict)  # Art -> {level, quality}
    tractatus: Dict[str, List[str]] = field(default_factory=dict)  # Art -> list of tractatus
    capacity: int = 100
    organization: int = 0


@dataclass
class VisSource:
    """A source of vis."""

    name: str
    form: Form
    amount: int
    season: str
    description: str
    claimed: bool = False


@dataclass
class Covenant:
    """Represents a covenant in Ars Magica."""

    name: str
    size: CovenantSize
    age: int

    # Resources
    buildings: List[Building] = field(default_factory=list)
    library: Library = field(default_factory=Library)
    vis_sources: List[VisSource] = field(default_factory=list)

    # Characteristics
    aura: int = 3
    vis_stocks: Dict[Form, int] = field(default_factory=lambda: {form: 0 for form in Form})

    # Population
    magi: List[str] = field(default_factory=list)
    covenfolk: int = 0
    grogs: int = 0

    # Economics
    income: int = 0
    expenses: int = 0

    def add_building(self, building: Building) -> None:
        """Add a new building to the covenant."""
        self.buildings.append(building)
        self.expenses += building.maintenance_cost

    def add_vis_source(self, source: VisSource) -> None:
        """Add a new vis source to the covenant."""
        self.vis_sources.append(source)

    def collect_vis(self, season: str) -> Dict[Form, int]:
        """Collect vis from available sources for the given season."""
        collected = {form: 0 for form in Form}

        for source in self.vis_sources:
            if source.season == season and not source.claimed:
                collected[source.form] += source.amount
                source.claimed = True
                self.vis_stocks[source.form] += source.amount

        return collected

    def add_book(self, name: str, level: int) -> None:
        """Add a book to the library."""
        if len(self.library.books) < self.library.capacity:
            self.library.books[name] = level
        else:
            raise ValueError("Library capacity reached")

    def calculate_income(self) -> int:
        """Calculate seasonal income."""
        # Basic implementation - can be expanded
        return self.income

    def calculate_expenses(self) -> int:
        """Calculate seasonal expenses."""
        total = self.expenses
        # Add maintenance costs
        for building in self.buildings:
            total += building.maintenance_cost
        return total

    def save(self, directory: Path = Path("ars/data/covenants")) -> None:
        """Save covenant to file."""
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / f"{self.name.lower().replace(' ', '_')}.yml"

        # Convert data for YAML
        data = {
            "name": self.name,
            "size": self.size.value,
            "age": self.age,
            "buildings": [
                {
                    "type": b.type.value,
                    "name": b.name,
                    "size": b.size,
                    "quality": b.quality,
                    "description": b.description,
                    "occupants": b.occupants,
                    "maintenance_cost": b.maintenance_cost,
                }
                for b in self.buildings
            ],
            "library": {
                "books": self.library.books,
                "summa": self.library.summa,
                "tractatus": self.library.tractatus,
                "capacity": self.library.capacity,
                "organization": self.library.organization,
            },
            "vis_sources": [
                {
                    "name": v.name,
                    "form": v.form.value,
                    "amount": v.amount,
                    "season": v.season,
                    "description": v.description,
                    "claimed": v.claimed,
                }
                for v in self.vis_sources
            ],
            "aura": self.aura,
            "vis_stocks": {k.value: v for k, v in self.vis_stocks.items()},
            "magi": self.magi,
            "covenfolk": self.covenfolk,
            "grogs": self.grogs,
            "income": self.income,
            "expenses": self.expenses,
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load(cls, name: str, directory: Path = Path("ars/data/covenants")) -> "Covenant":
        """Load covenant from file."""
        filepath = directory / f"{name.lower().replace(' ', '_')}.yml"

        with filepath.open("r") as f:
            data = yaml.safe_load(f)

            # Convert data back to objects
            data["size"] = CovenantSize(data["size"])

            # Convert buildings
            buildings = []
            for b in data["buildings"]:
                buildings.append(
                    Building(
                        type=BuildingType(b["type"]),
                        name=b["name"],
                        size=b["size"],
                        quality=b["quality"],
                        description=b["description"],
                        occupants=b["occupants"],
                        maintenance_cost=b["maintenance_cost"],
                    )
                )
            data["buildings"] = buildings

            # Convert library
            data["library"] = Library(**data["library"])

            # Convert vis sources
            vis_sources = []
            for v in data["vis_sources"]:
                vis_sources.append(
                    VisSource(
                        name=v["name"],
                        form=Form(v["form"]),
                        amount=v["amount"],
                        season=v["season"],
                        description=v["description"],
                        claimed=v["claimed"],
                    )
                )
            data["vis_sources"] = vis_sources

            # Convert vis stocks
            data["vis_stocks"] = {Form(k): v for k, v in data["vis_stocks"].items()}

            return cls(**data)
