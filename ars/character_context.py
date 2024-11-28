import json
from pathlib import Path
from typing import Optional

from .character import Character  # Assuming you have a Character class


class CharacterContext:
    _instance = None
    _current_character: Optional[Character] = None
    _save_path: Path = Path.home() / ".ars" / "current_character"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_current_character(cls) -> Optional[Character]:
        if cls._current_character is None:
            cls._load_from_file()
        return cls._current_character

    @classmethod
    def set_current_character(cls, character: Character) -> None:
        cls._current_character = character
        cls._save_to_file()

    @classmethod
    def clear_current_character(cls) -> None:
        cls._current_character = None
        if cls._save_path.exists():
            cls._save_path.unlink()

    @classmethod
    def _save_to_file(cls) -> None:
        if not cls._current_character:
            return

        cls._save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cls._save_path, "w") as f:
            json.dump(
                {
                    "character_name": cls._current_character.name,
                    "character_path": str(cls._current_character.save_path),
                },
                f,
            )

    @classmethod
    def _load_from_file(cls) -> None:
        if not cls._save_path.exists():
            return

        try:
            with open(cls._save_path, "r") as f:
                data = json.load(f)
                character_path = Path(data["character_path"])
                if character_path.exists():
                    cls._current_character = Character.load(character_path)
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            cls._save_path.unlink(missing_ok=True)


# Convenience functions
def get_current_character() -> Optional[Character]:
    return CharacterContext.get_current_character()


def set_current_character(character: Character) -> None:
    CharacterContext.set_current_character(character)


def clear_current_character() -> None:
    CharacterContext.clear_current_character()
