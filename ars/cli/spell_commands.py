from typing import Optional

import click
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from ars.core.types import Duration, Form, Range, Target, Technique
from ars.core.spells import Spell, SpellEffect, SpellCaster
from ars.core.characters.magus import Magus
from ars.core.character import Character
from ars.cli.state import get_active_character, set_active_character, get_character_dir
from ars.core.character import CharacterError

console = Console()


@click.group()
def spell():
    """Spell management and casting commands."""
    pass


def get_character_or_active(character_name: Optional[str]) -> Character:
    """Get specified character or active character."""
    if character_name is None:
        active_char = get_active_character()
        if active_char is None:
            raise CharacterError("No character specified and no active character set. Use 'ars use <character>' first.")
        character_name = active_char
        
    return Character.load(character_name, directory=get_character_dir())


@spell.command()
@click.argument("character_name", required=False)
def create(character_name: Optional[str]):
    """Create a new spell for a character."""
    try:
        character = get_character_or_active(character_name)
        if not isinstance(character, Magus):
            console.print("[red]Only Magi can learn spells[/red]")
            return

        # Basic spell information
        console.print("[bold blue]Create New Spell[/bold blue]")
        name = Prompt.ask("Spell Name")
        
        # Technique selection
        technique = Prompt.ask(
            "Technique",
            choices=[t.value for t in Technique]
        )
        
        # Form selection
        form = Prompt.ask(
            "Form",
            choices=[f.value for f in Form]
        )
        
        # Level
        level = IntPrompt.ask("Spell Level", default=5)
        
        # Range selection
        range_type = Prompt.ask(
            "Range",
            choices=[r.value for r in Range]
        )
        
        # Duration selection
        duration_type = Prompt.ask(
            "Duration",
            choices=[d.value for d in Duration]
        )
        
        # Target selection
        target_type = Prompt.ask(
            "Target",
            choices=[t.value for t in Target]
        )
        
        # Description
        description = Prompt.ask("Description")
        
        # Effects
        effects = []
        while Confirm.ask("Add spell effect?"):
            effect = SpellEffect(
                base_effect=Prompt.ask("Effect description"),
                magnitude=IntPrompt.ask("Magnitude", default=1)
            )
            
            # Add modifiers
            while Confirm.ask("Add effect modifier?"):
                modifier_name = Prompt.ask("Modifier name")
                modifier_value = IntPrompt.ask("Modifier value")
                effect.special_modifiers[modifier_name] = modifier_value
                
            effects.append(effect)

        # Create the spell
        spell = Spell(
            name=name,
            technique=Technique(technique),
            form=Form(form),
            level=level,
            range=Range(range_type),
            duration=Duration(duration_type),
            target=Target(target_type),
            description=description,
            effects=effects
        )

        # Add to character's repertoire
        character.learn_spell(spell)
        character.save()

        console.print(f"[green]Created spell '{name}' for {character_name}[/green]")

    except Exception as e:
        console.print(f"[red]Error creating spell: {e}[/red]")


@spell.command()
@click.argument("character_name", required=False)
@click.argument("spell_name")
@click.option("--aura", "-a", type=int, default=0, help="Magical aura modifier")
@click.option("--stress/--no-stress", default=True, help="Use stress die")
@click.option("--modifiers", "-m", type=int, default=0, help="Additional modifiers")
@click.option("--defiant", is_flag=True, help="Cast spell defiantly")
@click.option("--ceremonial", is_flag=True, help="Cast as ceremonial ritual")
def cast(
    character_name: Optional[str],
    spell_name: str,
    aura: int,
    stress: bool,
    modifiers: int,
    defiant: bool,
    ceremonial: bool
):
    """Cast a spell."""
    try:
        character = get_character_or_active(character_name)
        if not isinstance(character, Magus):
            console.print("[red]Only Magi can cast spells[/red]")
            return

        spell = character.spells.get(spell_name)
        if not spell:
            console.print(f"[red]Spell '{spell_name}' not found[/red]")
            return

        # Handle different casting methods
        if ceremonial and not spell.ritual:
            console.print("[red]Only ritual spells can be cast ceremonially[/red]")
            return

        if ceremonial:
            # Get participants for ceremonial casting
            participants = []
            while Confirm.ask("Add participant?"):
                participant_name = Prompt.ask("Participant name")
                try:
                    participant = Character.load(participant_name)
                    if isinstance(participant, Magus):
                        participants.append(participant)
                    else:
                        console.print("[red]Only Magi can participate in ceremonial magic[/red]")
                except Exception:
                    console.print(f"[red]Could not load character '{participant_name}'[/red]")

            result = SpellCaster.cast_ceremonial(spell, character, participants, aura, modifiers)
        elif defiant:
            result = SpellCaster.cast_defiant(spell, character, aura, modifiers)
        else:
            result = SpellCaster.cast_spell(spell, character, aura, modifiers, stress)

        # Display results
        table = Table(title=f"Casting Results: {spell_name}")
        table.add_column("Aspect", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Casting Total", str(result.total))
        table.add_row("Target Level", str(spell.level))
        table.add_row("Success", "[green]Yes[/green]" if result.success else "[red]No[/red]")
        
        if result.botch:
            table.add_row("Botch!", "[red]Yes[/red]")
            
        if result.warping_gained:
            table.add_row("Warping Gained", f"[red]{result.warping_gained}[/red]")
            
        if result.fatigue_cost:
            table.add_row("Fatigue Cost", str(result.fatigue_cost))

        console.print(table)

        # Save character state
        character.save()

    except Exception as e:
        console.print(f"[red]Error casting spell: {e}[/red]")


@spell.command()
@click.argument("character_name", required=False)
def list_spells(character_name: Optional[str]):
    """List all spells known by a character."""
    try:
        character = get_character_or_active(character_name)
        if not isinstance(character, Magus):
            console.print("[red]Only Magi can know spells[/red]")
            return

        if not character.spells:
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
        table.add_column("Mastery", style="yellow")

        for spell in character.spells.values():
            table.add_row(
                spell.name,
                spell.technique.value,
                spell.form.value,
                str(spell.level),
                spell.range.value,
                spell.duration.value,
                spell.target.value,
                str(spell.mastery_level)
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing spells: {e}[/red]")


@spell.command()
@click.argument("character_name", required=False)
@click.argument("spell_name")
def show_spell(character_name: Optional[str], spell_name: str):
    """Show detailed information about a spell."""
    try:
        character = get_character_or_active(character_name)
        if not isinstance(character, Magus):
            console.print("[red]Only Magi can know spells[/red]")
            return

        spell = character.spells.get(spell_name)
        if not spell:
            console.print(f"[red]Spell '{spell_name}' not found[/red]")
            return

        table = Table(title=f"Spell Details: {spell_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Technique", spell.technique.value)
        table.add_row("Form", spell.form.value)
        table.add_row("Level", str(spell.level))
        table.add_row("Range", spell.range.value)
        table.add_row("Duration", spell.duration.value)
        table.add_row("Target", spell.target.value)
        table.add_row("Description", spell.description)
        table.add_row("Mastery Level", str(spell.mastery_level))

        if spell.effects:
            effects_table = Table(title="Spell Effects")
            effects_table.add_column("Effect", style="cyan")
            effects_table.add_column("Magnitude", style="green")
            effects_table.add_column("Modifiers", style="yellow")

            for effect in spell.effects:
                modifiers_str = ", ".join(
                    f"{k}: {v}" for k, v in effect.special_modifiers.items()
                )
                effects_table.add_row(
                    effect.base_effect,
                    str(effect.magnitude),
                    modifiers_str or "None"
                )

            console.print(table)
            console.print("\n")
            console.print(effects_table)
        else:
            console.print(table)

    except Exception as e:
        console.print(f"[red]Error showing spell details: {e}[/red]") 