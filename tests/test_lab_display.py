from io import StringIO

import pytest
from rich.console import Console

from ars.lab_display import LabVisualization
from ars.laboratory import LabEquipment, LabFeature, Laboratory, LabSpecialization


@pytest.fixture
def sample_lab():
    lab = Laboratory(owner="Testus of Bonisagus", size=0, magical_aura=3, safety=1, health=0, aesthetics=0, upkeep=0)
    lab.features.append(LabFeature.ORGANIZED)
    lab.add_equipment(LabEquipment(name="Precision Alembic", bonus=2, specialization=LabSpecialization.VIS_EXTRACTION))
    return lab


def test_lab_visualization(sample_lab):
    visualization = LabVisualization(sample_lab)
    console = Console(file=StringIO(), force_terminal=True)

    # Test that visualization can be created without errors
    visualization.console = console
    visualization.show()

    output = console.file.getvalue()
    assert "Testus of Bonisagus" in output
    assert "Laboratory Details" in output
    assert "Precision Alembic" in output
