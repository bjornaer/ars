from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .types import AbilityType, House


class CharacterNotFoundError(Exception):
    """Raised when a character cannot be found."""

    pass


@dataclass
class Character:
    """Represents a character in Ars Magica."""

    name: str
    player: str
    saga: str
    covenant: str
    house: House
    age: int = 25

    # Characteristics
    intelligence: int = 0
    perception: int = 0
    strength: int = 0
    stamina: int = 0
    presence: int = 0
    communication: int = 0
    dexterity: int = 0
    quickness: int = 0

    # Magic
    techniques: dict[str, int] = field(
        default_factory=lambda: {"Creo": 0, "Intellego": 0, "Muto": 0, "Perdo": 0, "Rego": 0}
    )
    forms: dict[str, int] = field(
        default_factory=lambda: {
            "Animal": 0,
            "Aquam": 0,
            "Auram": 0,
            "Corpus": 0,
            "Herbam": 0,
            "Ignem": 0,
            "Imaginem": 0,
            "Mentem": 0,
            "Terram": 0,
            "Vim": 0,
        }
    )

    # Abilities
    abilities: dict[AbilityType, dict[str, int]] = field(default_factory=lambda: {t: {} for t in AbilityType})

    # Personality
    personality_traits: dict[str, int] = field(default_factory=dict)
    virtues: list[str] = field(default_factory=list)
    flaws: list[str] = field(default_factory=list)

    def save(self, directory: Path = Path("ars/data/characters")) -> None:
        """Save character to file."""
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / f"{self.name.lower().replace(' ', '_')}.yml"

        # Convert enum keys to strings for YAML
        data = self.__dict__.copy()
        data["abilities"] = {type_name.name: abilities for type_name, abilities in self.abilities.items()}
        data["house"] = self.house.value

        with filepath.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def load(cls, name: str, directory: Path = Path("ars/data/characters")) -> "Character":
        """Load character from file."""
        filepath = directory / f"{name.lower().replace(' ', '_')}.yml"

        try:
            with filepath.open("r") as f:
                data = yaml.safe_load(f)

                # Convert string ability types back to enum
                abilities_data = data.pop("abilities")
                data["abilities"] = {
                    AbilityType[type_name]: abilities for type_name, abilities in abilities_data.items()
                }

                # Convert house string back to enum
                data["house"] = House[data["house"].upper()]

                return cls(**data)
        except FileNotFoundError as err:
            raise CharacterNotFoundError(f"Character '{name}' not found") from err

    @staticmethod
    def list_characters(directory: Path = Path("ars/data/characters")) -> list[str]:
        """List all saved characters."""
        directory.mkdir(parents=True, exist_ok=True)
        return [f.stem for f in directory.glob("*.yml")]
