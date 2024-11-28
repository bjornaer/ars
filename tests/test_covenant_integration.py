import pytest

from ars.character import Character
from ars.covenant import Building, BuildingType, Covenant, CovenantSize
from ars.laboratory import Laboratory
from ars.core.types import House


@pytest.fixture
def integrated_covenant():
    return Covenant(name="Integration Test Covenant", size=CovenantSize.MEDIUM, age=25, aura=4)


@pytest.fixture
def integrated_character():
    return Character(
        name="Integrus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Integration Test Covenant",
        house=House.BONISAGUS,
    )


@pytest.fixture
def integrated_laboratory():
    return Laboratory(owner="Integrus of Bonisagus", size=2, magical_aura=4)  # Should match covenant aura


def test_character_covenant_integration(integrated_covenant, integrated_character):
    """Test integration between character and covenant."""
    # Add character to covenant
    integrated_covenant.magi.append(integrated_character.name)

    # Verify character's covenant matches
    assert integrated_character.covenant == integrated_covenant.name

    # Save both
    integrated_covenant.save()
    integrated_character.save()

    # Load and verify
    loaded_covenant = Covenant.load(integrated_covenant.name)
    loaded_character = Character.load(integrated_character.name)

    assert loaded_character.name in loaded_covenant.magi
    assert loaded_character.covenant == loaded_covenant.name


def test_laboratory_covenant_integration(integrated_covenant, integrated_laboratory):
    """Test integration between laboratory and covenant."""
    # Add laboratory building to covenant
    lab_building = Building(
        type=BuildingType.LABORATORY,
        name=f"{integrated_laboratory.owner}'s Laboratory",
        size=integrated_laboratory.size,
        quality=2,
    )
    integrated_covenant.add_building(lab_building)

    # Verify laboratory aura matches covenant
    assert integrated_laboratory.magical_aura == integrated_covenant.aura

    # Save both
    integrated_covenant.save()
    integrated_laboratory.save()

    # Load and verify
    loaded_covenant = Covenant.load(integrated_covenant.name)
    loaded_laboratory = Laboratory.load(integrated_laboratory.owner)

    assert any(b.type == BuildingType.LABORATORY for b in loaded_covenant.buildings)
    assert loaded_laboratory.magical_aura == loaded_covenant.aura


def test_full_integration(integrated_covenant, integrated_character, integrated_laboratory):
    """Test full integration between all components."""
    # Set up relationships
    integrated_covenant.magi.append(integrated_character.name)
    lab_building = Building(
        type=BuildingType.LABORATORY,
        name=f"{integrated_laboratory.owner}'s Laboratory",
        size=integrated_laboratory.size,
        quality=2,
    )
    integrated_covenant.add_building(lab_building)

    # Verify relationships
    assert integrated_character.name in integrated_covenant.magi
    assert integrated_character.covenant == integrated_covenant.name
    assert integrated_laboratory.magical_aura == integrated_covenant.aura

    # Test vis collection affects character's laboratory
    integrated_laboratory.magical_aura = integrated_covenant.aura

    # Save all
    integrated_covenant.save()
    integrated_character.save()
    integrated_laboratory.save()

    # Load and verify all relationships persist
    loaded_covenant = Covenant.load(integrated_covenant.name)
    loaded_character = Character.load(integrated_character.name)
    loaded_laboratory = Laboratory.load(integrated_laboratory.owner)

    assert loaded_character.name in loaded_covenant.magi
    assert loaded_character.covenant == loaded_covenant.name
    assert loaded_laboratory.magical_aura == loaded_covenant.aura
    assert any(
        b.type == BuildingType.LABORATORY and b.name == f"{loaded_character.name}'s Laboratory"
        for b in loaded_covenant.buildings
    )
