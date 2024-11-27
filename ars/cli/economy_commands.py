from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ars.covenant_economy import (
    Book,
    BuildingProject,
    CovenantEconomy,
    MagicalResource,
    MundaneResource,
    Personnel,
    ResourceCategory,
)
from ars.types import Form

console = Console()


@click.group()
def economy():
    """Covenant economy and resource management commands."""
    pass


@economy.command()
@click.argument("covenant_name")
@click.option("--treasury", "-t", type=float, default=0.0, help="Initial treasury amount")
def initialize(covenant_name: str, treasury: float):
    """Initialize covenant economy system."""
    try:
        economy = CovenantEconomy(covenant_name)
        economy.treasury = treasury
        economy.save_state(Path(f"ars/data/economy_{covenant_name}.yml"))
        console.print(f"[green]Initialized economy for {covenant_name} " f"with {treasury} treasury[/green]")
    except Exception as e:
        console.print(f"[red]Error initializing economy: {e}[/red]")


@economy.command()
@click.argument("covenant_name")
@click.argument("name")
@click.option("--type", "-t", "res_type", type=click.Choice(["mundane", "magical", "book", "personnel"]), required=True)
@click.option("--category", "-c", type=click.Choice([c.value for c in ResourceCategory]), required=True)
@click.option("--quality", "-q", type=int, default=5)
@click.option("--maintenance", "-m", type=float, default=0.0)
def add_resource(covenant_name: str, name: str, res_type: str, category: str, quality: int, maintenance: float):
    """Add a new resource to the covenant."""
    try:
        economy = CovenantEconomy.load_state(Path(f"ars/data/economy_{covenant_name}.yml"))

        # Get base resource details
        if Confirm.ask("Add resource details?"):
            details = _get_resource_details(res_type)
        else:
            details = {}

        # Create appropriate resource type
        if res_type == "mundane":
            resource = MundaneResource(
                name=name,
                category=ResourceCategory(category),
                quality=quality,
                maintenance_cost=maintenance,
                resource_type=details.get("type", "generic"),
                size=details.get("size", 1),
                workers_required=details.get("workers", 0),
            )
        elif res_type == "magical":
            resource = MagicalResource(
                name=name,
                category=ResourceCategory(category),
                quality=quality,
                maintenance_cost=maintenance,
                magical_bonus=details.get("bonus", 0),
                form=Form(details.get("form")) if details.get("form") else None,
                charges=details.get("charges"),
            )
        elif res_type == "book":
            resource = Book(
                name=name,
                category=ResourceCategory(category),
                quality=quality,
                maintenance_cost=maintenance,
                level=details.get("level", 1),
                subject=details.get("subject", ""),
                author=details.get("author", ""),
                copies=details.get("copies", 1),
            )
        elif res_type == "personnel":
            resource = Personnel(
                name=name,
                category=ResourceCategory(category),
                quality=quality,
                maintenance_cost=maintenance,
                role=details.get("role", "worker"),
                abilities=details.get("abilities", {}),
                salary=details.get("salary", 0.0),
                loyalty=details.get("loyalty", 50),
            )

        if economy.add_resource(resource):
            economy.save_state(Path(f"ars/data/economy_{covenant_name}.yml"))
            console.print(f"[green]Added resource: {name}[/green]")
        else:
            console.print(f"[red]Resource already exists: {name}[/red]")

    except Exception as e:
        console.print(f"[red]Error adding resource: {e}[/red]")


@economy.command()
@click.argument("covenant_name")
@click.argument("name")
@click.option("--type", "-t", required=True, help="Type of project")
@click.option("--cost", "-c", type=float, required=True, help="Project cost")
@click.option("--seasons", "-s", type=int, required=True, help="Seasons required")
@click.option("--workers", "-w", type=int, default=0, help="Workers required")
def start_project(covenant_name: str, name: str, type: str, cost: float, seasons: int, workers: int):
    """Start a new building project."""
    try:
        economy = CovenantEconomy.load_state(Path(f"ars/data/economy_{covenant_name}.yml"))

        project = BuildingProject(
            name=name, building_type=type, cost=cost, seasons_required=seasons, workers_assigned=workers
        )

        # Add required resources
        if Confirm.ask("Add required resources?"):
            while True:
                resource = Prompt.ask("Resource name (or 'done')")
                if resource.lower() == "done":
                    break
                amount = int(Prompt.ask("Amount required"))
                project.resources_committed[resource] = amount

        if economy.start_project(project):
            economy.save_state(Path(f"ars/data/economy_{covenant_name}.yml"))
            console.print(f"[green]Started project: {name}[/green]")
        else:
            console.print("[red]Could not start project: insufficient funds or " "project already exists[/red]")

    except Exception as e:
        console.print(f"[red]Error starting project: {e}[/red]")


@economy.command()
@click.argument("covenant_name")
@click.argument("name")
@click.argument("amount", type=float)
def add_income(covenant_name: str, name: str, amount: float):
    """Add an income source."""
    try:
        economy = CovenantEconomy.load_state(Path(f"ars/data/economy_{covenant_name}.yml"))
        economy.add_income_source(name, amount)
        economy.save_state(Path(f"ars/data/economy_{covenant_name}.yml"))
        console.print(f"[green]Added income source: {name} " f"({amount} per season)[/green]")
    except Exception as e:
        console.print(f"[red]Error adding income: {e}[/red]")


@economy.command()
@click.argument("covenant_name")
@click.argument("name")
@click.argument("amount", type=float)
def add_expense(covenant_name: str, name: str, amount: float):
    """Add an expense."""
    try:
        economy = CovenantEconomy.load_state(Path(f"ars/data/economy_{covenant_name}.yml"))
        economy.add_expense(name, amount)
        economy.save_state(Path(f"ars/data/economy_{covenant_name}.yml"))
        console.print(f"[green]Added expense: {name} " f"({amount} per season)[/green]")
    except Exception as e:
        console.print(f"[red]Error adding expense: {e}[/red]")


@economy.command()
@click.argument("covenant_name")
@click.option("--season", "-s", required=True)
@click.option("--year", "-y", type=int, required=True)
def process_season(covenant_name: str, season: str, year: int):
    """Process a season's economic activities."""
    try:
        economy = CovenantEconomy.load_state(Path(f"ars/data/economy_{covenant_name}.yml"))

        results = economy.process_season(season, year)

        # Display results
        console.print(f"\n[bold]Economic Results for {season} {year}[/bold]")

        console.print(f"\nTreasury: {economy.treasury}")
        console.print(f"Income: +{results['income']}")
        console.print(f"Expenses: -{results['expenses']}")

        if results["maintenance"]:
            console.print("\n[yellow]Maintenance Issues:[/yellow]")
            for issue in results["maintenance"]:
                console.print(f"- {issue}")

        if results["projects"]:
            console.print("\n[green]Project Updates:[/green]")
            for project in results["projects"]:
                console.print(f"- {project['name']}: {project['status']}")

        if results["resources"]:
            console.print("\n[blue]Resource Updates:[/blue]")
            for resource in results["resources"]:
                console.print(f"- {resource['name']}: " f"Condition {resource['condition']}%")

        economy.save_state(Path(f"ars/data/economy_{covenant_name}.yml"))

    except Exception as e:
        console.print(f"[red]Error processing season: {e}[/red]")


@economy.command()
@click.argument("covenant_name")
def status(covenant_name: str):
    """Show covenant economic status."""
    try:
        economy = CovenantEconomy.load_state(Path(f"ars/data/economy_{covenant_name}.yml"))

        # Display general info
        console.print(f"\n[bold]{covenant_name} Economic Status[/bold]")
        console.print(f"\nTreasury: {economy.treasury}")

        # Display income sources
        if economy.income_sources:
            income_table = Table(title="Income Sources")
            income_table.add_column("Source")
            income_table.add_column("Amount")

            for source, amount in economy.income_sources.items():
                income_table.add_row(source, str(amount))

            console.print("\n", income_table)

        # Display expenses
        if economy.expenses:
            expense_table = Table(title="Expenses")
            expense_table.add_column("Expense")
            expense_table.add_column("Amount")

            for expense, amount in economy.expenses.items():
                expense_table.add_row(expense, str(amount))

            console.print("\n", expense_table)

        # Display resources
        if economy.resources:
            resource_table = Table(title="Resources")
            resource_table.add_column("Name")
            resource_table.add_column("Type")
            resource_table.add_column("Category")
            resource_table.add_column("Quality")
            resource_table.add_column("Condition")

            for resource in economy.resources.values():
                resource_table.add_row(
                    resource.name,
                    resource.__class__.__name__,
                    resource.category.value,
                    str(resource.quality),
                    f"{resource.condition}%",
                )

            console.print("\n", resource_table)

        # Display active projects
        active_projects = {name: proj for name, proj in economy.projects.items() if proj.status == "In Progress"}
        if active_projects:
            project_table = Table(title="Active Projects")
            project_table.add_column("Name")
            project_table.add_column("Type")
            project_table.add_column("Progress")
            project_table.add_column("Workers")

            for project in active_projects.values():
                project_table.add_row(
                    project.name,
                    project.building_type,
                    f"{project.seasons_completed}/{project.seasons_required}",
                    str(project.workers_assigned),
                )

            console.print("\n", project_table)

    except Exception as e:
        console.print(f"[red]Error showing status: {e}[/red]")


def _get_resource_details(res_type: str) -> dict:
    """Get detailed information for a resource based on its type."""
    details = {}

    if res_type == "mundane":
        details["type"] = Prompt.ask("Resource type")
        details["size"] = int(Prompt.ask("Size", default="1"))
        details["workers"] = int(Prompt.ask("Workers required", default="0"))

    elif res_type == "magical":
        details["bonus"] = int(Prompt.ask("Magical bonus", default="0"))
        if Confirm.ask("Add Form?"):
            details["form"] = Prompt.ask("Form", choices=[f.value for f in Form])
        if Confirm.ask("Has charges?"):
            details["charges"] = int(Prompt.ask("Number of charges"))

    elif res_type == "book":
        details["level"] = int(Prompt.ask("Book level", default="1"))
        details["subject"] = Prompt.ask("Subject")
        details["author"] = Prompt.ask("Author")
        details["copies"] = int(Prompt.ask("Number of copies", default="1"))

    elif res_type == "personnel":
        details["role"] = Prompt.ask("Role")
        details["salary"] = float(Prompt.ask("Salary", default="0"))
        details["loyalty"] = int(Prompt.ask("Loyalty (0-100)", default="50"))

        # Add abilities
        details["abilities"] = {}
        if Confirm.ask("Add abilities?"):
            while True:
                ability = Prompt.ask("Ability name (or 'done')")
                if ability.lower() == "done":
                    break
                level = int(Prompt.ask("Ability level"))
                details["abilities"][ability] = level

    return details
