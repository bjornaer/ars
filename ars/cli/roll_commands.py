import click
from rich.console import Console
from rich.table import Table

from ars.core.dice import DiceRoller, DieType

console = Console()


@click.group()
def roll():
    """Dice rolling commands."""
    pass


@roll.command()
@click.option("--num", "-n", default=1, help="Number of dice to roll")
@click.option("--stress/--no-stress", default=False, help="Use stress die")
@click.option("--modifier", "-m", type=int, default=0, help="Roll modifier")
def dice(num: int, stress: bool, modifier: int):
    """Roll simple or stress dice."""
    try:
        die_type = DieType.STRESS if stress else DieType.SIMPLE
        results = DiceRoller.roll_multiple(
            num_dice=num,
            die_type=die_type,
            modifier=modifier
        )

        table = Table(title="Dice Results")
        table.add_column("Die", style="cyan")
        table.add_column("Roll", style="yellow")
        table.add_column("Multiplier", style="blue")
        table.add_column("Total", style="green")
        
        total = 0
        for i, result in enumerate(results, 1):
            if stress:
                table.add_row(
                    f"Die {i}",
                    str(result.roll),
                    str(result.multiplier),
                    str(result.total)
                )
                if result.is_botch:
                    table.add_row(
                        "Botch!",
                        f"[red]{result.botch_dice} zeros[/red]",
                        "",
                        ""
                    )
            else:
                table.add_row(
                    f"Die {i}",
                    str(result.roll),
                    "1",
                    str(result.total)
                )
                
            total += result.total

        if modifier:
            table.add_row(
                "Modifier",
                str(modifier),
                "",
                str(modifier)
            )
            total += modifier

        if num > 1 or modifier:
            table.add_row(
                "Final Total",
                "",
                "",
                f"[bold green]{total}[/bold green]"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error rolling dice: {e}[/red]")


@roll.command()
@click.option("--botch-dice", "-b", type=int, default=1, help="Number of botch dice")
def botch(botch_dice: int):
    """Roll for a botch check."""
    try:
        results = DiceRoller.roll_botch(botch_dice)
        
        table = Table(title="Botch Check")
        table.add_column("Die", style="cyan")
        table.add_column("Roll", style="yellow")
        
        zeros = 0
        for i, roll in enumerate(results, 1):
            table.add_row(
                f"Die {i}",
                str(roll)
            )
            if roll == 0:
                zeros += 1

        is_botch = zeros > 0
        table.add_row(
            "Result",
            f"[red]BOTCH![/red]" if is_botch else "[green]No Botch[/green]"
        )
        
        if is_botch:
            table.add_row(
                "Severity",
                f"[red]{zeros} zeros[/red]"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error rolling botch: {e}[/red]") 