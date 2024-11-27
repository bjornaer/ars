from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ars.types import Form
from ars.vis_aura import VisSource


class ResourceCategory(Enum):
    """Categories of covenant resources."""

    MUNDANE = "Mundane"
    MAGICAL = "Magical"
    BOOKS = "Books"
    PERSONNEL = "Personnel"
    INFRASTRUCTURE = "Infrastructure"


@dataclass
class Resource:
    """Base class for covenant resources."""

    name: str
    category: ResourceCategory
    quality: int
    maintenance_cost: float = 0.0
    condition: int = 100  # Percentage
    notes: str = ""


@dataclass
class MundaneResource(Resource):
    """Mundane resources like buildings, tools, etc."""

    size: int = 1
    resource_type: str = "tools"
    workers_required: int = 0


@dataclass
class MagicalResource(Resource):
    """Magical resources like enchanted items, aura features."""

    magical_bonus: int = 0
    form: Optional[Form] = None
    charges: Optional[int] = None


@dataclass
class Book(Resource):
    """Books and lab texts."""

    level: int = 1
    subject: str = ""
    author: str = ""
    copies: int = 1


@dataclass
class Personnel(Resource):
    """Covenant staff and specialists."""

    role: str = ""
    abilities: Dict[str, int] = field(default_factory=dict)
    salary: float = 0.0
    loyalty: int = 50  # Percentage


@dataclass
class BuildingProject:
    """A construction or improvement project."""

    building_type: str = "tower"
    name: str = ""
    cost: float = 0.0
    seasons_required: int = 0
    seasons_completed: int = 0
    workers_assigned: int = 0
    resources_committed: Dict[str, int] = field(default_factory=dict)
    status: str = "Not Started"


class CovenantEconomy:
    """Manages covenant economics and resources."""

    def __init__(self, covenant_name: str):
        self.covenant_name = covenant_name
        self.resources: Dict[str, Resource] = {}
        self.income_sources: Dict[str, float] = {}
        self.expenses: Dict[str, float] = {}
        self.projects: Dict[str, BuildingProject] = {}
        self.treasury: float = 0.0
        self.stored_vis: Dict[Form, int] = {}
        self.vis_sources: List[VisSource] = []

    def add_resource(self, resource: Resource) -> bool:
        """Add a new resource to the covenant."""
        if resource.name in self.resources:
            return False
        self.resources[resource.name] = resource
        return True

    def remove_resource(self, resource_name: str) -> Optional[Resource]:
        """Remove a resource from the covenant."""
        return self.resources.pop(resource_name, None)

    def add_income_source(self, name: str, amount: float) -> None:
        """Add a new income source."""
        self.income_sources[name] = amount

    def add_expense(self, name: str, amount: float) -> None:
        """Add a new expense."""
        self.expenses[name] = amount

    def start_project(self, project: BuildingProject) -> bool:
        """Start a new building project."""
        if project.name in self.projects:
            return False

        if project.cost > self.treasury:
            return False

        self.projects[project.name] = project
        self.treasury -= project.cost
        project.status = "In Progress"
        return True

    def process_season(self, season: str) -> Dict[str, Any]:
        """Process economic activities for a season."""
        return {
            "income": self._process_income(season),
            "expenses": self._process_expenses(season),
            "projects": self._process_projects(season),
            "maintenance": self._process_maintenance(season),
        }

    def _process_income(self, season: str) -> Dict[str, int]:
        """Process seasonal income from various sources."""
        income = {}
        for source in self.income_sources:
            if source.season == season or source.season == "Any":
                income[source.name] = source.generate_income()
        return income

    def _process_expenses(self, season: str) -> Dict[str, int]:
        """Process seasonal expenses."""
        expenses = {}
        for expense in self.expenses:
            if expense.season == season or expense.season == "Any":
                expenses[expense.name] = expense.calculate_cost()
        return expenses

    def _process_projects(self, season: str) -> Dict[str, Any]:
        """Process ongoing building and improvement projects."""
        results = {}
        for project in self.active_projects:
            progress = project.advance_season()
            results[project.name] = {
                "progress": progress,
                "completed": project.is_completed(),
                "resources_used": project.resources_consumed,
            }
        return results

    def _process_maintenance(self, season: str) -> Dict[str, Any]:
        """Process maintenance activities."""
        maintenance = {}
        for building in self.buildings:
            cost = building.calculate_maintenance(season)
            if cost > 0:
                maintenance[building.name] = {
                    "cost": cost,
                    "condition": building.condition,
                    "repairs_needed": building.needs_repairs(),
                }
        return maintenance

    def _calculate_deterioration(self, resource: MundaneResource, season: str) -> int:
        """Calculate resource deterioration."""
        base_deterioration = 1

        # Season effects
        season_modifiers = {"Winter": 2, "Spring": 0, "Summer": 1, "Autumn": 1}
        base_deterioration *= season_modifiers.get(season, 1)

        # Size effects
        base_deterioration += resource.size // 2

        # Worker effects
        if resource.workers_required > 0:
            worker_ratio = min(resource.workers_required, self._get_available_workers()) / resource.workers_required
            base_deterioration = int(base_deterioration * (2 - worker_ratio))

        return base_deterioration

    def _check_project_requirements(self, project: BuildingProject) -> bool:
        """Check if project requirements are met."""
        # Check workers
        if project.workers_assigned < project.workers_required:
            return False

        # Check resources
        for resource, _ in project.resources_committed.items():
            if resource not in self.resources:
                return False
            if isinstance(self.resources[resource], MundaneResource):
                if self.resources[resource].condition < 50:
                    return False

        return True

    def _complete_project(self, project: BuildingProject) -> None:
        """Complete a building project."""
        project.status = "Completed"

        # Create new resource from project
        new_resource = MundaneResource(
            name=project.name,
            category=ResourceCategory.INFRASTRUCTURE,
            quality=10,  # Base quality
            resource_type=project.building_type,
            size=3,  # Default size
            workers_required=project.workers_assigned,
        )

        self.add_resource(new_resource)

    def _get_available_workers(self) -> int:
        """Get number of available workers."""
        return sum(1 for r in self.resources.values() if isinstance(r, Personnel) and r.role == "worker")

    def save_state(self, filepath: Path) -> None:
        """Save economic state."""
        data = {
            "covenant_name": self.covenant_name,
            "treasury": self.treasury,
            "resources": {name: self._serialize_resource(resource) for name, resource in self.resources.items()},
            "income_sources": self.income_sources,
            "expenses": self.expenses,
            "projects": {
                name: {
                    "name": project.name,
                    "type": project.building_type,
                    "cost": project.cost,
                    "seasons_required": project.seasons_required,
                    "seasons_completed": project.seasons_completed,
                    "workers_assigned": project.workers_assigned,
                    "resources_committed": project.resources_committed,
                    "status": project.status,
                }
                for name, project in self.projects.items()
            },
            "stored_vis": {form.value: amount for form, amount in self.stored_vis.items()},
        }

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load_state(cls, filepath: Path) -> "CovenantEconomy":
        """Load economic state."""
        with filepath.open("r") as f:
            data = yaml.safe_load(f)

        economy = cls(data["covenant_name"])
        economy.treasury = data["treasury"]
        economy.income_sources = data["income_sources"]
        economy.expenses = data["expenses"]

        # Load resources
        for name, res_data in data["resources"].items():
            economy.resources[name] = cls._deserialize_resource(res_data)

        # Load projects
        for name, proj_data in data["projects"].items():
            project = BuildingProject(
                name=proj_data["name"],
                building_type=proj_data["type"],
                cost=proj_data["cost"],
                seasons_required=proj_data["seasons_required"],
                seasons_completed=proj_data["seasons_completed"],
                workers_assigned=proj_data["workers_assigned"],
                resources_committed=proj_data["resources_committed"],
                status=proj_data["status"],
            )
            economy.projects[name] = project

        # Load stored vis
        economy.stored_vis = {Form(form): amount for form, amount in data["stored_vis"].items()}

        return economy

    @staticmethod
    def _serialize_resource(resource: Resource) -> Dict:
        """Serialize a resource to dictionary."""
        data = {
            "type": resource.__class__.__name__,
            "name": resource.name,
            "category": resource.category.value,
            "quality": resource.quality,
            "maintenance_cost": resource.maintenance_cost,
            "condition": resource.condition,
            "notes": resource.notes,
        }

        if isinstance(resource, MundaneResource):
            data.update(
                {
                    "resource_type": resource.resource_type,
                    "size": resource.size,
                    "workers_required": resource.workers_required,
                }
            )
        elif isinstance(resource, MagicalResource):
            data.update(
                {
                    "magical_bonus": resource.magical_bonus,
                    "form": resource.form.value if resource.form else None,
                    "charges": resource.charges,
                }
            )
        elif isinstance(resource, Book):
            data.update(
                {
                    "level": resource.level,
                    "subject": resource.subject,
                    "author": resource.author,
                    "copies": resource.copies,
                }
            )
        elif isinstance(resource, Personnel):
            data.update(
                {
                    "role": resource.role,
                    "abilities": resource.abilities,
                    "salary": resource.salary,
                    "loyalty": resource.loyalty,
                }
            )

        return data

    @staticmethod
    def _deserialize_resource(data: Dict) -> Resource:
        """Deserialize a resource from dictionary."""
        base_args = {
            "name": data["name"],
            "category": ResourceCategory(data["category"]),
            "quality": data["quality"],
            "maintenance_cost": data["maintenance_cost"],
            "condition": data["condition"],
            "notes": data["notes"],
        }

        if data["type"] == "MundaneResource":
            return MundaneResource(
                **base_args,
                resource_type=data["resource_type"],
                size=data["size"],
                workers_required=data["workers_required"],
            )
        elif data["type"] == "MagicalResource":
            return MagicalResource(
                **base_args,
                magical_bonus=data["magical_bonus"],
                form=Form(data["form"]) if data["form"] else None,
                charges=data["charges"],
            )
        elif data["type"] == "Book":
            return Book(
                **base_args, level=data["level"], subject=data["subject"], author=data["author"], copies=data["copies"]
            )
        elif data["type"] == "Personnel":
            return Personnel(
                **base_args,
                role=data["role"],
                abilities=data["abilities"],
                salary=data["salary"],
                loyalty=data["loyalty"],
            )

        raise ValueError(f"Unknown resource type: {data['type']}")
