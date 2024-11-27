import click
from rich.console import Console
from rich.prompt import Prompt

from .character import Character
from .dice import ArtRoller, DiceRoller
from .display import CharacterDisplay

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Ars Magica character management and dice rolling system."""
    pass


@main.group()
def character() -> None:
    """Character management commands."""
    pass


@character.command()
def create() -> None:
    """Create a new character."""
    try:
        console.print("[bold blue]Creating new character[/bold blue]")

        # Basic information
        name = Prompt.ask("Character Name")
        player = Prompt.ask("Player Name")
        saga = Prompt.ask("Saga")
        covenant = Prompt.ask("Covenant")
        age = Prompt.ask("Age", default="25")

        char = Character(name=name, player=player, saga=saga, covenant=covenant, age=int(age))

        # Characteristics
        console.print("\n[bold]Enter Characteristics (-3 to +3):[/bold]")
        for attr in [
            "intelligence",
            "perception",
            "strength",
            "stamina",
            "presence",
            "communication",
            "dexterity",
            "quickness",
        ]:
            value = Prompt.ask(f"{attr.capitalize()}", default="0", show_default=True)
            setattr(char, attr, int(value))

        # Arts
        console.print("\n[bold]Enter Techniques (0+):[/bold]")
        for technique in char.techniques:
            value = Prompt.ask(f"{technique}", default="0", show_default=True)
            char.techniques[technique] = int(value)

        console.print("\n[bold]Enter Forms (0+):[/bold]")
        for form in char.forms:
            value = Prompt.ask(f"{form}", default="0", show_default=True)
            char.forms[form] = int(value)

        # Save character
        char.save()
        console.print(f"\n[green]Character {name} created and saved![/green]")

    except Exception as e:
        console.print(f"[red]Error creating character: {e}[/red]")


@character.command()
def list() -> None:
    """List all available characters."""
    try:
        characters = Character.list_characters()
        if not characters:
            console.print("[yellow]No characters found.[/yellow]")
            return

        console.print("\n[bold]Available Characters:[/bold]")
        for char in characters:
            console.print(f"  • {char}")

    except Exception as e:
        console.print(f"[red]Error listing characters: {e}[/red]")


@character.command()
@click.argument("name")
def show(name: str) -> None:
    """Display character sheet."""
    try:
        char = Character.load(name)
        display = CharacterDisplay(char)
        display.show()

    except FileNotFoundError:
        console.print(f"[red]Character '{name}' not found![/red]")
    except Exception as e:
        console.print(f"[red]Error displaying character: {e}[/red]")


@main.group()
def roll() -> None:
    """Dice rolling commands."""
    pass


@roll.command()
@click.option("--stress", is_flag=True, help="Use stress die")
def simple(stress: bool) -> None:
    """Roll a simple or stress die."""
    try:
        if stress:
            result = DiceRoller.stress_die()
            console.print(f"Stress die result: {result}")
        else:
            result = DiceRoller.simple_die()
            console.print(f"Simple die result: {result}")

    except Exception as e:
        console.print(f"[red]Error rolling die: {e}[/red]")


@roll.command()
@click.argument("technique")
@click.argument("form")
@click.option("--aura", default=0, help="Magical aura modifier")
@click.option("--stress/--no-stress", default=True, help="Use stress die")
def spell(technique: str, form: str, aura: int, stress: bool) -> None:
    """Roll for spell casting."""
    try:
        result = ArtRoller.cast_spell(int(technique), int(form), aura=aura, stress=stress)
        console.print(f"Spell casting result: {result}")

    except Exception as e:
        console.print(f"[red]Error rolling for spell: {e}[/red]")


if __name__ == "__main__":
    main()
