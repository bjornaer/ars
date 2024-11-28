from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Prompt

from ars.character import Character
from ars.character_context import clear_current_character, get_current_character, set_current_character
from ars.commands.character_wizard import CharacterWizard
from ars.display import CharacterDisplay

console = Console()


@click.group()
def character():
    """Character management commands"""
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


@character.command()
def wizard():
    """Start interactive character creation wizard."""
    wizard = CharacterWizard()
    character = wizard.run()

    if character:
        try:
            character.save()
            console.print(f"[green]Character {character.name} created successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error saving character: {e}[/red]")


@character.command()
@click.argument("name")
def load(name: str):
    """Load a character as the current character"""
    char_path = Path.home() / ".ars" / "characters" / f"{name}.json"
    if not char_path.exists():
        console.print(f"[red]Character '{name}' not found[/red]")
        return

    character = Character.load(char_path)
    set_current_character(character)
    console.print(f"Loaded character: {character.name}")


@character.command()
def current():
    """Show current character info"""
    character = get_current_character()
    if not character:
        console.print("[red]No character currently loaded[/red]")
        return

    console.print(f"Current character: {character.name}")


@character.command()
def clear():
    """Clear the current character"""
    clear_current_character()
    console.print("Cleared current character")
