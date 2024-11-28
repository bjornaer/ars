import pytest

from ars.character import Character
from ars.covenant import Covenant
from ars.laboratory import Laboratory
from ars.spell_research import ResearchProject, ResearchType
from ars.core.types import Form, House, Technique
from ars.vis_aura_integration import IntegratedVisAuraManager


@pytest.fixture
def integrated_setup():
    """Create an integrated test environment."""
    covenant = Covenant(name="Test Covenant", size="Small", age=10, aura=3)

    laboratory = Laboratory(owner="Testus", size=0, magical_aura=3)

    character = Character(
        name="Testus", player="Test Player", saga="Test Saga", covenant="Test Covenant", house=House.BONISAGUS
    )

    project = ResearchProject(
        researcher="Testus",
        research_type=ResearchType.SPELL_CREATION,
        target_level=10,
        technique=Technique.CREO,
        form=Form.IGNEM,
    )

    manager = IntegratedVisAuraManager("Test Saga")

    return covenant, laboratory, character, project, manager


def test_covenant_integration(integrated_setup):
    """Test integration with covenant system."""
    covenant, _, _, _, manager = integrated_setup

    manager.integrate_with_covenant(covenant, "Summer")

    # Verify aura registration
    aura = manager.aura_manager.get_aura(covenant.name)
    assert aura is not None
    assert aura.strength == covenant.aura

    # Verify vis sources registration
    if covenant.vis_sources:
        source_name = f"{covenant.name}_{covenant.vis_sources[0].location}"
        assert source_name in manager.vis_manager.sources


def test_laboratory_integration(integrated_setup):
    """Test integration with laboratory system."""
    covenant, laboratory, _, _, manager = integrated_setup

    manager.integrate_with_laboratory(laboratory, covenant)

    assert laboratory.magical_aura == covenant.aura
    assert "vis_extraction" in laboratory.activity_modifiers


def test_research_integration(integrated_setup):
    """Test integration with research system."""
    covenant, laboratory, _, project, manager = integrated_setup

    # Add some vis to stocks
    manager.vis_manager.stocks[Technique.CREO] = 5
    manager.vis_manager.stocks[Form.IGNEM] = 3

    effects = manager.integrate_with_research(project, laboratory, covenant, "Summer")

    assert effects is not None
    assert "magical_activities" in effects

    # Verify vis usage
    if "Creo_bonus" in effects:
        assert manager.vis_manager.stocks[Technique.CREO] < 5


def test_vis_extraction_integration(integrated_setup):
    """Test integrated vis extraction process."""
    covenant, laboratory, character, _, manager = integrated_setup

    # Add a vis source
    from ars.vis_aura import VisSource, VisType

    source = VisSource(form=Technique.CREO, amount=5, type=VisType.RAW, season="Summer", location=laboratory.location)
    manager.vis_manager.register_source("test_source", source)

    results = manager.process_vis_extraction(character, laboratory, covenant, "Summer", 1220)

    assert len(results) > 0
    assert results[0][0] == Technique.CREO
    assert results[0][1] >= 5  # Should be at least base amount


def test_save_load_integration(integrated_setup, tmp_path):
    """Test saving and loading integrated state."""
    covenant, laboratory, character, project, manager = integrated_setup

    # Setup some state
    manager.integrate_with_covenant(covenant)
    manager.integrate_with_laboratory(laboratory, covenant)

    # Save state
    manager.save_state(tmp_path)

    # Load state
    loaded_manager = IntegratedVisAuraManager.load_state("Test Saga", tmp_path)

    # Verify state
    assert loaded_manager.vis_manager.stocks == manager.vis_manager.stocks
    assert loaded_manager.saga_name == manager.saga_name
