from typing import Dict

import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from ars.character import Character, CharacterNotFoundError
from ars.combat import CombatManager, CombatRound, CombatStats, Weapon, WeaponType

console = Console()


@click.group()
def combat():
    """Combat management commands."""
    pass


@combat.command()
@click.argument("attacker_name")
@click.argument("defender_name")
@click.option("--weapon", "-w", help="Weapon name for attacker")
@click.option("--stress/--no-stress", default=True, help="Use stress die")
@click.option("--modifiers", "-m", type=int, default=0, help="Additional modifiers")
def attack(attacker_name: str, defender_name: str, weapon: str, stress: bool, modifiers: int):
    """Perform an attack between two characters."""
    try:
        attacker = Character.load(attacker_name)
        defender = Character.load(defender_name)

        # Get weapon stats (assuming weapons are stored with character)
        if not hasattr(attacker, "weapons") or weapon not in attacker.weapons:
            console.print(f"[red]Weapon '{weapon}' not found for {attacker_name}[/red]")
            return

        weapon_stats = attacker.weapons[weapon]

        # Perform attack roll
        attack_result = CombatManager.attack_roll(
            attacker.weapon_skills.get(weapon, 0), weapon_stats, modifiers, stress
        )

        # Perform defense roll
        defense_result = CombatManager.defense_roll(
            defender.defense_skill, weapon_stats, 0, stress  # No modifiers for now
        )

        # Calculate damage
        damage = CombatManager.calculate_damage(
            attacker.characteristics.get("Strength", 0), weapon_stats, attack_result, defense_result, defender.soak
        )

        # Display results
        table = Table(title="Combat Results")
        table.add_column("Action", style="cyan")
        table.add_column("Roll", style="yellow")
        table.add_column("Total", style="green")

        table.add_row("Attack", str(attack_result.rolls), str(attack_result.total))
        table.add_row("Defense", str(defense_result.rolls), str(defense_result.total))

        if attack_result.botch or defense_result.botch:
            table.add_row("Botch!", "[red]Attack[/red]" if attack_result.botch else "[red]Defense[/red]", "")

        if damage > 0:
            table.add_row("Damage", "", f"[red]{damage}[/red]")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error processing combat: {e}[/red]")


@combat.command()
def init_round():
    """Initialize a new combat round."""
    try:
        round = CombatRound()
        participants: Dict[str, Dict] = {}

        while True:
            name = Prompt.ask("Enter participant name (or 'done')")
            if name.lower() == "done":
                break

            try:
                character = Character.load(name)
            except CharacterNotFoundError:
                console.print(f"[red]Character '{name}' not found[/red]")
                continue
            except Exception as e:
                console.print(f"[red]Error loading character '{name}': {e}[/red]")
                continue

            weapon_name = Prompt.ask("Weapon")
            if not hasattr(character, "weapons") or weapon_name not in character.weapons:
                console.print(f"[red]Weapon '{weapon_name}' not found[/red]")
                continue

            weapon = character.weapons[weapon_name]

            # Calculate initiative
            init_result = CombatManager.calculate_initiative(character.characteristics.get("Quickness", 0), weapon)

            stats = CombatStats(
                initiative_total=init_result.total,
                attack_total=character.weapon_skills.get(weapon_name, 0) + weapon.attack_modifier,
                defense_total=character.defense_skill + weapon.defense_modifier,
                damage_total=character.characteristics.get("Strength", 0) + weapon.damage_modifier,
                soak_total=character.soak,
            )

            round.add_participant(name, stats)
            participants[name] = {"character": character, "weapon": weapon, "stats": stats}

        # Display initiative order
        table = Table(title="Combat Order")
        table.add_column("Order", style="cyan")
        table.add_column("Name", style="yellow")
        table.add_column("Initiative", style="green")
        table.add_column("Weapon", style="blue")

        current_turn = 1
        while True:
            next_up = round.next_turn()
            if not next_up:
                break

            name, stats = next_up
            table.add_row(str(current_turn), name, str(stats.initiative_total), participants[name]["weapon"].name)
            current_turn += 1

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error initializing combat round: {e}[/red]")


@combat.command()
@click.argument("character_name")
@click.argument("weapon_name")
@click.option("--type", "-t", type=click.Choice([t.name for t in WeaponType]), required=True)
@click.option("--init", "-i", type=int, default=0, help="Initiative modifier")
@click.option("--attack", "-a", type=int, default=0, help="Attack modifier")
@click.option("--defense", "-d", type=int, default=0, help="Defense modifier")
@click.option("--damage", "-m", type=int, default=0, help="Damage modifier")
@click.option("--range", "-r", help="Weapon range")
@click.option("--strength-req", "-s", type=int, default=0, help="Strength requirement")
def add_weapon(
    character_name: str,
    weapon_name: str,
    type: str,
    init: int,
    attack: int,
    defense: int,
    damage: int,
    range: str,
    strength_req: int,
):
    """Add a weapon to a character's inventory."""
    try:
        character = Character.load(character_name)

        weapon = Weapon(
            name=weapon_name,
            weapon_type=WeaponType[type],
            init_modifier=init,
            attack_modifier=attack,
            defense_modifier=defense,
            damage_modifier=damage,
            range=range,
            strength_requirement=strength_req,
        )

        if not hasattr(character, "weapons"):
            character.weapons = {}

        character.weapons[weapon_name] = weapon
        character.save()

        console.print(f"[green]Added weapon '{weapon_name}' to {character_name}[/green]")

    except Exception as e:
        console.print(f"[red]Error adding weapon: {e}[/red]")
