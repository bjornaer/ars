import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..character import Character
from ..laboratory import Laboratory
from ..spell_research import ResearchProject, ResearchType
from ..spell_research_manager import SpellResearchManager
from ..spells import Spell
from ..types import Form, Technique

console = Console()


@click.group()
def research():
    """Spell research and creation commands."""
    pass


@research.command()
@click.argument("researcher")
@click.argument("research_type", type=click.Choice([t.value for t in ResearchType]))
@click.option("--spell", help="Target spell name for modification or mastery")
@click.option("--level", type=int, help="Target spell level for creation")
@click.option("--technique", type=click.Choice([t.value for t in Technique]), help="Spell technique")
@click.option("--form", type=click.Choice([f.value for f in Form]), help="Spell form")
def start(
    researcher: str, research_type: str, spell: str = None, level: int = None, technique: str = None, form: str = None
):
    """Start a new research project."""
    try:
        # Load character and validate
        character = Character.load(researcher)

        # Load target spell if specified
        target_spell = None
        if spell:
            target_spell = Spell.load(spell)

        # Validate parameters based on research type
        research_type_enum = ResearchType(research_type)
        if research_type_enum == ResearchType.SPELL_CREATION:
            if not all([level, technique, form]):
                console.print("[red]Level, technique, and form are required for spell creation.[/red]")
                return
        elif research_type_enum in [ResearchType.SPELL_MODIFICATION, ResearchType.SPELL_MASTERY]:
            if not spell:
                console.print("[red]Target spell is required for modification or mastery.[/red]")
                return

        # Create project
        project = SpellResearchManager.create_research_project(
            researcher=character,
            research_type=research_type_enum,
            target_spell=target_spell,
            target_level=level,
            technique=Technique(technique) if technique else None,
            form=Form(form) if form else None,
        )

        # Save project
        project.save()

        console.print(f"[green]Started new {research_type} project for {researcher}[/green]")

    except Exception as e:
        console.print(f"[red]Error starting research project: {e}[/red]")


@research.command()
@click.argument("researcher")
def conduct(researcher: str):
    """Conduct a season of research."""
    try:
        # Load necessary components
        character = Character.load(researcher)
        laboratory = Laboratory.load(researcher)
        project = ResearchProject.load(researcher)

        # Conduct research
        result = SpellResearchManager.conduct_research(project=project, character=character, laboratory=laboratory)

        # Display results
        console.print("\n[bold cyan]Research Results:[/bold cyan]")

        result_panel = Panel.fit(
            f"Outcome: {result.outcome.value}\n"
            f"Points Gained: {result.points_gained}\n"
            f"Breakthrough Points: {result.breakthrough_points}\n"
            f"Warping Points: {result.warping_points}",
            title="Season Results",
        )
        console.print(result_panel)

        if result.notes:
            notes_panel = Panel.fit("\n".join(result.notes), title="Research Notes")
            console.print(notes_panel)

        if result.new_spell:
            spell_panel = Panel.fit(
                f"Created new spell: {result.new_spell.name}\n"
                f"Level: {result.new_spell.level}\n"
                f"Technique: {result.new_spell.technique}\n"
                f"Form: {result.new_spell.form}",
                title="New Spell",
            )
            console.print(spell_panel)

        # Save updated project
        project.save()

        # Update character if necessary
        if result.warping_points > 0:
            character.add_warping(result.warping_points)
            character.save()

    except Exception as e:
        console.print(f"[red]Error conducting research: {e}[/red]")


@research.command()
@click.argument("researcher")
def show(researcher: str):
    """Display current research project details."""
    try:
        project = ResearchProject.load(researcher)

        # Create main info table
        info_table = Table(title="Research Project")
        info_table.add_column("Attribute")
        info_table.add_column("Value")

        info_table.add_row("Researcher", project.researcher)
        info_table.add_row("Type", project.research_type.value)
        if project.target_spell:
            info_table.add_row("Target Spell", project.target_spell.name)
        if project.target_level:
            info_table.add_row("Target Level", str(project.target_level))
        if project.technique:
            info_table.add_row("Technique", project.technique.value)
        if project.form:
            info_table.add_row("Form", project.form.value)

        info_table.add_row("Seasons Invested", str(project.seasons_invested))
        info_table.add_row("Research Points", str(project.research_points))
        info_table.add_row("Breakthrough Points", str(project.breakthrough_points))

        console.print(info_table)

        # Show modifiers if any
        if project.modifiers:
            mod_table = Table(title="Research Modifiers")
            mod_table.add_column("Name")
            mod_table.add_column("Bonus")
            mod_table.add_column("Description")

            for mod in project.modifiers:
                mod_table.add_row(mod.name, str(mod.bonus), mod.description)

            console.print(mod_table)

        # Show notes if any
        if project.notes:
            notes_panel = Panel.fit("\n".join(project.notes), title="Research Notes")
            console.print(notes_panel)

    except Exception as e:
        console.print(f"[red]Error displaying research project: {e}[/red]")


@research.command()
@click.argument("researcher")
@click.argument("note")
def add_note(researcher: str, note: str):
    """Add a note to the research project."""
    try:
        project = ResearchProject.load(researcher)
        project.add_note(note)
        project.save()

        console.print("[green]Added note to research project[/green]")
    except Exception as e:
        console.print(f"[red]Error adding note: {e}[/red]")
