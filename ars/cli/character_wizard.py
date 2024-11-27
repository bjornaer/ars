from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..character import Character
from ..types import Characteristic, Form, House, Technique
from ..virtues_flaws import VirtueFlaw

console = Console()


class CharacterWizard:
    """Interactive character creation wizard."""

    def __init__(self):
        self.character: Optional[Character] = None
        self.remaining_points = {"characteristics": 7, "virtues": 10, "flaws": -10, "arts": 30, "abilities": 30}

    def run(self) -> Optional[Character]:
        """Run the character creation wizard."""
        console.print(
            Panel.fit(
                "Welcome to the Ars Magica Character Creation Wizard!\n" "Let's create your character step by step."
            )
        )

        try:
            self._basic_info()
            self._characteristics()
            self._virtues_flaws()
            self._arts()
            self._abilities()
            self._final_touches()

            return self.character

        except KeyboardInterrupt:
            console.print("\n[yellow]Character creation cancelled.[/yellow]")
            return None

    def _basic_info(self) -> None:
        """Gather basic character information."""
        console.print("\n[bold]Basic Information[/bold]")

        name = Prompt.ask("Character name")
        player = Prompt.ask("Player name")
        saga = Prompt.ask("Saga name")

        # Show available houses
        houses_table = Table(title="Available Houses")
        houses_table.add_column("House")
        houses_table.add_column("Description")
        for house in House:
            houses_table.add_row(house.value, house.get_description())  # We need to add this method to House enum
        console.print(houses_table)

        house = Prompt.ask("Choose a house", choices=[h.value for h in House])

        self.character = Character(name=name, player=player, saga=saga, house=House(house))

    def _characteristics(self) -> None:
        """Choose character characteristics."""
        console.print(f"\n[bold]Characteristics[/bold] (Points remaining: {self.remaining_points['characteristics']})")

        characteristics_table = Table(title="Characteristics")
        characteristics_table.add_column("Characteristic")
        characteristics_table.add_column("Cost")
        characteristics_table.add_column("Description")

        for char in Characteristic:
            characteristics_table.add_row(
                char.value, "1 point per level", char.get_description()  # We need to add this method
            )
        console.print(characteristics_table)

        while self.remaining_points["characteristics"] > 0:
            char = Prompt.ask("Choose characteristic to modify", choices=[c.value for c in Characteristic])
            value = int(Prompt.ask(f"Value for {char} (-3 to +3)", default="0"))

            if abs(value) <= self.remaining_points["characteristics"]:
                setattr(self.character, char.lower(), value)
                self.remaining_points["characteristics"] -= abs(value)
                console.print(f"Points remaining: {self.remaining_points['characteristics']}")
            else:
                console.print("[red]Not enough points![/red]")

            if not Confirm.ask("Modify another characteristic?"):
                break

    def _virtues_flaws(self) -> None:
        """Choose virtues and flaws."""
        console.print(
            f"\n[bold]Virtues and Flaws[/bold]\n"
            f"Virtue points: {self.remaining_points['virtues']}\n"
            f"Flaw points: {self.remaining_points['flaws']}"
        )

        # Show available virtues and flaws
        virtues_table = Table(title="Available Virtues")
        virtues_table.add_column("Virtue")
        virtues_table.add_column("Cost")
        virtues_table.add_column("Description")

        flaws_table = Table(title="Available Flaws")
        flaws_table.add_column("Flaw")
        flaws_table.add_column("Points")
        flaws_table.add_column("Description")

        # Add virtues and flaws from the VirtueFlaw class
        for v in VirtueFlaw.get_virtues():
            virtues_table.add_row(v.name, str(v.cost), v.description)

        for f in VirtueFlaw.get_flaws():
            flaws_table.add_row(f.name, str(f.points), f.description)

        console.print(virtues_table)
        console.print(flaws_table)

        # Select virtues
        while self.remaining_points["virtues"] > 0:
            virtue = Prompt.ask("Choose a virtue (or 'done' to finish)", default="done")
            if virtue.lower() == "done":
                break

            v = VirtueFlaw.get_virtue(virtue)
            if v and v.cost <= self.remaining_points["virtues"]:
                self.character.add_virtue(v)
                self.remaining_points["virtues"] -= v.cost
                console.print(f"Virtue points remaining: {self.remaining_points['virtues']}")
            else:
                console.print("[red]Invalid virtue or not enough points![/red]")

        # Select flaws
        while self.remaining_points["flaws"] < 0:
            flaw = Prompt.ask("Choose a flaw (or 'done' to finish)", default="done")
            if flaw.lower() == "done":
                break

            f = VirtueFlaw.get_flaw(flaw)
            if f and (self.remaining_points["flaws"] + f.points) <= 0:
                self.character.add_flaw(f)
                self.remaining_points["flaws"] += f.points
                console.print(f"Flaw points remaining: {self.remaining_points['flaws']}")
            else:
                console.print("[red]Invalid flaw or too many points![/red]")

    def _arts(self) -> None:
        """Choose magical arts."""
        console.print(f"\n[bold]Magical Arts[/bold] " f"(Points remaining: {self.remaining_points['arts']})")

        # Show available arts
        arts_table = Table(title="Magical Arts")
        arts_table.add_column("Art")
        arts_table.add_column("Type")
        arts_table.add_column("Cost")

        for tech in Technique:
            arts_table.add_row(tech.value, "Technique", "5 exp per level")
        for form in Form:
            arts_table.add_row(form.value, "Form", "5 exp per level")

        console.print(arts_table)

        while self.remaining_points["arts"] > 0:
            art = Prompt.ask(
                "Choose art to improve (or 'done' to finish)",
                choices=[*[t.value for t in Technique], *[f.value for f in Form], "done"],
            )
            if art.lower() == "done":
                break

            value = int(Prompt.ask(f"Level for {art} (0 to {self.remaining_points['arts'] // 5})", default="0"))

            cost = value * 5
            if cost <= self.remaining_points["arts"]:
                if art in [t.value for t in Technique]:
                    self.character.techniques[art] = value
                else:
                    self.character.forms[art] = value
                self.remaining_points["arts"] -= cost
                console.print(f"Points remaining: {self.remaining_points['arts']}")
            else:
                console.print("[red]Not enough points![/red]")

    def _abilities(self) -> None:
        """Choose character abilities."""
        console.print(f"\n[bold]Abilities[/bold] " f"(Points remaining: {self.remaining_points['abilities']})")

        while self.remaining_points["abilities"] > 0:
            ability = Prompt.ask("Enter ability name (or 'done' to finish)", default="done")
            if ability.lower() == "done":
                break

            value = int(Prompt.ask(f"Level for {ability} (1 to 5)", default="1"))

            cost = value * 5
            if cost <= self.remaining_points["abilities"]:
                self.character.abilities[ability] = value
                self.remaining_points["abilities"] -= cost
                console.print(f"Points remaining: {self.remaining_points['abilities']}")
            else:
                console.print("[red]Not enough points![/red]")

    def _final_touches(self) -> None:
        """Add final character details."""
        console.print("\n[bold]Final Details[/bold]")

        age = int(Prompt.ask("Character age", default="25"))
        gender = Prompt.ask("Character gender", default="")
        nationality = Prompt.ask("Character nationality", default="")
        description = Prompt.ask("Character description", default="")

        self.character.age = age
        self.character.gender = gender
        self.character.nationality = nationality
        self.character.description = description
