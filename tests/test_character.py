import pytest

from ars.character import Character
from ars.types import AbilityType, House


@pytest.fixture
def sample_character():
    return Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS,
        age=25,
    )


def test_character_creation(sample_character):
    assert sample_character.name == "Testus of Bonisagus"
    assert sample_character.age == 25
    assert sample_character.techniques == {"Creo": 0, "Intellego": 0, "Muto": 0, "Perdo": 0, "Rego": 0}


def test_character_save_load(sample_character, tmp_path):
    # Save character
    sample_character.save(directory=tmp_path)

    # Load character
    loaded = Character.load(sample_character.name, directory=tmp_path)

    assert loaded.name == sample_character.name
    assert loaded.techniques == sample_character.techniques
    assert loaded.house == sample_character.house


def test_ability_management(sample_character):
    sample_character.abilities[AbilityType.ACADEMIC]["Latin"] = 5
    assert sample_character.abilities[AbilityType.ACADEMIC]["Latin"] == 5
