from pathlib import Path
from typing import Optional
import yaml

def get_saga_dir(saga_name: str) -> Path:
    """Get the directory for a specific saga."""
    return Path.home() / ".ars" / saga_name.lower().replace(' ', '_')


def get_active_saga() -> Optional[str]:
    """Get the currently active saga name from global config."""
    global_config = Path.home() / ".ars" / "global_config.yml"
    if not global_config.exists():
        return None
        
    with global_config.open('r') as f:
        config = yaml.safe_load(f)
        return config.get('active_saga')

def init_saga_config(saga_name: str) -> Path:
    """Initialize configuration directory and files for a saga."""
    # Create saga-specific directory
    saga_dir = get_saga_dir(saga_name)
    saga_dir.mkdir(parents=True, exist_ok=True)
    
    # Create saga subdirectories
    (saga_dir / "characters").mkdir(exist_ok=True)
    (saga_dir / "spells").mkdir(exist_ok=True)
    
    # Create saga-specific config if it doesn't exist
    config_file = saga_dir / "config.yml"
    if not config_file.exists():
        default_config = {
            "saga_name": saga_name,
            "data_dir": str(saga_dir),
            "character_dir": str(saga_dir / "characters"),
            "spell_dir": str(saga_dir / "spells")
        }
        with config_file.open("w") as f:
            yaml.dump(default_config, f)
            
    return saga_dir

def get_active_character() -> Optional[str]:
    """Get the currently active character name from global config."""
    global_config = Path.home() / ".ars" / "global_config.yml"
    if not global_config.exists():
        return None
        
    with global_config.open('r') as f:
        config = yaml.safe_load(f)
        return config.get('active_character')


def set_active_saga(saga_name: str):
    """Set the active saga in global config."""
    ars_dir = Path.home() / ".ars"
    ars_dir.mkdir(exist_ok=True)
    
    global_config = ars_dir / "global_config.yml"
    config = {}
    
    if global_config.exists():
        with global_config.open('r') as f:
            config = yaml.safe_load(f) or {}
            
    config['active_saga'] = saga_name
    
    with global_config.open('w') as f:
        yaml.dump(config, f)


def set_active_character(character_name: Optional[str]):
    """Set the active character in global config."""
    ars_dir = Path.home() / ".ars"
    ars_dir.mkdir(exist_ok=True)
    
    global_config = ars_dir / "global_config.yml"
    config = {}
    
    if global_config.exists():
        with global_config.open('r') as f:
            config = yaml.safe_load(f) or {}
            
    if character_name is None:
        config.pop('active_character', None)
    else:
        config['active_character'] = character_name
    
    with global_config.open('w') as f:
        yaml.dump(config, f)


def get_character_dir() -> Path:
    """Get the character directory for the active saga."""
    saga_dir = get_saga_dir(get_active_saga())
    return saga_dir / "characters" 