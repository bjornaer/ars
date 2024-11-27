from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..character import Character
from ..laboratory import Laboratory
from ..magic_items import InstallationType, ItemCreationManager, ItemEffect, ItemType, MagicItem
from ..types import Form, Technique
from ..vis_aura import VisManager

console = Console()


@click.group()
def enchant():
    """Magic item creation and enchantment commands."""
    pass


@enchant.command()
@click.argument("character_name")
@click.argument("item_name")
@click.argument("item_type", type=click.Choice([t.value for t in ItemType]))
@click.option("--material", "-m", help="Base material of the item")
@click.option("--size", "-s", type=int, default=0, help="Size of the item")
@click.option("--shape-bonus", type=int, default=0, help="Shape bonus")
@click.option("--material-bonus", type=int, default=0, help="Material bonus")
@click.option("--description", "-d", help="Item description")
def create_item(
    character_name: str,
    item_name: str,
    item_type: str,
    material: str,
    size: int,
    shape_bonus: int,
    material_bonus: int,
    description: str,
):
    """Create a new magic item."""
    try:
        # Load character
        character = Character.load(character_name)

        # Create item
        item = MagicItem(
            name=item_name,
            type=ItemType(item_type),
            creator=character_name,
            base_material=material or "Unknown",
            size=size,
            shape_bonus=shape_bonus,
            material_bonus=material_bonus,
            description=description or "",
        )

        # Calculate vis capacity based on type and size
        if item.type != ItemType.CHARGED:
            item.vis_capacity = (size + 2) * 5

        # Save item to character's inventory
        if not hasattr(character, "magic_items"):
            character.magic_items = []
        character.magic_items.append(item)
        character.save()

        console.print(f"[green]Created magic item: {item_name}[/green]")
        console.print(
            Panel(
                f"Type: {item_type}\n"
                f"Material: {material or 'Unknown'}\n"
                f"Size: {size}\n"
                f"Shape Bonus: {shape_bonus}\n"
                f"Material Bonus: {material_bonus}\n"
                f"Vis Capacity: {item.vis_capacity}\n"
                f"Description: {description or 'None'}"
            )
        )

    except Exception as e:
        console.print(f"[red]Error creating item: {e}[/red]")


@enchant.command()
@click.argument("character_name")
@click.argument("item_name")
@click.argument("effect_name")
@click.argument("technique", type=click.Choice([t.value for t in Technique]))
@click.argument("form", type=click.Choice([f.value for f in Form]))
@click.argument("level", type=int)
@click.option(
    "--installation",
    "-i",
    type=click.Choice([i.value for i in InstallationType]),
    default="Effect",
    help="Installation type",
)
@click.option("--uses", type=int, help="Uses per day")
@click.option("--trigger", help="Trigger condition")
@click.option("--penetration", type=int, default=0, help="Penetration bonus")
@click.option("--description", "-d", help="Effect description")
def add_effect(
    character_name: str,
    item_name: str,
    effect_name: str,
    technique: str,
    form: str,
    level: int,
    installation: str,
    uses: int,
    trigger: str,
    penetration: int,
    description: str,
):
    """Add an effect to a magic item."""
    try:
        # Load character and managers
        character = Character.load(character_name)
        laboratory = Laboratory.load(character_name)
        manager = ItemCreationManager()

        # Find item
        item = next((i for i in character.magic_items if i.name == item_name), None)
        if not item:
            console.print(f"[red]Item not found: {item_name}[/red]")
            return

        # Create effect
        effect = ItemEffect(
            name=effect_name,
            technique=Technique(technique),
            form=Form(form),
            level=level,
            installation_type=InstallationType(installation),
            uses_per_day=uses,
            trigger_condition=trigger,
            penetration=penetration,
            description=description or "",
        )

        # Start project
        if manager.start_project(character, laboratory, item, effect):
            console.print(f"[green]Started enchantment project for {effect_name}[/green]")
            console.print(
                Panel(
                    f"Lab Total: {effect.lab_total}\n"
                    f"Seasons Required: {effect.seasons_required}\n"
                    f"Vis Required: {', '.join(f'{k.value}: {v}' for k, v in effect.vis_required.items())}"
                )
            )

            # Save state
            manager.save_state(Path("ars/data/enchantment_projects.yml"))
        else:
            console.print("[red]Cannot add effect to item (check capacity)[/red]")

    except Exception as e:
        console.print(f"[red]Error adding effect: {e}[/red]")


@enchant.command()
@click.argument("character_name")
def continue_enchantment(character_name: str):
    """Continue work on current enchantment project."""
    try:
        # Load necessary components
        character = Character.load(character_name)
        laboratory = Laboratory.load(character_name)
        vis_manager = VisManager.load(Path("ars/data/vis_stocks.yml"))
        manager = ItemCreationManager.load_state(Path("ars/data/enchantment_projects.yml"))

        # Continue project
        result = manager.continue_project(character, laboratory, vis_manager)

        if "error" in result:
            console.print(f"[red]{result['error']}[/red]")
            return

        if result["status"] == "completed":
            console.print("[green]Enchantment completed![/green]")
            item = result["item"]
            effect = result["effect"]
            console.print(
                Panel(
                    f"Item: {item.name}\n"
                    f"Effect: {effect.name}\n"
                    f"Level: {effect.level}\n"
                    f"Remaining Capacity: {item.calculate_remaining_capacity()}"
                )
            )
        else:
            console.print(
                f"[yellow]Enchantment in progress. " f"Seasons remaining: {result['seasons_remaining']}[/yellow]"
            )

        # Save state
        manager.save_state(Path("ars/data/enchantment_projects.yml"))
        vis_manager.save(Path("ars/data/vis_stocks.yml"))

    except Exception as e:
        console.print(f"[red]Error continuing enchantment: {e}[/red]")


@enchant.command()
@click.argument("character_name")
@click.argument("item_name")
def show_item(character_name: str, item_name: str):
    """Display magic item details."""
    try:
        character = Character.load(character_name)
        item = next((i for i in character.magic_items if i.name == item_name), None)

        if not item:
            console.print(f"[red]Item not found: {item_name}[/red]")
            return

        # Create item info table
        info_table = Table(title=f"Magic Item: {item.name}")
        info_table.add_column("Property")
        info_table.add_column("Value")

        info_table.add_row("Type", item.type.value)
        info_table.add_row("Creator", item.creator)
        info_table.add_row("Material", item.base_material)
        info_table.add_row("Size", str(item.size))
        info_table.add_row("Shape Bonus", str(item.shape_bonus))
        info_table.add_row("Material Bonus", str(item.material_bonus))
        info_table.add_row("Vis Capacity", f"{item.current_capacity}/{item.vis_capacity}")

        console.print(info_table)

        if item.effects:
            effects_table = Table(title="Effects")
            effects_table.add_column("Name")
            effects_table.add_column("Arts")
            effects_table.add_column("Level")
            effects_table.add_column("Type")
            effects_table.add_column("Uses/Day")
            effects_table.add_column("Trigger")

            for effect in item.effects:
                effects_table.add_row(
                    effect.name,
                    f"{effect.technique.value}/{effect.form.value}",
                    str(effect.level),
                    effect.installation_type.value,
                    str(effect.uses_per_day or "∞"),
                    effect.trigger_condition or "None",
                )

            console.print(effects_table)

        if item.description:
            console.print(Panel(item.description, title="Description"))

    except Exception as e:
        console.print(f"[red]Error displaying item: {e}[/red]")


@enchant.command()
@click.argument("character_name")
def list_items(character_name: str):
    """List all magic items owned by a character."""
    try:
        character = Character.load(character_name)

        if not hasattr(character, "magic_items") or not character.magic_items:
            console.print("[yellow]No magic items found[/yellow]")
            return

        table = Table(title=f"Magic Items owned by {character_name}")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Effects")
        table.add_column("Capacity")

        for item in character.magic_items:
            table.add_row(
                item.name, item.type.value, str(len(item.effects)), f"{item.current_capacity}/{item.vis_capacity}"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing items: {e}[/red]")
