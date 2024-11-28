import pytest

from ars.laboratory import LabEquipment, LabFeature, Laboratory, LabSpecialization
from ars.core.types import Form, Technique


@pytest.fixture
def test_equipment():
    return LabEquipment(
        name="Precision Alembic",
        bonus=3,
        specialization=LabSpecialization.POTIONS,
        forms=[Form.AQUAM],
        techniques=[Technique.CREO],
        description="A finely crafted alembic for potion brewing",
    )


@pytest.fixture
def test_laboratory(test_equipment):
    lab = Laboratory(owner="Testus of Bonisagus", size=3, magical_aura=3)
    lab.add_equipment(test_equipment)
    lab.add_feature(LabFeature.ORGANIZED)
    lab.add_specialization(LabSpecialization.POTIONS)
    return lab


def test_laboratory_creation():
    """Test basic laboratory creation."""
    lab = Laboratory(owner="Testus", size=3)
    assert lab.owner == "Testus"
    assert lab.size == 3
    assert lab.safety == 0
    assert lab.magical_aura == 0


def test_equipment_management(test_laboratory, test_equipment):
    """Test adding and removing equipment."""
    # Test adding equipment
    new_equipment = LabEquipment(name="Enchanted Crucible", bonus=2, specialization=LabSpecialization.ENCHANTING)
    test_laboratory.add_equipment(new_equipment)
    assert len(test_laboratory.equipment) == 2

    # Test removing equipment
    removed = test_laboratory.remove_equipment("Enchanted Crucible")
    assert removed == new_equipment
    assert len(test_laboratory.equipment) == 1

    # Test removing non-existent equipment
    assert test_laboratory.remove_equipment("Non-existent") is None


def test_feature_effects(test_laboratory):
    """Test the effects of adding laboratory features."""
    initial_safety = test_laboratory.safety

    # Test positive feature
    test_laboratory.add_feature(LabFeature.PROTECTED)
    assert test_laboratory.safety == initial_safety + 1

    # Test negative feature
    test_laboratory.add_feature(LabFeature.CHAOTIC)
    assert test_laboratory.safety == initial_safety  # +1 from PROTECTED, -1 from CHAOTIC

    # Test duplicate feature
    test_laboratory.add_feature(LabFeature.PROTECTED)
    assert test_laboratory.safety == initial_safety  # No change for duplicate


def test_specialization_management(test_laboratory):
    """Test adding and managing specializations."""
    test_laboratory.add_specialization(LabSpecialization.ENCHANTING)
    assert len(test_laboratory.specializations) == 2
    assert LabSpecialization.ENCHANTING in test_laboratory.specializations

    # Test duplicate specialization
    test_laboratory.add_specialization(LabSpecialization.ENCHANTING)
    assert len(test_laboratory.specializations) == 2


def test_bonus_calculations(test_laboratory):
    """Test various bonus calculations."""
    # Test total bonus calculation
    bonus = test_laboratory.calculate_total_bonus(technique=Technique.CREO, form=Form.AQUAM)
    assert bonus == test_laboratory.safety + test_laboratory.magical_aura + 3  # 3 from test_equipment

    # Test enchantment bonus
    test_laboratory.add_specialization(LabSpecialization.ENCHANTING)
    enchant_bonus = test_laboratory.calculate_enchantment_bonus()
    assert enchant_bonus == 4  # 3 from specialization + 1 from size


def test_extraction_bonus(test_laboratory):
    """Test vis extraction bonus calculation."""
    test_laboratory.add_specialization(LabSpecialization.VIS_EXTRACTION)

    # Base calculation
    bonus = test_laboratory.calculate_extraction_bonus()
    assert bonus == 4  # 3 from specialization + 1 from magical_aura//2

    # With activity modifier
    test_laboratory.activity_modifiers["vis_extraction"] = 2
    bonus = test_laboratory.calculate_extraction_bonus()
    assert bonus == 6  # 3 from specialization + 1 from aura + 2 from modifier


def test_serialization(test_laboratory, tmp_path):
    """Test laboratory serialization and deserialization."""
    # Save laboratory
    save_path = tmp_path / "test_lab.yml"
    test_laboratory.save(save_path)

    # Load laboratory
    loaded_lab = Laboratory.load(save_path)

    # Verify basic attributes
    assert loaded_lab.owner == test_laboratory.owner
    assert loaded_lab.size == test_laboratory.size
    assert loaded_lab.magical_aura == test_laboratory.magical_aura

    # Verify equipment
    assert len(loaded_lab.equipment) == len(test_laboratory.equipment)
    loaded_equip = loaded_lab.equipment[0]
    original_equip = test_laboratory.equipment[0]
    assert loaded_equip.name == original_equip.name
    assert loaded_equip.bonus == original_equip.bonus
    assert loaded_equip.specialization == original_equip.specialization

    # Verify features and specializations
    assert loaded_lab.features == test_laboratory.features
    assert loaded_lab.specializations == test_laboratory.specializations


def test_equipment_serialization(test_equipment, tmp_path):
    """Test equipment serialization and deserialization."""
    # Save equipment
    save_path = tmp_path / "test_equipment.yml"
    test_equipment.save(save_path)

    # Load equipment
    loaded_equipment = LabEquipment.load(save_path)

    # Verify attributes
    assert loaded_equipment.name == test_equipment.name
    assert loaded_equipment.bonus == test_equipment.bonus
    assert loaded_equipment.specialization == test_equipment.specialization
    assert loaded_equipment.forms == test_equipment.forms
    assert loaded_equipment.techniques == test_equipment.techniques


def test_form_technique_bonuses(test_laboratory):
    """Test form and technique bonus calculations."""
    test_laboratory.form_bonuses[Form.IGNEM] = 2
    test_laboratory.technique_bonuses[Technique.CREO] = 3

    bonus = test_laboratory.calculate_total_bonus(technique=Technique.CREO, form=Form.IGNEM)

    expected = test_laboratory.safety + test_laboratory.magical_aura + 2 + 3  # Form bonus  # Technique bonus

    assert bonus == expected
