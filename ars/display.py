from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from .character import AbilityType, Character
from .faces import FaceGenerator, House


class CharacterDisplay:
    """Handles the terminal display of character information."""

    def __init__(self, character: Character):
        self.character = character
        self.console = Console()

    def _create_header(self) -> Panel:
        """Create the character header panel."""
        grid = Table.grid(padding=(0, 2))
        grid.add_column("Label", style="bold blue")
        grid.add_column("Value")

        grid.add_row("Name:", self.character.name)
        grid.add_row("Player:", self.character.player)
        grid.add_row("Saga:", self.character.saga)
        grid.add_row("Covenant:", self.character.covenant)
        grid.add_row("Age:", str(self.character.age))

        return Panel(grid, title="[bold blue]Character Information[/bold blue]", border_style="blue")

    def _create_characteristics_panel(self) -> Panel:
        """Create the characteristics panel."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Characteristic")
        table.add_column("Score", justify="center")

        characteristics = [
            ("Intelligence", self.character.intelligence),
            ("Perception", self.character.perception),
            ("Strength", self.character.strength),
            ("Stamina", self.character.stamina),
            ("Presence", self.character.presence),
            ("Communication", self.character.communication),
            ("Dexterity", self.character.dexterity),
            ("Quickness", self.character.quickness),
        ]

        for name, value in characteristics:
            modifier = "+" if value > 0 else ""
            table.add_row(name, f"{modifier}{value}")

        return Panel(table, title="[bold magenta]Characteristics[/bold magenta]", border_style="magenta")

    def _create_arts_panel(self) -> Panel:
        """Create the magical arts panel."""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Art")
        table.add_column("Score", justify="center")

        # Techniques
        table.add_section()
        for tech, value in self.character.techniques.items():
            table.add_row(f"[bold]{tech}[/bold]", str(value))

        # Forms
        table.add_section()
        for form, value in self.character.forms.items():
            table.add_row(form, str(value))

        return Panel(table, title="[bold cyan]Magical Arts[/bold cyan]", border_style="cyan")

    def _create_abilities_panel(self) -> Panel:
        """Create the abilities panel."""
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Type")
        table.add_column("Ability")
        table.add_column("Score", justify="center")

        for ability_type in AbilityType:
            abilities = self.character.abilities[ability_type]
            if abilities:
                table.add_section()
                type_name = ability_type.name.capitalize()
                for ability, score in abilities.items():
                    table.add_row(f"[bold]{type_name}[/bold]", ability, str(score))

        return Panel(table, title="[bold green]Abilities[/bold green]", border_style="green")

    def _create_spells_panel(self) -> Panel:
        """Create the spells panel."""
        table = Table(show_header=True, header_style="bold yellow")
        table.add_column("Name")
        table.add_column("Technique")
        table.add_column("Form")
        table.add_column("Level", justify="center")
        table.add_column("Range")
        table.add_column("Duration")
        table.add_column("Target")

        for spell in self.character.spells:
            table.add_row(
                spell.name, spell.technique, spell.form, str(spell.level), spell.range, spell.duration, spell.target
            )

        return Panel(table, title="[bold yellow]Spells[/bold yellow]", border_style="yellow")

    def _create_personality_panel(self) -> Panel:
        """Create the personality traits panel."""
        table = Table(show_header=True, header_style="bold red")
        table.add_column("Trait")
        table.add_column("Score", justify="center")

        for trait, score in self.character.personality_traits.items():
            table.add_row(trait, str(score))

        return Panel(table, title="[bold red]Personality Traits[/bold red]", border_style="red")

    def _create_virtues_flaws_panel(self) -> Panel:
        """Create the virtues and flaws panel."""
        table = Table(show_header=True, header_style="bold")
        table.add_column("Virtues")
        table.add_column("Flaws")

        # Zip virtues and flaws, padding shorter list with empty strings
        max_len = max(len(self.character.virtues), len(self.character.flaws))
        virtues = self.character.virtues + [""] * (max_len - len(self.character.virtues))
        flaws = self.character.flaws + [""] * (max_len - len(self.character.flaws))

        for virtue, flaw in zip(virtues, flaws, strict=False):
            table.add_row(f"[green]{virtue}[/green]" if virtue else "", f"[red]{flaw}[/red]" if flaw else "")

        return Panel(table, title="[bold]Virtues & Flaws[/bold]", border_style="white")

    def _create_face_panel(self, house: House) -> Panel:
        """Create panel with character face."""
        face = FaceGenerator.get_face(house, self.character)
        return Panel(face, title="[bold cyan]Magus Visage[/bold cyan]", border_style="cyan")

    def show(self, house: House) -> None:
        """Display the complete character sheet with face."""
        layout = Layout()

        # Create main layout with face
        layout.split_column(Layout(name="header", size=6), Layout(name="face_and_body"))

        # Split into face and body
        layout["face_and_body"].split_row(Layout(name="face", size=30), Layout(name="body"))

        # Split body into left and right columns
        layout["body"].split_row(Layout(name="left", ratio=1), Layout(name="right", ratio=1))

        # Split left column
        layout["left"].split_column(
            Layout(name="characteristics"), Layout(name="abilities"), Layout(name="personality")
        )

        # Split right column
        layout["right"].split_column(Layout(name="arts"), Layout(name="spells"), Layout(name="virtues_flaws"))

        # Assign panels to layout
        layout["header"].update(self._create_header())
        layout["face"].update(self._create_face_panel(house))
        layout["characteristics"].update(self._create_characteristics_panel())
        layout["arts"].update(self._create_arts_panel())
        layout["abilities"].update(self._create_abilities_panel())
        layout["spells"].update(self._create_spells_panel())
        layout["personality"].update(self._create_personality_panel())
        layout["virtues_flaws"].update(self._create_virtues_flaws_panel())

        # Render layout
        self.console.print(layout)
