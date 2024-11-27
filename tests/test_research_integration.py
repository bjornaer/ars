import pytest

from ars.character import Character
from ars.laboratory import Laboratory
from ars.spell_research import ResearchProject, ResearchType
from ars.spell_research_manager import SpellResearchManager
from ars.types import Form, House, Technique


@pytest.fixture
def integrated_setup():
    """Create an integrated test environment."""
    character = Character(
        name="Integrus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS,
    )
    character.techniques["Creo"] = 10
    character.forms["Ignem"] = 8

    laboratory = Laboratory(owner="Integrus of Bonisagus", size=2, magical_aura=3)

    project = ResearchProject(
        researcher=character.name,
        research_type=ResearchType.SPELL_CREATION,
        target_level=10,
        technique=Technique.CREO,
        form=Form.IGNEM,
    )

    return character, laboratory, project


def test_full_research_cycle(integrated_setup, tmp_path):
    """Test a complete research cycle with all components."""
    character, laboratory, project = integrated_setup

    # Save all components
    character.save(directory=tmp_path)
    laboratory.save(directory=tmp_path)
    project.save(directory=tmp_path)

    # Conduct research
    result = SpellResearchManager.conduct_research(project, character, laboratory)

    # Verify research affected all components
    assert result.points_gained > 0

    if result.warping_points > 0:
        character.add_warping(result.warping_points)
        assert character.warping_points > 0

    # Save updated state
    project.save(directory=tmp_path)
    character.save(directory=tmp_path)

    # Load and verify
    loaded_project = ResearchProject.load(character.name, directory=tmp_path)
    loaded_character = Character.load(character.name, directory=tmp_path)

    assert loaded_project.research_points == project.research_points
    if result.warping_points > 0:
        assert loaded_character.warping_points == character.warping_points


def test_laboratory_research_integration(integrated_setup):
    """Test integration between laboratory features and research."""
    character, laboratory, project = integrated_setup

    # Add laboratory features that should affect research
    laboratory.add_feature("Well Organized")  # Assuming this gives a bonus

    # Conduct research
    result = SpellResearchManager.conduct_research(project, character, laboratory)

    # Verify laboratory features affected research
    base_total = character.techniques["Creo"] + character.forms["Ignem"]
    assert result.points_gained > base_total  # Should include lab bonus


def test_character_research_integration(integrated_setup):
    """Test integration between character advancement and research."""
    character, laboratory, project = integrated_setup

    initial_art_score = character.techniques["Creo"]

    # Simulate multiple seasons of research
    for _ in range(4):
        result = SpellResearchManager.conduct_research(project, character, laboratory)

        assert result.points_gained > 0

        # Update character experience (if implemented)
        if hasattr(character, "add_experience"):
            character.add_experience("Creo", 2)  # Example experience gain

    # Verify character advancement
    if hasattr(character, "add_experience"):
        assert character.techniques["Creo"] > initial_art_score
