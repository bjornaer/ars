from typing import Dict, Optional

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

from ars.core.types import (
    House, Characteristic, Form, Technique, 
    AbilityType, WeaponType, ArmorType
)
from ars.core.characters.magus import Magus
from ars.core.characters.grog import Grog

console = Console()


class CharacterWizard:
    """Interactive character creation wizard."""

    def __init__(self):
        self.console = Console()

    def _get_basic_info(self) -> Dict:
        """Get basic character information."""
        console.print("\n[bold blue]Basic Information[/bold blue]")
        return {
            "name": Prompt.ask("Character Name"),
            "player": Prompt.ask("Player Name"),
            "saga": Prompt.ask("Saga Name"),
            "covenant": Prompt.ask("Covenant Name"),
            "age": IntPrompt.ask("Age", default=25)
        }

    def _get_characteristics(self) -> Dict[Characteristic, int]:
        """Get character characteristics."""
        console.print("\n[bold blue]Characteristics (-3 to +3)[/bold blue]")
        characteristics = {}
        
        for char in Characteristic:
            while True:
                value = IntPrompt.ask(
                    f"{char.value}",
                    default=0
                )
                if -3 <= value <= 3:
                    characteristics[char] = value
                    break
                console.print("[red]Value must be between -3 and +3[/red]")
                
        return characteristics

    def _get_magical_arts(self) -> tuple[Dict[Technique, int], Dict[Form, int]]:
        """Get magical arts scores for Magi."""
        techniques = {}
        forms = {}
        
        console.print("\n[bold blue]Techniques[/bold blue]")
        for tech in Technique:
            techniques[tech] = IntPrompt.ask(f"{tech.value}", default=0)
            
        console.print("\n[bold blue]Forms[/bold blue]")
        for form in Form:
            forms[form] = IntPrompt.ask(f"{form.value}", default=0)
            
        return techniques, forms

    def _get_combat_skills(self) -> tuple[Dict[WeaponType, int], Dict[ArmorType, int]]:
        """Get combat skills for Grogs."""
        weapon_skills = {}
        armor_skills = {}
        
        console.print("\n[bold blue]Weapon Skills[/bold blue]")
        for weapon in WeaponType:
            if Confirm.ask(f"Add {weapon.value} skill?"):
                weapon_skills[weapon] = IntPrompt.ask(f"{weapon.value} score", default=0)
                
        console.print("\n[bold blue]Armor Proficiency[/bold blue]")
        for armor in ArmorType:
            if Confirm.ask(f"Add {armor.value} proficiency?"):
                armor_skills[armor] = IntPrompt.ask(f"{armor.value} score", default=0)
                
        return weapon_skills, armor_skills

    def create_magus(self) -> Magus:
        """Create a Magus character."""
        info = self._get_basic_info()
        
        # Get House
        house_name = Prompt.ask(
            "House",
            choices=[h.value for h in House]
        )
        house = House(house_name)
        
        characteristics = self._get_characteristics()
        techniques, forms = self._get_magical_arts()
        
        return Magus(
            **info,
            house=house,
            characteristics=characteristics,
            techniques=techniques,
            forms=forms
        )

    def create_grog(self) -> Grog:
        """Create a Grog character."""
        info = self._get_basic_info()
        characteristics = self._get_characteristics()
        weapon_skills, armor_skills = self._get_combat_skills()
        
        return Grog(
            **info,
            characteristics=characteristics,
            weapon_skills=weapon_skills,
            armor_proficiency=armor_skills
        )

    def run(self) -> Optional[Magus | Grog]:
        """Run the character creation wizard."""
        console.print("[bold]Character Creation Wizard[/bold]")
        
        char_type = Prompt.ask(
            "Character Type",
            choices=["Magus", "Grog"]
        )
        
        try:
            if char_type == "Magus":
                character = self.create_magus()
            else:
                character = self.create_grog()
                
            return character
            
        except Exception as e:
            console.print(f"[red]Error creating character: {e}[/red]")
            return None
