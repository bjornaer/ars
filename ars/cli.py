from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console

from ars.commands.adventure_commands import adventure
from ars.commands.character_commands import character
from ars.commands.combat_commands import combat
from ars.commands.covenant_commands import covenant
from ars.commands.economy_commands import economy
from ars.commands.experience_commands import exp
from ars.commands.lab_commands import lab
from ars.commands.magic_item_commands import enchant
from ars.commands.research_commands import research
from ars.commands.roll_commands import roll
from ars.commands.season_commands import season
from ars.commands.spell_commands import spell
from ars.commands.vis_aura_commands import vis
from ars.state import GameState

console = Console()
game_state: Optional[GameState] = None


def get_game_state() -> GameState:
    """Get or create the game state."""
    global game_state
    if game_state is None:
        config_file = Path.home() / ".ars" / "config.yml"
        if config_file.exists():
            with config_file.open("r") as f:
                config = yaml.safe_load(f)
                saga_name = config.get("saga_name", "Default Saga")
        else:
            saga_name = "Default Saga"
        game_state = GameState(saga_name=saga_name)
    return game_state


@click.group()
@click.version_option(version="0.1.3")
def main() -> None:
    """Ars Magica character management and dice rolling system."""
    pass


@main.command()
@click.argument("saga_name")
def init(saga_name: str):
    """Initialize a new saga."""
    global game_state
    game_state = GameState(saga_name=saga_name)
    game_state.save_state()
    console.print(f"[green]Initialized new saga: {saga_name}[/green]")


# Register all commands with the main CLI group
main.add_command(adventure)
main.add_command(character)
main.add_command(combat)
main.add_command(covenant)
main.add_command(economy)
main.add_command(exp)
main.add_command(lab)
main.add_command(enchant)
main.add_command(research)
main.add_command(season)
main.add_command(spell)
main.add_command(vis)
main.add_command(roll)

if __name__ == "__main__":
    main()
