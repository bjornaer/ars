import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ars.certamen import CertamenManager
from ars.character import Character
from ars.core.types import Form, Technique

console = Console()


@click.group()
def certamen():
    """Certamen (magical duel) commands."""
    pass


@certamen.command()
@click.argument("challenger_name")
@click.argument("defender_name")
@click.argument("technique")
@click.argument("form")
def challenge(challenger_name: str, defender_name: str, technique: str, form: str):
    """Initiate a Certamen challenge."""
    try:
        challenger = Character.load(challenger_name)
        defender = Character.load(defender_name)

        manager = CertamenManager()
        _ = manager.initiate_certamen(challenger, defender, Technique(technique.upper()), Form(form.upper()))

        table = Table(title="Certamen Challenge")
        table.add_column("Aspect", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Challenger", challenger_name)
        table.add_row("Defender", defender_name)
        table.add_row("Technique", technique)
        table.add_row("Form", form)

        console.print(table)
        console.print("\n[yellow]Waiting for defender's response...[/yellow]")

    except Exception as e:
        console.print(f"[red]Error initiating Certamen: {e}[/red]")


@certamen.command()
@click.argument("defender_name")
@click.argument("technique")
@click.argument("form")
def respond(defender_name: str, technique: str, form: str):
    """Respond to a Certamen challenge."""
    try:
        defender = Character.load(defender_name)
        manager = CertamenManager()

        _ = manager.respond_to_challenge(defender, Technique(technique.upper()), Form(form.upper()))

        table = Table(title="Certamen Response")
        table.add_column("Aspect", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Defender", defender_name)
        table.add_row("Technique", technique)
        table.add_row("Form", form)

        console.print(table)
        console.print("\n[green]Challenge accepted! Ready to begin exchanges.[/green]")

    except Exception as e:
        console.print(f"[red]Error responding to Certamen: {e}[/red]")


@certamen.command()
@click.argument("character1_name")
@click.argument("character2_name")
@click.option("--modifiers", "-m", type=str, help="Modifiers in format name:value,name:value")
def exchange(character1_name: str, character2_name: str, modifiers: str = None):
    """Resolve one exchange in the Certamen."""
    try:
        character1 = Character.load(character1_name)
        character2 = Character.load(character2_name)

        # Parse modifiers if provided
        modifier_dict = {}
        if modifiers:
            for mod in modifiers.split(","):
                name, value = mod.split(":")
                modifier_dict[name] = int(value)

        manager = CertamenManager()
        result = manager.resolve_exchange(character1, character2, modifiers=modifier_dict)

        # Display results
        table = Table(title=f"Certamen Exchange (Round {manager.rounds_completed})")
        table.add_column("Aspect", style="cyan")
        table.add_column(character1_name, style="magenta")
        table.add_column(character2_name, style="yellow")

        for char_name, char_result in result["results"].items():
            table.add_row(
                "Roll",
                str(char_result["roll"].rolls) if char_name == character1_name else "",
                str(char_result["roll"].rolls) if char_name == character2_name else "",
            )
            table.add_row(
                "Total",
                str(char_result["total"]) if char_name == character1_name else "",
                str(char_result["total"]) if char_name == character2_name else "",
            )
            table.add_row(
                "Fatigue Cost",
                str(char_result["fatigue_cost"]) if char_name == character1_name else "",
                str(char_result["fatigue_cost"]) if char_name == character2_name else "",
            )

        table.add_row("Current Score", str(result["scores"][character1_name]), str(result["scores"][character2_name]))

        console.print(table)

        if result.get("victor"):
            console.print(f"\n[green]Victory! {result['victor']} has won the Certamen![/green]")
        else:
            console.print("\n[yellow]Exchange complete. Continue with next exchange.[/yellow]")

        # Save character states
        character1.save()
        character2.save()

    except Exception as e:
        console.print(f"[red]Error resolving exchange: {e}[/red]")


@certamen.command()
@click.argument("character1_name")
@click.argument("character2_name")
def end_certamen(character1_name: str, character2_name: str):
    """End the Certamen and display final results."""
    try:
        character1 = Character.load(character1_name)
        character2 = Character.load(character2_name)

        manager = CertamenManager()
        result = manager.end_certamen(character1, character2)

        # Create final results display
        title = Text("Final Certamen Results", style="bold magenta")
        content = Text.assemble(
            ("Winner: ", "cyan"),
            (result.winner, "green bold"),
            ("\nLoser: ", "cyan"),
            (result.loser, "red"),
            ("\nFinal Score: ", "cyan"),
            (f"{result.winner}: {result.winning_score}, {result.loser}: {result.losing_score}", "yellow"),
            ("\nRounds: ", "cyan"),
            (str(result.rounds), "yellow"),
            ("\nFatigue Costs:", "cyan"),
            (f"\n  {result.winner}: {result.fatigue_costs[result.winner]}", "yellow"),
            (f"\n  {result.loser}: {result.fatigue_costs[result.loser]}", "yellow"),
            ("\nWarping Gained:", "cyan"),
            (f"\n  {result.winner}: {result.warping_gained[result.winner]}", "red"),
            (f"\n  {result.loser}: {result.warping_gained[result.loser]}", "red"),
        )

        panel = Panel(content, title=title, border_style="magenta", padding=(1, 2))
        console.print(panel)

        # Save final character states
        character1.save()
        character2.save()

    except Exception as e:
        console.print(f"[red]Error ending Certamen: {e}[/red]")


@certamen.command()
@click.argument("character_name")
def status(character_name: str):
    """Display current Certamen status for a character."""
    try:
        character = Character.load(character_name)

        table = Table(title=f"Certamen Status: {character_name}")
        table.add_column("Aspect", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Current Fatigue", str(character.fatigue_level))
        table.add_row("Warping Points", str(getattr(character, "warping_points", 0)))

        if hasattr(character, "current_certamen"):
            table.add_row("Active Certamen", "Yes")
            table.add_row("Current Score", str(character.current_certamen.get("score", 0)))
        else:
            table.add_row("Active Certamen", "No")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
