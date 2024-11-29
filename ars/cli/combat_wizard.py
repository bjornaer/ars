from dataclasses import dataclass
from typing import Optional, Tuple, Dict

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from ars.core.character import Character
from ars.core.types import WeaponType, ArmorType
from ars.core.combat import CombatResult

console = Console()


@dataclass
class TemporaryCombatant:
    """Temporary character for quick combat."""
    name: str
    weapon_skill: int
    defense_skill: int
    strength: int
    soak: int
    weapons: Dict[str, dict] = None
    armor: Dict[str, dict] = None

    @classmethod
    def from_prompt(cls, name: str = None) -> "TemporaryCombatant":
        """Create temporary combatant from user input."""
        if not name:
            name = Prompt.ask("Combatant name")
            
        console.print(f"\n[bold]Enter stats for {name}:[/bold]")
        return cls(
            name=name,
            weapon_skill=IntPrompt.ask("Weapon skill", default=0),
            defense_skill=IntPrompt.ask("Defense skill", default=0),
            strength=IntPrompt.ask("Strength", default=0),
            soak=IntPrompt.ask("Soak", default=0)
        )


class CombatWizard:
    """Wizard for handling combat setup and display."""

    def get_combatants(
        self,
        attacker_name: Optional[str],
        defender_name: Optional[str]
    ) -> Tuple[Character | TemporaryCombatant, Character | TemporaryCombatant]:
        """Get or create combatants for the fight."""
        
        # Handle attacker
        attacker = None
        if attacker_name:
            try:
                attacker = Character.load(attacker_name)
            except Exception:
                console.print(f"[yellow]Could not load {attacker_name}, using temporary stats[/yellow]")
        
        if not attacker:
            attacker = TemporaryCombatant.from_prompt(attacker_name)
            self._add_temporary_weapon(attacker)
            
        # Handle defender
        defender = None
        if defender_name:
            try:
                defender = Character.load(defender_name)
            except Exception:
                console.print(f"[yellow]Could not load {defender_name}, using temporary stats[/yellow]")
                
        if not defender:
            defender = TemporaryCombatant.from_prompt(defender_name)
            if Confirm.ask("Add armor to defender?"):
                self._add_temporary_armor(defender)
                
        return attacker, defender

    def get_weapon(self, attacker: Character | TemporaryCombatant) -> Optional[str]:
        """Get weapon choice for attacker."""
        if not hasattr(attacker, 'weapons') or not attacker.weapons:
            if isinstance(attacker, TemporaryCombatant):
                self._add_temporary_weapon(attacker)
            else:
                console.print("[red]Attacker has no weapons[/red]")
                return None
                
        weapons = list(attacker.weapons.keys())
        return Prompt.ask(
            "Choose weapon",
            choices=weapons
        )

    def _add_temporary_weapon(self, combatant: TemporaryCombatant) -> None:
        """Add a temporary weapon to a combatant."""
        console.print("\n[bold]Add weapon:[/bold]")
        
        weapon_type = Prompt.ask(
            "Weapon type",
            choices=[t.value for t in WeaponType]
        )
        
        weapon = {
            "type": WeaponType(weapon_type),
            "init_mod": IntPrompt.ask("Initiative modifier", default=0),
            "attack_mod": IntPrompt.ask("Attack modifier", default=0),
            "defense_mod": IntPrompt.ask("Defense modifier", default=0),
            "damage_mod": IntPrompt.ask("Damage modifier", default=0)
        }
        
        if not combatant.weapons:
            combatant.weapons = {}
            
        weapon_name = Prompt.ask("Weapon name")
        combatant.weapons[weapon_name] = weapon

    def _add_temporary_armor(self, combatant: TemporaryCombatant) -> None:
        """Add temporary armor to a combatant."""
        console.print("\n[bold]Add armor:[/bold]")
        
        armor_type = Prompt.ask(
            "Armor type",
            choices=[t.value for t in ArmorType]
        )
        
        armor = {
            "type": ArmorType(armor_type),
            "protection": IntPrompt.ask("Protection value", default=0),
            "load": IntPrompt.ask("Load value", default=0),
            "modifiers": IntPrompt.ask("Additional modifiers", default=0)
        }
        
        if not combatant.armor:
            combatant.armor = {}
            
        armor_name = Prompt.ask("Armor name")
        combatant.armor[armor_name] = armor

    def display_combat_results(
        self,
        result: CombatResult,
        attacker: Character | TemporaryCombatant,
        defender: Character | TemporaryCombatant,
        weapon: dict
    ) -> None:
        """Display detailed combat results."""
        # Main results table
        table = Table(title=f"Combat Results: {attacker.name} vs {defender.name}")
        table.add_column("Action", style="cyan")
        table.add_column("Roll", style="yellow")
        table.add_column("Modifiers", style="blue")
        table.add_column("Total", style="green")

        # Attack details
        table.add_row(
            "Attack",
            str(result.attack_roll),
            f"+{weapon['attack_mod']} (weapon)\n+{attacker.weapon_skill} (skill)",
            str(result.attack_total)
        )

        # Defense details
        defense_mods = f"+{defender.defense_skill} (skill)"
        if hasattr(defender, 'armor') and defender.armor:
            armor = next(iter(defender.armor.values()))  # Get first armor
            defense_mods += f"\n{armor['modifiers']} (armor)"
            
        table.add_row(
            "Defense",
            str(result.defense_roll),
            defense_mods,
            str(result.defense_total)
        )
        
        if result.is_hit:
            # Damage details
            damage_mods = f"+{weapon['damage_mod']} (weapon)\n+{attacker.strength} (str)"
            soak_details = str(defender.soak)
            if hasattr(defender, 'armor') and defender.armor:
                armor = next(iter(defender.armor.values()))
                soak_details += f" (+{armor['protection']} armor)"
                
            table.add_row(
                "Damage",
                str(result.damage_roll),
                f"Mods: {damage_mods}\nSoak: {soak_details}",
                f"[red]{result.damage_total}[/red]"
            )
            
        if result.is_botch:
            table.add_row(
                "Botch!",
                "[red]Yes[/red]",
                result.botch_details or "",
                ""
            )

        console.print(table) 