from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ars.character import Character
from ars.covenant import Covenant
from ars.laboratory import Laboratory
from ars.core.types import Season
from ars.serialization import Serializable


@dataclass
class GameState(Serializable):
    """Central state management for the game."""

    saga_name: str
    data_dir: Path = field(default_factory=lambda: Path.home() / ".ars")
    current_season: Season = Season.SPRING
    current_year: int = 1220

    # State collections
    characters: Dict[str, Character] = field(default_factory=dict)
    covenants: Dict[str, Covenant] = field(default_factory=dict)
    laboratories: Dict[str, Laboratory] = field(default_factory=dict)

    # Current selections
    current_character: Optional[str] = None
    current_covenant: Optional[str] = None

    def __post_init__(self):
        """Ensure data directory exists and load initial state."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.load_state()

    def load_state(self) -> None:
        """Load all game state from files."""
        state_file = self.data_dir / f"{self.saga_name}_state.yml"
        if state_file.exists():
            with state_file.open("r") as f:
                data = yaml.safe_load(f)
                self.current_season = Season(data.get("current_season", "SPRING"))
                self.current_year = data.get("current_year", 1220)
                self.current_character = data.get("current_character")
                self.current_covenant = data.get("current_covenant")

        # Load individual components
        self._load_characters()
        self._load_covenants()
        self._load_laboratories()

    def save_state(self) -> None:
        """Save all game state to files."""
        # Save main state file
        state_file = self.data_dir / f"{self.saga_name}_state.yml"
        with state_file.open("w") as f:
            yaml.safe_dump(
                {
                    "current_season": self.current_season.value,
                    "current_year": self.current_year,
                    "current_character": self.current_character,
                    "current_covenant": self.current_covenant,
                },
                f,
            )

        # Save individual components
        self._save_characters()
        self._save_covenants()
        self._save_laboratories()

    # Character management
    def _load_characters(self) -> None:
        char_dir = self.data_dir / "characters"
        if char_dir.exists():
            for char_file in char_dir.glob("*.yml"):
                character = Character.load(char_file)
                self.characters[character.name] = character

    def _save_characters(self) -> None:
        char_dir = self.data_dir / "characters"
        char_dir.mkdir(exist_ok=True)
        for character in self.characters.values():
            character.save(char_dir / f"{character.name}.yml")

    # Covenant management
    def _load_covenants(self) -> None:
        cov_dir = self.data_dir / "covenants"
        if cov_dir.exists():
            for cov_file in cov_dir.glob("*.yml"):
                covenant = Covenant.load(cov_file)
                self.covenants[covenant.name] = covenant

    def _save_covenants(self) -> None:
        cov_dir = self.data_dir / "covenants"
        cov_dir.mkdir(exist_ok=True)
        for covenant in self.covenants.values():
            covenant.save(cov_dir / f"{covenant.name}.yml")

    # Laboratory management
    def _load_laboratories(self) -> None:
        lab_dir = self.data_dir / "laboratories"
        if lab_dir.exists():
            for lab_file in lab_dir.glob("*.yml"):
                laboratory = Laboratory.load(lab_file)
                self.laboratories[laboratory.owner] = laboratory

    def _save_laboratories(self) -> None:
        lab_dir = self.data_dir / "laboratories"
        lab_dir.mkdir(exist_ok=True)
        for laboratory in self.laboratories.values():
            laboratory.save(lab_dir / f"{laboratory.owner}.yml")

    # Convenience methods for current selections
    def get_current_character(self) -> Optional[Character]:
        """Get the currently selected character."""
        return self.characters.get(self.current_character) if self.current_character else None

    def get_current_covenant(self) -> Optional[Covenant]:
        """Get the currently selected covenant."""
        return self.covenants.get(self.current_covenant) if self.current_covenant else None

    def get_laboratory_for_character(self, character_name: str) -> Optional[Laboratory]:
        """Get laboratory for a specific character."""
        return self.laboratories.get(character_name)

    def set_current_character(self, character_name: str) -> None:
        """Set the current character."""
        if character_name in self.characters:
            self.current_character = character_name
            self.save_state()
        else:
            raise ValueError(f"Character '{character_name}' not found")

    def set_current_covenant(self, covenant_name: str) -> None:
        """Set the current covenant."""
        if covenant_name in self.covenants:
            self.current_covenant = covenant_name
            self.save_state()
        else:
            raise ValueError(f"Covenant '{covenant_name}' not found")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        # Convert season string to enum
        data["current_season"] = Season(data["current_season"])

        # Create instance without collections
        collections = ["characters", "covenants", "laboratories"]
        clean_data = {k: v for k, v in data.items() if k not in collections}
        state = cls(**clean_data)

        # Load collections
        if "characters" in data:
            state.characters = {name: Character.from_dict(char_data) for name, char_data in data["characters"].items()}
        if "covenants" in data:
            state.covenants = {name: Covenant.from_dict(cov_data) for name, cov_data in data["covenants"].items()}
        if "laboratories" in data:
            state.laboratories = {
                name: Laboratory.from_dict(lab_data) for name, lab_data in data["laboratories"].items()
            }

        return state
