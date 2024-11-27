import click
from rich.console import Console
from rich.table import Table

from ars.character import Character
from ars.spells import Duration, Range, SpellCaster, SpellRegistry, Target

console = Console()


@click.group()
def spell():
    """Spell casting and management commands."""
    pass


@spell.command()
@click.argument("character_name")
@click.argument("spell_name")
@click.option("--aura", "-a", type=int, default=0, help="Magical aura modifier")
@click.option("--stress/--no-stress", default=True, help="Use stress die")
@click.option("--modifiers", "-m", type=int, default=0, help="Additional modifiers")
def cast(character_name: str, spell_name: str, aura: int, stress: bool, modifiers: int):
    """Cast a spell with a character."""
    try:
        character = Character.load(character_name)
        spell = character.spells.get(spell_name)

        if not spell:
            console.print(f"[red]Spell '{spell_name}' not found for {character_name}[/red]")
            return

        success, result = SpellCaster.cast_spell(
            spell,
            character.techniques[spell.technique],
            character.forms[spell.form],
            aura=aura,
            modifiers=modifiers,
            stress=stress,
        )

        # Create result display
        table = Table(title=f"Spell Casting: {spell_name}")
        table.add_column("Aspect", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Roll", str(result.rolls))
        table.add_row("Multiplier", str(result.multiplier))
        table.add_row("Modifiers", str(modifiers))
        table.add_row("Aura", str(aura))
        table.add_row("Total", str(result.total))
        table.add_row("Target Level", str(spell.level))
        table.add_row("Success", "[green]Yes[/green]" if success else "[red]No[/red]")

        if result.botch:
            table.add_row("Botch!", "[red]Yes[/red]")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error casting spell: {e}[/red]")


@spell.command()
@click.argument("character_name")
@click.argument("template_name")
@click.argument("specific_name")
@click.option("--range", "-r", type=click.Choice([r.value for r in Range]), required=True)
@click.option("--duration", "-d", type=click.Choice([d.value for d in Duration]), required=True)
@click.option("--target", "-t", type=click.Choice([t.value for t in Target]), required=True)
def create(character_name: str, template_name: str, specific_name: str, range: str, duration: str, target: str):
    """Create a new spell from a template."""
    try:
        character = Character.load(character_name)
        template = SpellRegistry.get_template(template_name)

        if not template:
            console.print(f"[red]Template '{template_name}' not found[/red]")
            return

        spell = template.create_spell(specific_name, Range(range), Duration(duration), Target(target))

        # Add spell to character
        if not hasattr(character, "spells"):
            character.spells = {}
        character.spells[spell.name] = spell
        character.save()

        console.print(f"[green]Created spell '{spell.name}' for {character_name}[/green]")

    except Exception as e:
        console.print(f"[red]Error creating spell: {e}[/red]")


@spell.command()
@click.argument("character_name")
def list_spells(character_name: str):
    """List all spells known by a character."""
    try:
        character = Character.load(character_name)

        if not hasattr(character, "spells") or not character.spells:
            console.print(f"[yellow]{character_name} knows no spells[/yellow]")
            return

        table = Table(title=f"Spells Known by {character_name}")
        table.add_column("Name", style="cyan")
        table.add_column("Tech", style="magenta")
        table.add_column("Form", style="magenta")
        table.add_column("Level", style="green")
        table.add_column("Range", style="blue")
        table.add_column("Duration", style="blue")
        table.add_column("Target", style="blue")

        for spell in character.spells.values():
            table.add_row(
                spell.name, spell.technique, spell.form, str(spell.level), spell.range, spell.duration, spell.target
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing spells: {e}[/red]")
