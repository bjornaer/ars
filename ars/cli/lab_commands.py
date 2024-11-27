import click
from rich.console import Console

from ..character import Character
from ..lab_activities import ItemEnchantment, LongevityRitual, VisExtraction
from ..lab_display import show_laboratory
from ..laboratory import LabEquipment, LabFeature, Laboratory, LabSpecialization
from ..types import Form, Technique

console = Console()


@click.group()
def lab():
    """Laboratory management commands."""
    pass


@lab.command()
@click.argument("owner")
@click.option("--size", default=0, help="Size of the laboratory")
@click.option("--aura", default=3, help="Magical aura strength")
def create(owner: str, size: int, aura: int):
    """Create a new laboratory for a magus."""
    try:
        laboratory = Laboratory(owner=owner, size=size, magical_aura=aura)
        laboratory.save()
        console.print(f"[green]Created laboratory for {owner}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating laboratory: {e}[/red]")


@lab.command()
@click.argument("owner")
def show(owner: str):
    """Display laboratory details with visualization."""
    show_laboratory(owner)


@lab.command()
@click.argument("owner")
@click.argument("equipment_name")
@click.option("--bonus", required=True, type=int, help="Equipment bonus")
@click.option("--specialization", type=click.Choice([s.value for s in LabSpecialization]))
def add_equipment(owner: str, equipment_name: str, bonus: int, specialization: str = None):
    """Add equipment to laboratory."""
    try:
        laboratory = Laboratory.load(owner)

        equipment = LabEquipment(
            name=equipment_name,
            bonus=bonus,
            specialization=LabSpecialization(specialization) if specialization else None,
        )

        laboratory.add_equipment(equipment)
        laboratory.save()

        console.print(f"[green]Added {equipment_name} to {owner}'s laboratory[/green]")
    except Exception as e:
        console.print(f"[red]Error adding equipment: {e}[/red]")


@lab.command()
@click.argument("owner")
@click.argument("feature")
def add_feature(owner: str, feature: str):
    """Add a feature to laboratory."""
    try:
        laboratory = Laboratory.load(owner)

        try:
            lab_feature = LabFeature(feature)
        except ValueError:
            console.print(f"[red]Invalid feature. Valid features are: {', '.join(f.value for f in LabFeature)}[/red]")
            return

        laboratory.features.append(lab_feature)
        laboratory.save()

        console.print(f"[green]Added feature {feature} to {owner}'s laboratory[/green]")
    except Exception as e:
        console.print(f"[red]Error adding feature: {e}[/red]")


@lab.command()
@click.argument("owner")
@click.argument("activity", type=click.Choice(["vis", "enchant", "longevity"]))
@click.option("--technique", help="Technique for the activity")
@click.option("--form", help="Form for the activity")
def perform_activity(owner: str, activity: str, technique: str = None, form: str = None):
    """Perform a laboratory activity."""
    try:
        laboratory = Laboratory.load(owner)
        character = Character.load(owner)  # Assuming character name matches lab owner

        if activity == "vis":
            if not form:
                console.print("[red]Form is required for vis extraction[/red]")
                return

            activity = VisExtraction(
                name="Vis Extraction",
                season=1,  # TODO: Track seasons
                year=1234,  # TODO: Track years
                magus=character,
                laboratory=laboratory,
            )
            result = activity.execute(Form(form))
            console.print(f"[green]Extracted {result} pawns of {form} vis[/green]")

        elif activity == "enchant":
            if not all([technique, form]):
                console.print("[red]Technique and Form are required for enchanting[/red]")
                return

            activity = ItemEnchantment(
                name="Item Enchantment", season=1, year=1234, magus=character, laboratory=laboratory
            )
            lab_total = activity.calculate_lab_total(Technique(technique), Form(form))
            console.print(f"[green]Enchantment lab total: {lab_total}[/green]")

        elif activity == "longevity":
            activity = LongevityRitual(
                name="Longevity Ritual", season=1, year=1234, magus=character, laboratory=laboratory
            )
            result = activity.execute()
            console.print(f"[green]Longevity Ritual strength: {result}[/green]")

    except Exception as e:
        console.print(f"[red]Error performing activity: {e}[/red]")
