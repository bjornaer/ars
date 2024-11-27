from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from .laboratory import LabFeature, Laboratory


class LabVisualization:
    """Handles laboratory visualization."""

    # ASCII art templates for different lab features
    LAB_TEMPLATES = {
        "basic": """
        ╭──────────────────────────────────╮
        │   [⚗]    ┌─────┐    📚    [⚗]   │
        │          │     │     ┌─┐        │
        │   📜     │     │     │ │   🔮   │
        │    ┌─────┘     └─────┐ │        │
        │    │      Lab       │ │   ⚛    │
        │    │    Central     │ └─┐  │    │
        │ 🧪  │     Area      │   │  │    │
        │    │               │   │ 🌿    │
        │    └───────────────┘   │      │
        │            ⚡           └──┐   │
        │     [◈]         [◈]      │   │
        ╰──────────────────────────────────╯
        """,
        LabFeature.ORGANIZED: """
        ╭──────────────────────────────────╮
        │   [⚗]    ┌─────┐    📚    [⚗]   │
        │    │     │     │     ┌─┐   │    │
        │   📜     │     │     │ │   🔮   │
        │    ├─────┘     └─────┤ │        │
        │    │   Organized    │ │   ⚛    │
        │    │      Lab      │ └─┐  │    │
        │ 🧪  │     Area      │   │  │    │
        │    │   [ordered]   │   │ 🌿    │
        │    └───────────────┘   │      │
        │            ⚡           └──┐   │
        │     [◈]         [◈]      │   │
        ╰──────────────────────────────────╯
        """,
        LabFeature.WELL_LIT: """
        ╭──────────────────────────────────╮
        │ ☀️  [⚗]   ┌─────┐   📚  ☀️ [⚗]   │
        │          │     │     ┌─┐        │
        │   📜     │     │     │ │   🔮   │
        │    ┌─────┘     └─────┐ │   ☀️   │
        │ ☀️  │    Well-Lit   │ │   ⚛    │
        │    │      Lab      │ └─┐  │    │
        │ 🧪  │     Area      │   │  │    │
        │    │    [bright]   │   │ 🌿    │
        │    └───────────────┘   │  ☀️   │
        │     ☀️      ⚡           └──┐   │
        │     [◈]         [◈]      │   │
        ╰──────────────────────────────────╯
        """,
        # Add more templates for other features
    }

    def __init__(self, laboratory: Laboratory):
        self.laboratory = laboratory
        self.console = Console()

    def _create_header(self) -> Panel:
        """Create header panel with lab owner and basic info."""
        grid = Table.grid(padding=1)
        grid.add_row(
            f"[bold cyan]Owner:[/bold cyan] {self.laboratory.owner}",
            f"[bold cyan]Size:[/bold cyan] {self.laboratory.size}",
            f"[bold cyan]Aura:[/bold cyan] {self.laboratory.magical_aura}",
        )
        return Panel(grid, title="[bold]Laboratory Details[/bold]", border_style="cyan")

    def _create_lab_visualization(self) -> Panel:
        """Create visual representation of the laboratory."""
        # Choose template based on features
        template = self.LAB_TEMPLATES["basic"]
        for feature in self.laboratory.features:
            if feature in self.LAB_TEMPLATES:
                template = self.LAB_TEMPLATES[feature]
                break

        # Add equipment markers
        for equipment in self.laboratory.equipment:
            # Add equipment symbols to the template
            # This is a simplified version; you might want to make this more sophisticated
            template = template.replace("   ", f" {equipment.name[:1]} ", 1)

        return Panel(template, title="[bold]Laboratory Layout[/bold]", border_style="green")

    def _create_stats_panel(self) -> Panel:
        """Create panel with laboratory statistics."""
        stats = Table.grid(padding=1)
        stats.add_row("[cyan]Safety:[/cyan]", str(self.laboratory.safety))
        stats.add_row("[cyan]Health:[/cyan]", str(self.laboratory.health))
        stats.add_row("[cyan]Aesthetics:[/cyan]", str(self.laboratory.aesthetics))
        stats.add_row("[cyan]Upkeep:[/cyan]", str(self.laboratory.upkeep))
        return Panel(stats, title="[bold]Laboratory Statistics[/bold]", border_style="blue")

    def _create_equipment_table(self) -> Table:
        """Create table of laboratory equipment."""
        table = Table(title="Laboratory Equipment", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Equipment", style="cyan")
        table.add_column("Bonus", justify="right")
        table.add_column("Specialization")

        for item in self.laboratory.equipment:
            table.add_row(item.name, str(item.bonus), item.specialization.value if item.specialization else "None")

        return table

    def _create_features_panel(self) -> Panel:
        """Create panel listing laboratory features."""
        features_text = "\n".join(f"• {feature.value}" for feature in self.laboratory.features)
        return Panel(features_text, title="[bold]Laboratory Features[/bold]", border_style="yellow")

    def show(self) -> None:
        """Display the complete laboratory visualization."""
        # Create the layout
        layout = Layout()

        # Split the layout into sections
        layout.split_column(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3))

        # Split the body into left and right sections
        layout["body"].split_row(Layout(name="left"), Layout(name="right"))

        # Split the right section into upper and lower
        layout["right"].split_column(Layout(name="right_upper"), Layout(name="right_lower"))

        # Assign content to layout sections
        layout["header"].update(self._create_header())
        layout["left"].update(self._create_lab_visualization())
        layout["right_upper"].update(Panel(Layout(self._create_stats_panel(), self._create_features_panel())))
        layout["right_lower"].update(self._create_equipment_table())

        # Print the layout
        self.console.print(layout)


# Update the CLI command to use the visualization
def show_laboratory(owner: str) -> None:
    """Display laboratory visualization."""
    try:
        laboratory = Laboratory.load(owner)
        visualization = LabVisualization(laboratory)
        visualization.show()
    except Exception as e:
        console = Console()
        console.print(f"[red]Error displaying laboratory: {e}[/red]")
