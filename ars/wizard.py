from rich.console import Console
from rich.prompt import Confirm, Prompt

from .character import AbilityType, Character
from .spells import Form, Technique

console = Console()


class CharacterWizard:
    """Interactive character creation wizard."""

    def __init__(self):
        self.console = Console()

    def _prompt_basic_info(self) -> dict[str, str]:
        """Prompt for basic character information."""
        console.print("\n[bold blue]Basic Information[/bold blue]")
        return {
            "name": Prompt.ask("Character Name"),
            "player": Prompt.ask("Player Name"),
            "saga": Prompt.ask("Saga Name"),
            "covenant": Prompt.ask("Covenant Name"),
            "age": int(Prompt.ask("Age", default="25")),
        }

    def _prompt_characteristics(self) -> dict[str, int]:
        """Prompt for character characteristics."""
        console.print("\n[bold blue]Characteristics (-3 to +3)[/bold blue]")
        characteristics = {}

        for char in [
            "intelligence",
            "perception",
            "strength",
            "stamina",
            "presence",
            "communication",
            "dexterity",
            "quickness",
        ]:
            while True:
                try:
                    value = int(Prompt.ask(f"{char.capitalize()}", default="0"))
                    if -3 <= value <= 3:
                        characteristics[char] = value
                        break
                    console.print("[red]Value must be between -3 and +3[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")

        return characteristics

    def _prompt_arts(self) -> tuple[dict[str, int], dict[str, int]]:
        """Prompt for magical arts."""
        console.print("\n[bold blue]Magical Arts (0+)[/bold blue]")

        techniques = {}
        console.print("\n[bold]Techniques:[/bold]")
        for tech in Technique:
            value = int(Prompt.ask(f"{tech.value}", default="0"))
            techniques[tech.value] = value

        forms = {}
        console.print("\n[bold]Forms:[/bold]")
        for form in Form:
            value = int(Prompt.ask(f"{form.value}", default="0"))
            forms[form.value] = value

        return techniques, forms

    def _prompt_abilities(self) -> dict[AbilityType, dict[str, int]]:
        """Prompt for abilities."""
        console.print("\n[bold blue]Abilities[/bold blue]")
        abilities = {t: {} for t in AbilityType}

        for ability_type in AbilityType:
            console.print(f"\n[bold]{ability_type.name} Abilities:[/bold]")
            while Confirm.ask("Add another ability?"):
                name = Prompt.ask("Ability name")
                value = int(Prompt.ask("Score", default="1"))
                abilities[ability_type][name] = value

        return abilities

    def create_character(self) -> Character:
        """Run the character creation wizard."""
        console.print("[bold green]Welcome to the Ars Magica Character Creator![/bold green]")

        # Get basic information
        basic_info = self._prompt_basic_info()

        # Create character instance
        char = Character(**basic_info)

        # Get characteristics
        characteristics = self._prompt_characteristics()
        for name, value in characteristics.items():
            setattr(char, name, value)

        # Get arts
        techniques, forms = self._prompt_arts()
        char.techniques = techniques
        char.forms = forms

        # Get abilities
        char.abilities = self._prompt_abilities()

        # Virtues and Flaws
        console.print("\n[bold blue]Virtues and Flaws[/bold blue]")
        while Confirm.ask("Add a virtue?"):
            virtue = Prompt.ask("Enter virtue")
            char.virtues.append(virtue)

        while Confirm.ask("Add a flaw?"):
            flaw = Prompt.ask("Enter flaw")
            char.flaws.append(flaw)

        return char
