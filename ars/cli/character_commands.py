import click
from pathlib import Path
import yaml
import json
from datetime import datetime
import zipfile
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from ars.cli.character_wizard import CharacterWizard
from ars.core.character import Character, CharacterError
from ars.core.characters.magus import Magus
from ars.core.characters.grog import Grog
from ars.core.types import AbilityType, WeaponType, ArmorType
from ars.cli.state import get_saga_dir, get_active_saga, get_character_dir

console = Console()


def get_active_saga_dir() -> Optional[Path]:
    """Get the directory of the active saga."""
    global_config = Path.home() / ".ars" / "global_config.yml"
    if not global_config.exists():
        raise CharacterError("No active saga. Use 'ars init' or 'ars activate' first.")
        
    with global_config.open('r') as f:
        config = yaml.safe_load(f)
        saga_name = config.get('active_saga')
        
    if not saga_name:
        raise CharacterError("No active saga. Use 'ars init' or 'ars activate' first.")
        
    return Path.home() / ".ars" / saga_name.lower().replace(' ', '_')


def get_character_dir() -> Path:
    """Get the character directory for the active saga."""
    saga_dir = get_active_saga_dir()
    return saga_dir / "characters"


@click.group()
def character():
    """Character management commands."""
    pass


@character.command()
@click.option("--quick/--no-quick", default=False, help="Quick creation mode")
def create(quick: bool):
    """Create a new character using the character wizard."""
    try:
        # Get active saga info
        saga_dir = get_active_saga_dir()
        with (saga_dir / "config.yml").open('r') as f:
            saga_config = yaml.safe_load(f)
            
        wizard = CharacterWizard(saga_name=saga_config['saga_name'])
        character = wizard.run()
        
        if character:
            if Confirm.ask("Save character?"):
                char_dir = get_character_dir()
                character.save(directory=char_dir)
                console.print(f"[green]Character '{character.name}' saved successfully[/green]")
        else:
            console.print("[red]Character creation cancelled or failed[/red]")
            
    except Exception as e:
        console.print(f"[red]Error creating character: {e}[/red]")


@character.command()
@click.argument("name")
def show(name: str):
    """Display character details."""
    try:
        char_dir = get_character_dir()
        char = Character.load(name, directory=char_dir)
        
        # Basic Info Table
        info_table = Table(title=f"Character: {char.name}")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Player", char.player)
        info_table.add_row("Saga", char.saga)
        info_table.add_row("Covenant", char.covenant)
        info_table.add_row("Age", str(char.age))
        
        if isinstance(char, Magus):
            info_table.add_row("Type", "Magus")
            info_table.add_row("House", char.house.value)
        else:
            info_table.add_row("Type", "Grog")
            
        console.print(info_table)
        
        # Characteristics Table
        char_table = Table(title="Characteristics")
        char_table.add_column("Characteristic", style="cyan")
        char_table.add_column("Score", style="green")
        
        for char_type, value in char.characteristics.items():
            char_table.add_row(char_type.value, str(value))
            
        console.print("\n", char_table)
        
        # Abilities Table
        for ability_type in AbilityType:
            abilities = char.abilities.get(ability_type, {})
            if abilities:
                ability_table = Table(title=f"{ability_type.value} Abilities")
                ability_table.add_column("Ability", style="cyan")
                ability_table.add_column("Score", style="green")
                
                for ability, score in abilities.items():
                    ability_table.add_row(ability, str(score))
                    
                console.print("\n", ability_table)
        
        # Equipment Tables
        if char.weapons:
            weapon_table = Table(title="Weapons")
            weapon_table.add_column("Weapon", style="cyan")
            weapon_table.add_column("Skill", style="green")
            
            for weapon, skill in char.weapons.items():
                weapon_table.add_row(weapon.value, str(skill))
                
            console.print("\n", weapon_table)
            
        if char.armor:
            armor_table = Table(title="Armor")
            armor_table.add_column("Type", style="cyan")
            armor_table.add_column("Protection", style="green")
            
            armor_stats = ArmorType.get_stats(char.armor)
            armor_table.add_row(
                char.armor.value,
                str(armor_stats["protection"])
            )
            
            console.print("\n", armor_table)
            
        # Magus-specific information
        if isinstance(char, Magus):
            # Magical Arts
            arts_table = Table(title="Magical Arts")
            arts_table.add_column("Art", style="cyan")
            arts_table.add_column("Score", style="green")
            
            for tech, score in char.techniques.items():
                arts_table.add_row(f"(T) {tech.value}", str(score))
            for form, score in char.forms.items():
                arts_table.add_row(f"(F) {form.value}", str(score))
                
            console.print("\n", arts_table)
            
            # Spells
            if char.spells:
                spell_table = Table(title="Spells")
                spell_table.add_column("Name", style="cyan")
                spell_table.add_column("Level", style="green")
                spell_table.add_column("Technique", style="yellow")
                spell_table.add_column("Form", style="yellow")
                
                for spell in char.spells.values():
                    spell_table.add_row(
                        spell.name,
                        str(spell.level),
                        spell.technique.value,
                        spell.form.value
                    )
                    
                console.print("\n", spell_table)
        
    except Exception as e:
        console.print(f"[red]Error showing character: {e}[/red]")


@character.command()
def list():
    """List all characters in the active saga."""
    try:
        char_dir = get_character_dir()
        characters = []
        
        for file in char_dir.glob("*.yml"):
            try:
                char = Character.load(file.stem, directory=char_dir)
                char_type = "Magus" if isinstance(char, Magus) else "Grog"
                characters.append((
                    char.name,
                    char_type,
                    char.covenant
                ))
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load {file.name}: {e}[/yellow]")
        
        if characters:
            table = Table(title="Characters in Saga")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Covenant", style="green")
            
            for char in sorted(characters):
                table.add_row(*char)
                
            console.print(table)
        else:
            console.print("[yellow]No characters found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error listing characters: {e}[/red]")


@character.command()
@click.argument("name")
@click.option("--format", "-f", type=click.Choice(["json", "yaml"]), default="json")
@click.option("--output", "-o", type=click.Path(), default=None)
def export(name: str, format: str, output: str):
    """Export a character to a specific format."""
    try:
        char_dir = get_character_dir()
        char = Character.load(name, directory=char_dir)
        data = char.to_dict()
        
        # Add metadata
        saga_dir = get_active_saga_dir()
        with (saga_dir / "config.yml").open('r') as f:
            saga_config = yaml.safe_load(f)
            
        data["_export_metadata"] = {
            "export_date": datetime.now().isoformat(),
            "format_version": "1.0",
            "character_type": "Magus" if isinstance(char, Magus) else "Grog",
            "saga_name": saga_config["saga_name"]
        }
        
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"{name.lower().replace(' ', '_')}_{timestamp}.{format}"
            
        output_path = saga_dir / "exports"
        output_path.mkdir(exist_ok=True)
        output_file = output_path / output
        
        with output_file.open('w', encoding='utf-8') as f:
            if format == "json":
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:  # yaml
                yaml.dump(data, f, allow_unicode=True)
                
        console.print(f"[green]Character exported to {output_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error exporting character: {e}[/red]")


@character.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--force/--no-force", default=False, help="Overwrite if character exists")
def import_char(file: str, force: bool):
    """Import a character from a file."""
    try:
        with open(file, 'r', encoding='utf-8') as f:
            if file.endswith('.json'):
                data = json.load(f)
            elif file.endswith('.yml') or file.endswith('.yaml'):
                data = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported file format")
        
        # Validate metadata and saga compatibility
        if "_export_metadata" in data:
            metadata = data.pop("_export_metadata")
            saga_dir = get_active_saga_dir()
            with (saga_dir / "config.yml").open('r') as f:
                current_saga = yaml.safe_load(f)["saga_name"]
                
            if metadata.get("saga_name") != current_saga:
                if not Confirm.ask(
                    f"Character from different saga '{metadata.get('saga_name')}'. Import anyway?"
                ):
                    return
        
        # Create character
        char_type = metadata.get("character_type", "Grog")
        if char_type == "Magus":
            character = Magus.from_dict(data)
        else:
            character = Grog.from_dict(data)
        
        # Save to active saga
        char_dir = get_character_dir()
        char_path = char_dir / f"{character.name.lower().replace(' ', '_')}.yml"
        
        if char_path.exists() and not force:
            if not Confirm.ask(f"Character '{character.name}' already exists. Overwrite?"):
                console.print("[yellow]Import cancelled[/yellow]")
                return
        
        character.save(directory=char_dir)
        console.print(f"[green]Successfully imported {character.name}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error importing character: {e}[/red]")


@character.command()
@click.argument("names", nargs=-1)
@click.option("--output", "-o", type=click.Path(), default=None)
def export_bundle(names: List[str], output: str):
    """Export multiple characters as a bundle."""
    try:
        saga_dir = get_active_saga_dir()
        char_dir = get_character_dir()
        
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = saga_dir / "exports" / f"character_bundle_{timestamp}.zip"
            
        output.parent.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as bundle:
            # Add saga config
            with (saga_dir / "config.yml").open('r') as f:
                saga_config = yaml.safe_load(f)
            
            # Create manifest
            manifest = {
                "export_date": datetime.now().isoformat(),
                "format_version": "1.0",
                "saga_name": saga_config["saga_name"],
                "characters": {}
            }
            
            for name in names:
                try:
                    char = Character.load(name, directory=char_dir)
                    char_data = char.to_dict()
                    
                    # Add to manifest
                    manifest["characters"][name] = {
                        "type": "Magus" if isinstance(char, Magus) else "Grog",
                        "covenant": char.covenant
                    }
                    
                    # Add character file to bundle
                    char_filename = f"characters/{name.lower().replace(' ', '_')}.json"
                    bundle.writestr(
                        char_filename,
                        json.dumps(char_data, indent=2, ensure_ascii=False)
                    )
                    
                except Exception as e:
                    console.print(f"[red]Error bundling {name}: {e}[/red]")
            
            # Add manifest to bundle
            bundle.writestr(
                "manifest.json",
                json.dumps(manifest, indent=2, ensure_ascii=False)
            )
            
        console.print(f"[green]Characters exported to {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error creating bundle: {e}[/red]")