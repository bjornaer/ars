import pytest

from ars.character import Character
from ars.lab_activities import ItemEnchantment, LongevityRitual, VisExtraction
from ars.laboratory import Laboratory
from ars.core.types import Form, House, Technique


@pytest.fixture
def sample_character():
    char = Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS,
    )
    char.techniques["Creo"] = 5
    char.forms["Vim"] = 5
    return char


@pytest.fixture
def sample_laboratory():
    return Laboratory(owner="Testus of Bonisagus", size=0, magical_aura=3)


def test_vis_extraction(sample_character, sample_laboratory):
    activity = VisExtraction(
        name="Test Extraction", season=1, year=1220, magus=sample_character, laboratory=sample_laboratory
    )

    result = activity.execute(Form.VIM)
    # Lab total should be: Arts (10) + Aura (3) = 13
    # Vis pawns should be 13 // 10 = 1
    assert result == 1


def test_item_enchantment(sample_character, sample_laboratory):
    activity = ItemEnchantment(
        name="Test Enchantment", season=1, year=1220, magus=sample_character, laboratory=sample_laboratory
    )

    lab_total = activity.calculate_lab_total(Technique.CREO, Form.VIM)
    # Lab total should be: Arts (10) + Aura (3) = 13
    assert lab_total == 13


def test_longevity_ritual(sample_character, sample_laboratory):
    activity = LongevityRitual(
        name="Test Ritual", season=1, year=1220, magus=sample_character, laboratory=sample_laboratory
    )

    result = activity.execute()
    # Lab total should be: Cr + Co + Aura
    assert result > 0
