from pathlib import Path
from typing import Dict, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ars.adventure import AdventureManager, AdventureType, Encounter, EncounterType, RewardType
from ars.adventure_integration import IntegratedAdventureManager
from ars.character import Character
from ars.covenant import Covenant
from ars.types import Form, Technique

console = Console()


@click.group()
def adventure():
    """Adventure and story management commands."""
    pass


@adventure.command()
@click.argument("name")
@click.option("--type", "-t", type=click.Choice([t.value for t in AdventureType]), required=True)
@click.option("--description", "-d", help="Adventure description")
@click.option("--location", "-l", required=True, help="Adventure location")
@click.option("--season", "-s", required=True, help="Season")
@click.option("--year", "-y", required=True, type=int, help="Year")
@click.option("--difficulty", "-df", type=int, default=3, help="Base difficulty (1-10)")
def create(name: str, type: str, description: str, location: str, season: str, year: int, difficulty: int):
    """Create a new adventure."""
    try:
        manager = AdventureManager()

        adventure = manager.create_adventure(
            name=name,
            type=AdventureType(type),
            description=description or "",
            location=location,
            season=season,
            year=year,
            difficulty=difficulty,
        )

        console.print(f"[green]Created adventure: {adventure.name}[/green]")

        # Ask if user wants to add encounters now
        if Confirm.ask("Add encounters now?"):
            while True:
                _add_encounter_interactive(manager, name)
                if not Confirm.ask("Add another encounter?"):
                    break

        # Save state
        manager.save_state(Path("ars/data/adventures.yml"))

    except Exception as e:
        console.print(f"[red]Error creating adventure: {e}[/red]")


@adventure.command()
@click.argument("adventure_name")
def add_encounter(adventure_name: str):
    """Add an encounter to an adventure."""
    try:
        manager = AdventureManager.load_state(Path("ars/data/adventures.yml"))
        _add_encounter_interactive(manager, adventure_name)
        manager.save_state(Path("ars/data/adventures.yml"))

    except Exception as e:
        console.print(f"[red]Error adding encounter: {e}[/red]")


def _add_encounter_interactive(manager: AdventureManager, adventure_name: str) -> None:
    """Interactive encounter creation."""
    # Show encounter types
    types_table = Table(title="Encounter Types")
    types_table.add_column("Type")
    types_table.add_column("Description")

    for e_type in EncounterType:
        types_table.add_row(e_type.value, _get_encounter_description(e_type))
    console.print(types_table)

    # Get encounter details
    e_type = Prompt.ask("Encounter type", choices=[t.value for t in EncounterType])

    difficulty = int(Prompt.ask("Difficulty (1-10)", default="3"))

    description = Prompt.ask("Description")

    # Get requirements based on type
    requirements = {}
    if Confirm.ask("Add requirements?"):
        while True:
            req = Prompt.ask("Requirement (ability/characteristic)")
            value = int(Prompt.ask(f"Minimum {req} value"))
            requirements[req] = value

            if not Confirm.ask("Add another requirement?"):
                break

    # Get rewards
    rewards = {}
    if Confirm.ask("Add rewards?"):
        while True:
            # Show reward types
            rewards_table = Table(title="Reward Types")
            rewards_table.add_column("Type")
            rewards_table.add_column("Description")

            for r_type in RewardType:
                rewards_table.add_row(r_type.value, _get_reward_description(r_type))
            console.print(rewards_table)

            r_type = Prompt.ask("Reward type", choices=[t.value for t in RewardType])

            reward_data = _get_reward_details(RewardType(r_type))
            rewards[RewardType(r_type)] = reward_data

            if not Confirm.ask("Add another reward?"):
                break

    # Add encounter
    if manager.add_encounter(adventure_name, EncounterType(e_type), difficulty, description, requirements, rewards):
        console.print("[green]Encounter added successfully![/green]")
    else:
        console.print("[red]Failed to add encounter[/red]")


@adventure.command()
@click.argument("adventure_name")
@click.argument("participants", nargs=-1)
@click.option("--season", "-s", required=True, help="Season")
@click.option("--year", "-y", required=True, type=int, help="Year")
@click.option("--covenant", "-c", help="Associated covenant")
def start(adventure_name: str, participants: tuple, season: str, year: int, covenant: Optional[str]):
    """Start an adventure with given participants."""
    try:
        manager = IntegratedAdventureManager("main_saga")  # TODO: Get from config

        # Load participant characters
        chars = []
        for name in participants:
            char = Character.load(name)
            if char:
                chars.append(char)
            else:
                console.print(f"[red]Character not found: {name}[/red]")
                return

        # Load covenant if specified
        cov = None
        if covenant:
            cov = Covenant.load(covenant)
            if not cov:
                console.print(f"[red]Covenant not found: {covenant}[/red]")
                return

        result = manager.start_seasonal_adventure(adventure_name, chars, season, year)

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return

        if cov:
            manager.apply_covenant_effects(manager.adventure_manager.adventures[adventure_name], cov)

        for char in chars:
            manager.apply_laboratory_effects(manager.adventure_manager.adventures[adventure_name], char)

        manager.apply_seasonal_effects(manager.adventure_manager.adventures[adventure_name], season)

        console.print(
            f"[green]Started adventure: {result['adventure']}\n"
            f"Participants: {', '.join(result['participants'])}\n"
            f"Season: {season} {year}[/green]"
        )

        manager.adventure_manager.save_state(Path("ars/data/adventures.yml"))

    except Exception as e:
        console.print(f"[red]Error starting adventure: {e}[/red]")


@adventure.command()
@click.argument("encounter_index", type=int)
def resolve_encounter(encounter_index: int):
    """Resolve the current encounter in active adventure."""
    try:
        manager = AdventureManager.load_state(Path("ars/data/adventures.yml"))

        if not manager.active_adventure:
            console.print("[red]No active adventure![/red]")
            return

        # Get actions for each participant
        actions = {}
        for participant in manager.active_adventure.participants:
            console.print(f"\n[bold]Actions for {participant}:[/bold]")
            actions[participant] = _get_participant_actions(manager.active_adventure.encounters[encounter_index])

        # Resolve encounter
        result = manager.resolve_encounter(encounter_index, actions)

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return

        # Display results
        _display_encounter_results(result)

        manager.save_state(Path("ars/data/adventures.yml"))

    except Exception as e:
        console.print(f"[red]Error resolving encounter: {e}[/red]")


@adventure.command()
def list():
    """List all adventures."""
    try:
        manager = AdventureManager.load_state(Path("ars/data/adventures.yml"))

        table = Table(title="Adventures")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Location")
        table.add_column("Season/Year")
        table.add_column("Status")
        table.add_column("Encounters")

        for adv in manager.adventures.values():
            table.add_row(
                adv.name, adv.type.value, adv.location, f"{adv.season}/{adv.year}", adv.status, str(len(adv.encounters))
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing adventures: {e}[/red]")


@adventure.command()
@click.argument("name")
def show(name: str):
    """Show adventure details."""
    try:
        manager = AdventureManager.load_state(Path("ars/data/adventures.yml"))

        if name not in manager.adventures:
            console.print("[red]Adventure not found![/red]")
            return

        adv = manager.adventures[name]

        # Display adventure info
        console.print(
            Panel(
                f"[bold]{adv.name}[/bold]\n"
                f"Type: {adv.type.value}\n"
                f"Location: {adv.location}\n"
                f"Season/Year: {adv.season}/{adv.year}\n"
                f"Difficulty: {adv.difficulty}\n"
                f"Status: {adv.status}\n"
                f"Description: {adv.description}"
            )
        )

        # Display encounters
        if adv.encounters:
            encounters_table = Table(title="Encounters")
            encounters_table.add_column("#")
            encounters_table.add_column("Type")
            encounters_table.add_column("Difficulty")
            encounters_table.add_column("Status")
            encounters_table.add_column("Description")

            for i, enc in enumerate(adv.encounters):
                encounters_table.add_row(
                    str(i + 1),
                    enc.type.value,
                    str(enc.difficulty),
                    "Completed" if enc.completed else "Pending",
                    enc.description,
                )

            console.print(encounters_table)

        # Display participants if active
        if adv.participants:
            console.print("\n[bold]Participants:[/bold]")
            for p in adv.participants:
                console.print(f"- {p}")

    except Exception as e:
        console.print(f"[red]Error showing adventure: {e}[/red]")


def _get_participant_actions(encounter: Encounter) -> Dict[str, any]:
    """Get actions for a participant in an encounter."""
    actions = {}

    if encounter.type == EncounterType.COMBAT:
        actions["weapon_ability"] = Prompt.ask("Weapon ability to use", default="Single Weapon")
        actions["characteristic"] = Prompt.ask("Characteristic to use", default="Dexterity")

    elif encounter.type == EncounterType.MAGICAL:
        actions["technique"] = Prompt.ask("Technique to use", choices=[t.value for t in Technique])
        actions["form"] = Prompt.ask("Form to use", choices=[f.value for f in Form])

    elif encounter.type == EncounterType.SOCIAL:
        actions["ability"] = Prompt.ask("Ability to use", default="Communication")
        actions["characteristic"] = Prompt.ask("Characteristic to use", default="Presence")

    return actions


def _display_encounter_results(results: Dict[str, any]) -> None:
    """Display the results of an encounter."""
    console.print("\n[bold]Encounter Results:[/bold]")

    for participant, result in results["results"].items():
        console.print(f"\n[bold]{participant}:[/bold]")
        console.print(f"Roll: {result['roll']}")
        console.print(f"Total: {result['total']}")
        console.print(f"Needed: {result['needed']}")
        console.print(f"Success: {'Yes' if result['success'] else 'No'}")

        effects = result["effects"]
        if effects["botch"]:
            console.print("[red]BOTCH![/red]")
        if effects["critical"]:
            console.print("[green]CRITICAL SUCCESS![/green]")
        if "magnitude" in effects:
            console.print(f"Magnitude: {effects['magnitude']}")

    console.print(f"\nOverall Success: {'Yes' if results['success'] else 'No'}")
    console.print(f"Adventure Status: {results['adventure_status']}")


def _get_encounter_description(e_type: EncounterType) -> str:
    """Get description for encounter type."""
    descriptions = {
        EncounterType.COMBAT: "Physical conflict resolution",
        EncounterType.SOCIAL: "Social interaction and negotiation",
        EncounterType.MAGICAL: "Magical challenges and mysteries",
        EncounterType.PUZZLE: "Mental challenges and riddles",
        EncounterType.CHALLENGE: "Skill-based challenges",
        EncounterType.DISCOVERY: "Exploration and discovery",
    }
    return descriptions.get(e_type, "")


def _get_reward_description(r_type: RewardType) -> str:
    """Get description for reward type."""
    descriptions = {
        RewardType.VIS: "Magical raw vis",
        RewardType.BOOKS: "Books and lab texts",
        RewardType.EQUIPMENT: "Mundane or magical equipment",
        RewardType.REPUTATION: "Reputation with various groups",
        RewardType.EXPERIENCE: "Experience points in abilities",
        RewardType.RESOURCES: "Covenant resources",
    }
    return descriptions.get(r_type, "")


def _get_reward_details(r_type: RewardType) -> Dict:
    """Get detailed reward information based on type."""
    if r_type == RewardType.VIS:
        form = Prompt.ask("Vis form", choices=[f.value for f in Form])
        amount = int(Prompt.ask("Amount of pawns"))
        return {form: amount}

    elif r_type == RewardType.EXPERIENCE:
        ability = Prompt.ask("Ability name")
        xp = int(Prompt.ask("Experience points"))
        return {ability: xp}

    elif r_type == RewardType.REPUTATION:
        group = Prompt.ask("Reputation group")
        value = int(Prompt.ask("Reputation change"))
        return {group: value}

    elif r_type == RewardType.RESOURCES:
        resource = Prompt.ask("Resource type")
        amount = int(Prompt.ask("Amount"))
        return {resource: amount}

    elif r_type == RewardType.BOOKS:
        return {
            "art": Prompt.ask("Art (if applicable)"),
            "level": int(Prompt.ask("Book level", default="5")),
            "quality": int(Prompt.ask("Book quality", default="10")),
        }

    elif r_type == RewardType.EQUIPMENT:
        return {"name": Prompt.ask("Equipment name"), "bonus": int(Prompt.ask("Equipment bonus", default="0"))}

    return {}
