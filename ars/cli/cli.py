from pathlib import Path
import click
import yaml
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from ars.cli.character_commands import character
from ars.cli.spell_commands import spell
from ars.cli.combat_commands import combat
from ars.cli.roll_commands import roll
from ars.cli.state import (
    get_saga_dir, get_active_saga, set_active_saga,
    get_active_character, set_active_character, get_character_dir,
    init_saga_config
)

console = Console()


@click.group()
@click.version_option(version="0.1.3")
def main():
    """Ars Magica 5th Edition Character and Combat Management System."""
    pass


# Register command groups
main.add_command(character)
main.add_command(spell)
main.add_command(combat)
main.add_command(roll)


@main.command()
@click.argument("saga_name")
@click.option("--activate/--no-activate", default=True, 
              help="Set as active saga after initialization")
def init(saga_name: str, activate: bool):
    """Initialize a new saga and configuration."""
    try:
        # Initialize saga directory and config
        saga_dir = init_saga_config(saga_name)
        console.print(f"[green]Initialized saga directory: {saga_dir}[/green]")
        
        if activate:
            set_active_saga(saga_name)
            console.print(f"[green]Set '{saga_name}' as active saga[/green]")
            
    except Exception as e:
        console.print(f"[red]Error initializing saga: {e}[/red]")


@main.command()
@click.argument("saga_name")
def activate(saga_name: str):
    """Set the active saga."""
    try:
        saga_dir = get_saga_dir(saga_name)
        if not saga_dir.exists():
            console.print(f"[red]Saga '{saga_name}' not found. Initialize it first.[/red]")
            return
            
        set_active_saga(saga_name)
        console.print(f"[green]Activated saga: {saga_name}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error activating saga: {e}[/red]")


@main.command()
def list_sagas():
    """List all available sagas."""
    try:
        ars_dir = Path.home() / ".ars"
        if not ars_dir.exists():
            console.print("[yellow]No sagas found[/yellow]")
            return
            
        active_saga = get_active_saga()
        sagas = []
        
        for path in ars_dir.iterdir():
            if path.is_dir() and not path.name.startswith('.'):
                config_file = path / "config.yml"
                if config_file.exists():
                    with config_file.open('r') as f:
                        config = yaml.safe_load(f)
                        saga_name = config.get('saga_name', path.name)
                        sagas.append((
                            saga_name,
                            "[green]active[/green]" if saga_name == active_saga else ""
                        ))
                        
        if sagas:
            table = Table(title="Available Sagas")
            table.add_column("Saga Name", style="cyan")
            table.add_column("Status", style="green")
            
            for saga in sorted(sagas):
                table.add_row(*saga)
                
            console.print(table)
        else:
            console.print("[yellow]No sagas found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error listing sagas: {e}[/red]")


@main.command()
@click.argument("character_name")
def use(character_name: str):
    """Set the active character."""
    try:
        # Verify character exists in active saga
        char_dir = get_character_dir()
        char_path = char_dir / f"{character_name.lower().replace(' ', '_')}.json"
        
        if not char_path.exists():
            console.print(f"[red]Character '{character_name}' not found in active saga[/red]")
            return
            
        set_active_character(character_name)
        console.print(f"[green]Now using character: {character_name}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error setting active character: {e}[/red]")


@main.command()
def unuse():
    """Clear the active character."""
    try:
        set_active_character(None)
        console.print("[green]Cleared active character[/green]")
        
    except Exception as e:
        console.print(f"[red]Error clearing active character: {e}[/red]")


if __name__ == "__main__":
    main()