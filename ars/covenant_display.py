from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from .covenant import Covenant


class CovenantVisualization:
    """Handles covenant visualization."""

    # ASCII art templates for different covenant sizes
    COVENANT_TEMPLATES = {
        "Small": """
        ╭──────────────────────────────────╮
        │    🏰  Summer Covenant   🏰     │
        │      ┌─────────────┐            │
        │  🏠  │   Main      │    ⚔️      │
        │      │   Hall      │            │
        │      └─────────────┘     🏠     │
        │           🔮                     │
        │    🏠          🏛️         🏠    │
        ╰──────────────────────────────────╯
        """,
        "Medium": """
        ╭────────────────────────────────────────╮
        │    🏰    Autumn Covenant     🏰       │
        │   ┌─────┐    ┌─────┐    ┌─────┐      │
        │   │ 🏛️  │    │     │    │  ⚔️ │      │
        │   └─────┘    │     │    └─────┘      │
        │      🏠      │     │       🏠        │
        │ ┌─────────┐  │     │  ┌─────────┐    │
        │ │   🔮    │  └─────┘  │   📚    │    │
        │ └─────────┘    🏰    └─────────┘    │
        │    🏠     🏠    🏠     🏠    🏠     │
        ╰────────────────────────────────────────╯
        """,
        "Large": """
        ╭──────────────────────────────────────────────╮
        │  🏰      Winter Covenant        🏰         │
        │ ┌─────┐  ┌─────────────┐  ┌─────┐  ┌─────┐ │
        │ │ 🏛️  │  │     🏰     │  │  ⚔️ │  │ 📚  │ │
        │ └─────┘  │           │  └─────┘  └─────┘ │
        │    🏠    │           │     🏠      🏠    │
        │ ┌─────┐  │           │  ┌─────┐  ┌─────┐ │
        │ │  🔮 │  └─────────────┘  │ ⚗️  │  │ 🛡️  │ │
        │ └─────┘      🏰         └─────┘  └─────┘ │
        │  🏠   🏠   🏠   🏠   🏠   🏠   🏠   🏠  │
        ╰──────────────────────────────────────────────╯
        """,
    }

    def __init__(self, covenant: Covenant):
        self.covenant = covenant
        self.console = Console()

    def _create_header(self) -> Panel:
        """Create header panel with covenant info."""
        grid = Table.grid(padding=1)
        grid.add_row(
            f"[bold cyan]Name:[/bold cyan] {self.covenant.name}",
            f"[bold cyan]Size:[/bold cyan] {self.covenant.size.value}",
            f"[bold cyan]Age:[/bold cyan] {self.covenant.age} years",
            f"[bold cyan]Aura:[/bold cyan] {self.covenant.aura}",
        )
        return Panel(grid, title="[bold]Covenant Details[/bold]", border_style="cyan")

    def _create_population_panel(self) -> Panel:
        """Create panel showing covenant population."""
        grid = Table.grid(padding=1)
        grid.add_row("[cyan]Magi:[/cyan]", str(len(self.covenant.magi)))
        grid.add_row("[cyan]Covenfolk:[/cyan]", str(self.covenant.covenfolk))
        grid.add_row("[cyan]Grogs:[/cyan]", str(self.covenant.grogs))
        return Panel(grid, title="[bold]Population[/bold]", border_style="blue")

    def _create_buildings_table(self) -> Table:
        """Create table of covenant buildings."""
        table = Table(title="Buildings", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Building")
        table.add_column("Type")
        table.add_column("Size")
        table.add_column("Quality")
        table.add_column("Maintenance")

        for building in self.covenant.buildings:
            table.add_row(
                building.name,
                building.type.value,
                str(building.size),
                str(building.quality),
                str(building.maintenance_cost),
            )

        return table

    def _create_vis_table(self) -> Table:
        """Create table showing vis sources and stocks."""
        table = Table(title="Vis Sources & Stocks", box=box.ROUNDED, show_header=True, header_style="bold green")
        table.add_column("Source/Stock")
        table.add_column("Form")
        table.add_column("Amount")
        table.add_column("Season")

        # Add sources
        for source in self.covenant.vis_sources:
            table.add_row(
                source.name,
                source.form.value,
                str(source.amount),
                source.season,
                style="dim" if source.claimed else "bright",
            )

        # Add stocks
        for form, amount in self.covenant.vis_stocks.items():
            if amount > 0:
                table.add_row("Stock", form.value, str(amount), "-", style="bold")

        return table

    def _create_library_panel(self) -> Panel:
        """Create panel showing library information."""
        content = Table.grid(padding=1)
        content.add_row("[cyan]Books:[/cyan]", str(len(self.covenant.library.books)))
        content.add_row("[cyan]Summa:[/cyan]", str(len(self.covenant.library.summa)))
        content.add_row("[cyan]Tractatus:[/cyan]", str(sum(len(t) for t in self.covenant.library.tractatus.values())))
        content.add_row("[cyan]Capacity:[/cyan]", str(self.covenant.library.capacity))
        content.add_row("[cyan]Organization:[/cyan]", str(self.covenant.library.organization))
        return Panel(content, title="[bold]Library[/bold]", border_style="yellow")

    def show(self) -> None:
        """Display the complete covenant visualization."""
        layout = Layout()

        # Split the layout into sections
        layout.split_column(Layout(name="header", size=3), Layout(name="main"), Layout(name="footer", size=3))

        # Split the main section
        layout["main"].split_row(Layout(name="left"), Layout(name="right"))

        # Split the right section
        layout["right"].split_column(Layout(name="right_upper"), Layout(name="right_lower"))

        # Add content
        layout["header"].update(self._create_header())

        # Add covenant visualization
        template = self.COVENANT_TEMPLATES.get(self.covenant.size.value, self.COVENANT_TEMPLATES["Small"])
        layout["left"].update(Panel(template, title="[bold]Covenant Layout[/bold]"))

        # Add other panels
        layout["right_upper"].update(Layout(self._create_population_panel(), self._create_library_panel()))
        layout["right_lower"].update(Layout(self._create_buildings_table(), self._create_vis_table()))

        self.console.print(layout)
