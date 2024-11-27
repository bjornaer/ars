import click
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from ..covenant import Building, BuildingType, Covenant, CovenantSize, VisSource
from ..types import Form

console = Console()


@click.group()
def covenant():
    """Covenant management commands."""
    pass


@covenant.command()
@click.argument("name")
@click.option("--size", type=click.Choice([s.value for s in CovenantSize]), required=True)
@click.option("--age", type=int, default=0, help="Age of the covenant in years")
@click.option("--aura", type=int, default=3, help="Magical aura strength")
def create(name: str, size: str, age: int, aura: int):
    """Create a new covenant."""
    try:
        covenant = Covenant(name=name, size=CovenantSize(size), age=age, aura=aura)
        covenant.save()
        console.print(f"[green]Created covenant {name}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating covenant: {e}[/red]")


@covenant.command()
@click.argument("covenant_name")
@click.argument("building_type", type=click.Choice([b.value for b in BuildingType]))
@click.argument("building_name")
@click.option("--size", type=int, default=1, help="Size of the building")
@click.option("--quality", type=int, default=0, help="Quality of the building")
@click.option("--description", help="Description of the building")
def add_building(
    covenant_name: str, building_type: str, building_name: str, size: int, quality: int, description: str = ""
):
    """Add a building to the covenant."""
    try:
        covenant = Covenant.load(covenant_name)

        building = Building(
            type=BuildingType(building_type),
            name=building_name,
            size=size,
            quality=quality,
            description=description,
            maintenance_cost=size * (quality + 1),  # Simple cost calculation
        )

        covenant.add_building(building)
        covenant.save()

        console.print(f"[green]Added {building_name} to {covenant_name}[/green]")
    except Exception as e:
        console.print(f"[red]Error adding building: {e}[/red]")


@covenant.command()
@click.argument("covenant_name")
@click.argument("source_name")
@click.argument("form", type=click.Choice([f.value for f in Form]))
@click.argument("amount", type=int)
@click.argument("season", type=click.Choice(["Spring", "Summer", "Autumn", "Winter"]))
@click.option("--description", help="Description of the vis source")
def add_vis_source(covenant_name: str, source_name: str, form: str, amount: int, season: str, description: str = ""):
    """Add a vis source to the covenant."""
    try:
        covenant = Covenant.load(covenant_name)

        source = VisSource(name=source_name, form=Form(form), amount=amount, season=season, description=description)

        covenant.add_vis_source(source)
        covenant.save()

        console.print(f"[green]Added vis source {source_name} to {covenant_name}[/green]")
    except Exception as e:
        console.print(f"[red]Error adding vis source: {e}[/red]")


@covenant.command()
@click.argument("covenant_name")
@click.argument("book_name")
@click.argument("level", type=int)
def add_book(covenant_name: str, book_name: str, level: int):
    """Add a book to the covenant library."""
    try:
        covenant = Covenant.load(covenant_name)
        covenant.add_book(book_name, level)
        covenant.save()

        console.print(f"[green]Added book {book_name} to {covenant_name}'s library[/green]")
    except Exception as e:
        console.print(f"[red]Error adding book: {e}[/red]")


@covenant.command()
@click.argument("covenant_name")
@click.argument("season", type=click.Choice(["Spring", "Summer", "Autumn", "Winter"]))
def collect_vis(covenant_name: str, season: str):
    """Collect vis from available sources for the season."""
    try:
        covenant = Covenant.load(covenant_name)
        collected = covenant.collect_vis(season)

        # Create a table to show collected vis
        table = Table(title=f"Vis Collection for {season}")
        table.add_column("Form")
        table.add_column("Amount")

        for form, amount in collected.items():
            if amount > 0:
                table.add_row(form.value, str(amount))

        console.print(table)
        covenant.save()
    except Exception as e:
        console.print(f"[red]Error collecting vis: {e}[/red]")


@covenant.command()
@click.argument("covenant_name")
def show(covenant_name: str):
    """Display covenant details."""
    try:
        covenant = Covenant.load(covenant_name)

        # Create main info panel
        main_info = Table.grid()
        main_info.add_row("Name:", covenant.name)
        main_info.add_row("Size:", covenant.size.value)
        main_info.add_row("Age:", str(covenant.age))
        main_info.add_row("Aura:", str(covenant.aura))

        # Create buildings table
        buildings_table = Table(title="Buildings")
        buildings_table.add_column("Name")
        buildings_table.add_column("Type")
        buildings_table.add_column("Size")
        buildings_table.add_column("Quality")

        for building in covenant.buildings:
            buildings_table.add_row(building.name, building.type.value, str(building.size), str(building.quality))

        # Create vis sources table
        vis_table = Table(title="Vis Sources")
        vis_table.add_column("Name")
        vis_table.add_column("Form")
        vis_table.add_column("Amount")
        vis_table.add_column("Season")

        for source in covenant.vis_sources:
            vis_table.add_row(source.name, source.form.value, str(source.amount), source.season)

        # Create library info
        library_info = Table.grid()
        library_info.add_row("Books:", str(len(covenant.library.books)))
        library_info.add_row("Capacity:", str(covenant.library.capacity))
        library_info.add_row("Organization:", str(covenant.library.organization))

        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(Panel(main_info, title="Covenant Information")),
            Layout(buildings_table),
            Layout(vis_table),
            Layout(Panel(library_info, title="Library Information")),
        )

        console.print(layout)

    except Exception as e:
        console.print(f"[red]Error displaying covenant: {e}[/red]")


@covenant.command()
@click.argument("covenant_name")
def finances(covenant_name: str):
    """Display covenant finances."""
    try:
        covenant = Covenant.load(covenant_name)

        income = covenant.calculate_income()
        expenses = covenant.calculate_expenses()
        balance = income - expenses

        table = Table(title="Covenant Finances")
        table.add_column("Category")
        table.add_column("Amount")

        table.add_row("Income", str(income))
        table.add_row("Expenses", str(expenses))
        table.add_row("Balance", str(balance))

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error displaying finances: {e}[/red]")
