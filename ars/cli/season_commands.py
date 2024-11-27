import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..character import Character
from ..covenant import Covenant
from ..seasons import ActivityType, Season, SeasonManager

console = Console()


@click.group()
def season():
    """Season and activity management commands."""
    pass


@season.command()
@click.argument("saga_name")
@click.option("--year", type=int, default=1220, help="Starting year")
@click.option(
    "--season", type=click.Choice(["Spring", "Summer", "Autumn", "Winter"]), default="Spring", help="Starting season"
)
def start_saga(saga_name: str, year: int, season: str):
    """Start a new saga."""
    try:
        manager = SeasonManager(saga_name)
        manager.current_year.year = year
        manager.current_year.current_season = Season(season)
        manager.save_saga()
        console.print(f"[green]Started new saga: {saga_name} in {season} {year}[/green]")
    except Exception as e:
        console.print(f"[red]Error starting saga: {e}[/red]")


@season.command()
@click.argument("saga_name")
@click.argument("character_name")
@click.argument("activity_type", type=click.Choice([a.value for a in ActivityType]))
@click.option("--details", type=str, help="Activity details in key:value format")
def schedule(saga_name: str, character_name: str, activity_type: str, details: str = None):
    """Schedule an activity for a character."""
    try:
        # Parse details
        activity_details = {}
        if details:
            for pair in details.split(","):
                key, value = pair.split(":")
                activity_details[key.strip()] = value.strip()

        # Load saga and character
        manager = SeasonManager(saga_name)
        manager.load_saga()
        character = Character.load(character_name)
        manager.register_character(character)

        # Schedule activity
        activity = manager.schedule_activity(character_name, ActivityType(activity_type), activity_details)
        manager.save_saga()

        console.print(
            f"[green]Scheduled {activity_type} for {character_name} "
            f"in {activity.season.value} {activity.year}[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error scheduling activity: {e}[/red]")


@season.command()
@click.argument("saga_name")
def advance(saga_name: str):
    """Advance and execute the current season."""
    try:
        manager = SeasonManager(saga_name)
        manager.load_saga()

        # Load covenant if exists
        try:
            covenant = Covenant.load(saga_name)
            manager.set_covenant(covenant)
        except FileNotFoundError:
            pass

        # Load all characters
        char_activities = manager.current_year.activities
        for char_name in char_activities.keys():
            character = Character.load(char_name)
            manager.register_character(character)

        # Execute season
        current_season = manager.current_year.current_season
        current_year = manager.current_year.year

        if not Confirm.ask(f"Execute {current_season.value} {current_year}?", default=True):
            return

        results = manager.execute_season()

        # Display results
        console.print(f"\n[bold cyan]Results for {current_season.value} {current_year}:[/bold cyan]")

        for character, activities in results.items():
            char_panel = Panel(
                "\n".join(f"{act_type}: {act_result}" for act_type, act_result in activities.items()),
                title=f"[bold]{character}[/bold]",
            )
            console.print(char_panel)

        # Save updated state
        manager.save_saga()
        console.print(
            f"[green]Advanced to {manager.current_year.current_season.value} " f"{manager.current_year.year}[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error advancing season: {e}[/red]")


@season.command()
@click.argument("saga_name")
def show(saga_name: str):
    """Display current saga status."""
    try:
        manager = SeasonManager(saga_name)
        manager.load_saga()

        # Create main info panel
        info_table = Table.grid(padding=1)
        info_table.add_row(
            f"[cyan]Saga:[/cyan] {saga_name}",
            f"[cyan]Year:[/cyan] {manager.current_year.year}",
            f"[cyan]Season:[/cyan] {manager.current_year.current_season.value}",
        )
        console.print(Panel(info_table, title="Saga Information"))

        # Show scheduled activities
        activities_table = Table(title="Scheduled Activities", show_header=True, header_style="bold magenta")
        activities_table.add_column("Character")
        activities_table.add_column("Activity")
        activities_table.add_column("Season")
        activities_table.add_column("Year")
        activities_table.add_column("Status")

        for char, activities in manager.current_year.activities.items():
            for activity in activities:
                activities_table.add_row(
                    char,
                    activity.type.value,
                    activity.season.value,
                    str(activity.year),
                    "[green]Completed[/green]" if activity.completed else "[yellow]Pending[/yellow]",
                )

        console.print(activities_table)

    except Exception as e:
        console.print(f"[red]Error displaying saga: {e}[/red]")


@season.command()
@click.argument("saga_name")
@click.argument("character_name")
def history(saga_name: str, character_name: str):
    """Show activity history for a character."""
    try:
        manager = SeasonManager(saga_name)
        manager.load_saga()

        activities = manager.current_year.activities.get(character_name, [])

        if not activities:
            console.print(f"[yellow]No activities found for {character_name}[/yellow]")
            return

        history_table = Table(
            title=f"Activity History for {character_name}", show_header=True, header_style="bold magenta"
        )
        history_table.add_column("Season")
        history_table.add_column("Year")
        history_table.add_column("Activity")
        history_table.add_column("Details")
        history_table.add_column("Results")

        for activity in activities:
            history_table.add_row(
                activity.season.value,
                str(activity.year),
                activity.type.value,
                str(activity.details),
                str(activity.results) if activity.completed else "Pending",
            )

        console.print(history_table)

    except Exception as e:
        console.print(f"[red]Error displaying history: {e}[/red]")
