import click
from rich.console import Console
from rich.table import Table

from ars.character_context import get_current_character

console = Console()


@click.group()
def exp():
    """Experience management commands"""
    pass


@exp.command()
@click.argument("amount", type=int)
@click.argument("category")
@click.option("--description", "-d", default="", help="Description of the experience gain")
def add(amount: int, category: str, description: str):
    """Add experience to current character"""
    character = get_current_character()
    if not character:
        console.print("[red]No character currently loaded[/red]")
        return

    character.add_exp(amount, description, category)
    character.save()
    console.print(f"Added {amount} exp to {character.name} in {category}")


@exp.command(name="show")
def show_exp():
    """Show experience details for current character"""
    character = get_current_character()
    if not character:
        console.print("[red]No character currently loaded[/red]")
        return

    table = Table(title=f"Experience for {character.name}")
    table.add_column("Category")
    table.add_column("Total")
    table.add_column("Available")

    for category, exp in character.experience.exp_by_category.items():
        table.add_row(category, str(exp), str(character.experience.get_available_exp()))

    console.print(table)


@exp.command()
def history():
    """Show experience history for current character"""
    character = get_current_character()
    if not character:
        console.print("[red]No character currently loaded[/red]")
        return

    table = Table(title=f"Experience History for {character.name}")
    table.add_column("Date")
    table.add_column("Amount")
    table.add_column("Category")
    table.add_column("Description")

    for entry in character.experience.history:
        table.add_row(entry.date.strftime("%Y-%m-%d"), str(entry.amount), entry.category, entry.description)

    console.print(table)
