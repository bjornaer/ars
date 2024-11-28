import click
from rich.console import Console
from rich.table import Table

from ars.character import Character
from ars.events import EventType
from ars.spell_mastery import MasteryCategory, SpellMasteryEffects

console = Console()


@click.group()
def mastery():
    """Spell mastery management commands."""
    pass


@mastery.command()
@click.argument("character_name")
@click.argument("spell_name")
def list_effects(character_name: str, spell_name: str):
    """List available mastery effects for a spell."""
    try:
        character = Character.load(character_name)
        spell = character.spells.get(spell_name)

        if not spell:
            console.print(f"[red]Spell '{spell_name}' not found for {character_name}[/red]")
            return

        table = Table(title=f"Available Mastery Effects for {spell_name}")
        table.add_column("Category", style="cyan")
        table.add_column("Effect", style="green")
        table.add_column("Level Required", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Current", style="magenta")

        current_effects = getattr(spell, "mastery_effects", [])

        for category in MasteryCategory:
            effects = SpellMasteryEffects.get_available_effects(spell.mastery_level, category)
            for effect in effects:
                table.add_row(
                    category.value,
                    effect.name,
                    str(effect.level_required),
                    effect.description,
                    "✓" if effect.name in current_effects else "",
                )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing mastery effects: {e}[/red]")


@mastery.command()
@click.argument("character_name")
@click.argument("spell_name")
@click.argument("effect_name")
def add_effect(character_name: str, spell_name: str, effect_name: str):
    """Add a mastery effect to a spell."""
    try:
        character = Character.load(character_name)
        spell = character.spells.get(spell_name)

        if not spell:
            console.print(f"[red]Spell '{spell_name}' not found[/red]")
            return

        if not hasattr(spell, "mastery_effects"):
            spell.mastery_effects = []

        effect = SpellMasteryEffects.EFFECTS.get(effect_name.lower())
        if not effect:
            console.print(f"[red]Effect '{effect_name}' not found[/red]")
            return

        if effect.level_required > spell.mastery_level:
            console.print(f"[red]Insufficient mastery level for {effect_name}[/red]")
            return

        if effect_name in spell.mastery_effects:
            console.print("[yellow]Effect already applied to spell[/yellow]")
            return

        spell.mastery_effects.append(effect_name)
        character.save()

        if character.event_manager:
            character.record_event(
                type=EventType.SPELL_MASTERY,
                description=f"Added mastery effect {effect_name} to {spell_name}",
                details={"spell": spell_name, "effect": effect_name, "mastery_level": spell.mastery_level},
            )

        console.print(f"[green]Added {effect_name} to {spell_name}[/green]")

    except Exception as e:
        console.print(f"[red]Error adding mastery effect: {e}[/red]")


@mastery.command()
@click.argument("character_name")
@click.argument("spell_name")
@click.option("--xp", type=int, default=1, help="Experience points to add")
def improve_mastery(character_name: str, spell_name: str, xp: int):
    """Improve spell mastery level."""
    try:
        character = Character.load(character_name)
        spell = character.spells.get(spell_name)

        if not spell:
            console.print(f"[red]Spell '{spell_name}' not found[/red]")
            return

        old_level = spell.mastery_level
        spell.mastery_level += xp
        character.save()

        if character.event_manager:
            character.record_event(
                type=EventType.SPELL_MASTERY,
                description=f"Improved mastery of {spell_name}",
                details={
                    "spell": spell_name,
                    "xp_gained": xp,
                    "old_level": old_level,
                    "new_level": spell.mastery_level,
                },
            )

        console.print(f"[green]Improved mastery of {spell_name} to level {spell.mastery_level}[/green]")

    except Exception as e:
        console.print(f"[red]Error improving mastery: {e}[/red]")
