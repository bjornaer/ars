import click
from rich.console import Console

from ars.dice import DiceRoller, DieType

console = Console()


@click.group()
def roll():
    """Roll dice commands."""
    pass


@roll.command()
@click.option("--num", "-n", default=1, help="Number of dice to roll")
@click.option("--stress/--no-stress", default=False, help="Use stress die")
def simple(num: int, stress: bool):
    """Roll simple or stress dice."""
    die_type = DieType.STRESS if stress else DieType.SIMPLE
    results = DiceRoller.roll_multiple(num_dice=num, die_type=die_type)

    for i, result in enumerate(results, 1):
        if stress:
            console.print(
                f"Die {i}: {result.value} (multiplier: {result.multiplier}, " f"raw rolls: {result.raw_rolls})"
            )
            if result.is_botch:
                console.print(f"[red]Botch! ({result.botch_dice} zeros)[/red]")
        else:
            console.print(f"Die {i}: {result.value}")

    if num > 1:
        total = sum(r.total for r in results)
        console.print(f"\nTotal: {total}")
