import pytest

from ars.laboratory import LabEquipment, LabFeature, Laboratory, LabSpecialization
from ars.types import Form, Technique


@pytest.fixture
def sample_lab():
    return Laboratory(owner="Testus of Bonisagus", size=0, magical_aura=3, safety=1, health=0, aesthetics=0, upkeep=0)


@pytest.fixture
def sample_equipment():
    return LabEquipment(
        name="Precision Alembic",
        bonus=2,
        specialization=LabSpecialization.VIS_EXTRACTION,
        forms=[Form.AQUAM],
        techniques=[Technique.CREO],
    )


def test_laboratory_creation(sample_lab):
    assert sample_lab.owner == "Testus of Bonisagus"
    assert sample_lab.magical_aura == 3
    assert sample_lab.safety == 1


def test_add_equipment(sample_lab, sample_equipment):
    sample_lab.add_equipment(sample_equipment)
    assert len(sample_lab.equipment) == 1
    assert sample_lab.equipment[0].name == "Precision Alembic"


def test_calculate_bonus(sample_lab, sample_equipment):
    sample_lab.add_equipment(sample_equipment)
    bonus = sample_lab.calculate_total_bonus(Technique.CREO, Form.AQUAM)
    # Base safety (1) + Equipment bonus (2) + Aura (3)
    assert bonus == 6


def test_save_load(sample_lab, tmp_path):
    # Add some data to save
    sample_lab.features.append(LabFeature.ORGANIZED)
    sample_lab.save(directory=tmp_path)

    # Load and verify
    loaded_lab = Laboratory.load(sample_lab.owner, directory=tmp_path)
    assert loaded_lab.owner == sample_lab.owner
    assert loaded_lab.features[0] == LabFeature.ORGANIZED


def test_remove_equipment(sample_lab, sample_equipment):
    sample_lab.add_equipment(sample_equipment)
    removed = sample_lab.remove_equipment("Precision Alembic")
    assert removed is not None
    assert len(sample_lab.equipment) == 0
