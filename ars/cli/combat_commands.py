import click
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from typing import Optional

from ars.core.character import Character
from ars.core.characters.grog import Grog
from ars.core.types import WeaponType, ArmorType
from ars.core.combat import CombatManager, CombatRound, CombatResult
from ars.cli.combat_wizard import CombatWizard
from ars.cli.state import get_active_character, set_active_character

console = Console()
combat_wizard = CombatWizard()

@click.group()
def combat():
    """Combat management commands."""
    pass


@combat.command()
@click.argument("character_name")
@click.argument("armor_name")
@click.option("--type", "-t", type=click.Choice([t.value for t in ArmorType]), required=True)
@click.option("--protection", "-p", type=int, default=0, help="Protection value")
@click.option("--load", "-l", type=int, default=0, help="Load/encumbrance value")
@click.option("--modifiers", "-m", type=int, default=0, help="Additional modifiers")
def add_armor(
    character_name: str,
    armor_name: str,
    type: str,
    protection: int,
    load: int,
    modifiers: int
):
    """Add armor to a character's inventory."""
    try:
        character = Character.load(character_name)
        
        armor = {
            "type": ArmorType(type),
            "protection": protection,
            "load": load,
            "modifiers": modifiers
        }
        
        character.add_armor(armor_name, armor)
        character.save()
        
        console.print(f"[green]Added armor '{armor_name}' to {character_name}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error adding armor: {e}[/red]")


@combat.command()
@click.argument("attacker_name", required=False)
@click.argument("defender_name", required=False)
@click.option("--weapon", "-w", help="Weapon name for attacker")
@click.option("--stress/--no-stress", default=True, help="Use stress die")
@click.option("--modifiers", "-m", type=int, default=0, help="Additional modifiers")
@click.option("--quick/--no-quick", default=False, help="Quick combat mode without loading characters")
def attack(
    attacker_name: Optional[str],
    defender_name: str,
    weapon: str,
    stress: bool,
    modifiers: int,
    quick: bool
):
    """Execute an attack between two characters."""
    try:
        if attacker_name is None:
            attacker = get_active_character()
        else:
            attacker = Character.load(attacker_name)
            
        defender = Character.load(defender_name)
        
        # Get weapon if not specified
        if not weapon:
            weapon = combat_wizard.get_weapon(attacker)
            if not weapon:
                return

        weapon_obj = attacker.weapons.get(weapon)
        if not weapon_obj:
            console.print(f"[red]Weapon '{weapon}' not found[/red]")
            return

        # Execute attack
        result = CombatManager.resolve_attack(
            attacker=attacker,
            defender=defender,
            weapon=weapon_obj,
            stress=stress,
            modifiers=modifiers
        )

        # Display detailed results
        combat_wizard.display_combat_results(result, attacker, defender, weapon_obj)

        # Update character states if they are saved characters
        if not quick and all([attacker_name, defender_name]):
            if result.is_hit:
                defender.take_damage(result.damage_total)
                defender.save()
                console.print(f"[yellow]Updated {defender_name}'s state[/yellow]")

    except Exception as e:
        console.print(f"[red]Error processing combat: {e}[/red]")


@combat.command()
@click.argument("character_name")
def show_equipment(character_name: str):
    """Display a character's combat equipment."""
    try:
        character = Character.load(character_name)
        
        # Weapons table
        if hasattr(character, 'weapons') and character.weapons:
            weapons_table = Table(title=f"{character_name}'s Weapons")
            weapons_table.add_column("Name", style="cyan")
            weapons_table.add_column("Type", style="yellow")
            weapons_table.add_column("Init", style="green")
            weapons_table.add_column("Attack", style="red")
            weapons_table.add_column("Defense", style="blue")
            weapons_table.add_column("Damage", style="magenta")
            
            for name, weapon in character.weapons.items():
                weapons_table.add_row(
                    name,
                    weapon.type.value,
                    str(weapon.init_mod),
                    str(weapon.attack_mod),
                    str(weapon.defense_mod),
                    str(weapon.damage_mod)
                )
            
            console.print(weapons_table)
        else:
            console.print("[yellow]No weapons equipped[/yellow]")
            
        # Armor table
        if hasattr(character, 'armor') and character.armor:
            armor_table = Table(title=f"{character_name}'s Armor")
            armor_table.add_column("Name", style="cyan")
            armor_table.add_column("Type", style="yellow")
            armor_table.add_column("Protection", style="green")
            armor_table.add_column("Load", style="red")
            armor_table.add_column("Modifiers", style="blue")
            
            for name, armor in character.armor.items():
                armor_table.add_row(
                    name,
                    armor.type.value,
                    str(armor.protection),
                    str(armor.load),
                    str(armor.modifiers)
                )
            
            console.print("\n", armor_table)
        else:
            console.print("[yellow]No armor equipped[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error showing equipment: {e}[/red]") 