from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..types import Form
from ..vis_aura import AuraManager, AuraProperties, AuraType, VisManager, VisSource, VisType

console = Console()


@click.group()
def vis():
    """Vis and aura management commands."""
    pass


@vis.command()
@click.argument("location")
@click.argument("aura_type", type=click.Choice([a.value for a in AuraType]))
@click.argument("strength", type=int)
@click.option("--properties", "-p", multiple=True, help="Aura properties")
@click.option("--modifier", "-m", multiple=True, help="Modifiers in form key:value")
def register_aura(location: str, aura_type: str, strength: int, properties: tuple, modifier: tuple):
    """Register a new magical aura."""
    try:
        # Parse modifiers
        modifiers = {}
        for mod in modifier:
            key, value = mod.split(":")
            modifiers[key.strip()] = int(value)

        # Create aura properties
        aura = AuraProperties(
            type=AuraType(aura_type), strength=strength, properties=list(properties), modifiers=modifiers
        )

        # Register aura
        manager = AuraManager()
        manager.register_aura(location, aura)

        console.print(f"[green]Registered {aura_type} aura of strength {strength} at {location}[/green]")

        if properties:
            console.print("[cyan]Properties:[/cyan]")
            for prop in properties:
                console.print(f"  • {prop}")

        if modifiers:
            console.print("[cyan]Modifiers:[/cyan]")
            for key, value in modifiers.items():
                console.print(f"  • {key}: {value}")

    except Exception as e:
        console.print(f"[red]Error registering aura: {e}[/red]")


@vis.command()
@click.argument("name")
@click.argument("form", type=click.Choice([f.value for f in Form]))
@click.argument("amount", type=int)
@click.option(
    "--type", "-t", "vis_type", type=click.Choice([v.value for v in VisType]), default="Raw", help="Type of vis"
)
@click.option("--season", "-s", help="Season when vis can be collected")
@click.option("--location", "-l", help="Source location")
@click.option("--description", "-d", help="Source description")
def add_source(name: str, form: str, amount: int, vis_type: str, season: str, location: str, description: str):
    """Register a new vis source."""
    try:
        source = VisSource(
            form=Form(form),
            amount=amount,
            type=VisType(vis_type),
            season=season,
            location=location or "",
            description=description or "",
        )

        manager = VisManager()
        manager.register_source(name, source)
        manager.save(Path("ars/data/vis_sources.yml"))

        console.print(f"[green]Registered vis source: {name}[/green]")
        console.print(
            Panel(
                f"Form: {form}\n"
                f"Amount: {amount}\n"
                f"Type: {vis_type}\n"
                f"Season: {season or 'Any'}\n"
                f"Location: {location or 'Not specified'}\n"
                f"Description: {description or 'None'}"
            )
        )

    except Exception as e:
        console.print(f"[red]Error adding vis source: {e}[/red]")


@vis.command()
@click.argument("source_name")
@click.argument("year", type=int)
@click.argument("season")
@click.option("--aura-strength", type=int, default=0, help="Local aura strength affecting collection")
def collect(source_name: str, year: int, season: str, aura_strength: int):
    """Collect vis from a source."""
    try:
        manager = VisManager.load(Path("ars/data/vis_sources.yml"))
        form, amount = manager.collect_vis(source_name, year, season, aura_strength)

        if amount > 0:
            console.print(f"[green]Collected {amount} pawns of {form.value} vis[/green]")
            manager.save(Path("ars/data/vis_sources.yml"))
        else:
            console.print("[yellow]No vis collected. Check season and last collection date.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error collecting vis: {e}[/red]")


@vis.command()
def show_stocks():
    """Display current vis stocks."""
    try:
        manager = VisManager.load(Path("ars/data/vis_sources.yml"))

        table = Table(title="Vis Stocks")
        table.add_column("Form", style="cyan")
        table.add_column("Amount", justify="right")

        for form, amount in manager.stocks.items():
            if amount > 0:  # Only show non-zero stocks
                table.add_row(form.value, str(amount))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error displaying vis stocks: {e}[/red]")


@vis.command()
def show_sources():
    """Display registered vis sources."""
    try:
        manager = VisManager.load(Path("ars/data/vis_sources.yml"))

        table = Table(title="Vis Sources")
        table.add_column("Name")
        table.add_column("Form")
        table.add_column("Amount")
        table.add_column("Season")
        table.add_column("Last Collected")
        table.add_column("Location")

        for name, source in manager.sources.items():
            table.add_row(
                name,
                source.form.value,
                str(source.amount),
                source.season or "Any",
                str(source.last_collected or "Never"),
                source.location or "Unknown",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error displaying vis sources: {e}[/red]")


@vis.command()
@click.argument("form", type=click.Choice([f.value for f in Form]))
@click.argument("amount", type=int)
def use(form: str, amount: int):
    """Use vis from stocks."""
    try:
        manager = VisManager.load(Path("ars/data/vis_sources.yml"))

        if manager.use_vis(Form(form), amount):
            console.print(f"[green]Used {amount} pawns of {form} vis[/green]")
            manager.save(Path("ars/data/vis_sources.yml"))
        else:
            console.print(f"[red]Insufficient {form} vis in stock[/red]")

    except Exception as e:
        console.print(f"[red]Error using vis: {e}[/red]")


@vis.command()
@click.argument("location")
def show_aura(location: str):
    """Display aura information for a location."""
    try:
        manager = AuraManager()
        aura = manager.get_aura(location)

        if not aura:
            console.print(f"[yellow]No registered aura for {location}[/yellow]")
            return

        panel = Panel(
            f"Type: {aura.type.value}\n"
            f"Strength: {aura.strength}\n"
            f"Properties: {', '.join(aura.properties) or 'None'}\n"
            f"Modifiers: {', '.join(f'{k}: {v}' for k, v in aura.modifiers.items()) or 'None'}",
            title=f"Aura at {location}",
        )
        console.print(panel)

    except Exception as e:
        console.print(f"[red]Error displaying aura: {e}[/red]")
