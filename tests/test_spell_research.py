import pytest

from ars.character import Character
from ars.laboratory import Laboratory
from ars.spell_research import ResearchModifier, ResearchOutcome, ResearchProject, ResearchType
from ars.spell_research_manager import ResearchResult, SpellResearchManager
from ars.spells import Spell, SpellParameters
from ars.types import Form, House, Technique


@pytest.fixture
def test_character():
    char = Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS,
    )
    # Add some Art scores
    char.techniques["Creo"] = 10
    char.forms["Ignem"] = 8
    return char


@pytest.fixture
def test_laboratory():
    return Laboratory(owner="Testus of Bonisagus", size=0, magical_aura=3)


@pytest.fixture
def test_spell():
    params = SpellParameters(technique=Technique.CREO, form=Form.IGNEM, level=10, name="Test Fire Spell")
    return Spell.create(params)


@pytest.fixture
def test_project(test_character):
    return ResearchProject(
        researcher=test_character.name,
        research_type=ResearchType.SPELL_CREATION,
        target_level=10,
        technique=Technique.CREO,
        form=Form.IGNEM,
    )


def test_research_project_creation(test_character):
    """Test creating a new research project."""
    project = SpellResearchManager.create_research_project(
        researcher=test_character,
        research_type=ResearchType.SPELL_CREATION,
        target_level=10,
        technique=Technique.CREO,
        form=Form.IGNEM,
    )

    assert project.researcher == test_character.name
    assert project.research_type == ResearchType.SPELL_CREATION
    assert project.target_level == 10
    assert project.technique == Technique.CREO
    assert project.form == Form.IGNEM
    assert project.seasons_invested == 0
    assert project.research_points == 0


def test_research_calculation(test_project, test_character, test_laboratory):
    """Test calculation of research totals."""
    total = test_project.calculate_research_total(test_character, test_laboratory)

    # Should be: Technique (10) + Form (8) + Aura (3) = 21
    assert total == 21


def test_research_modifiers(test_project):
    """Test adding and applying research modifiers."""
    modifier = ResearchModifier(
        name="Test Modifier", bonus=3, description="Test", applicable_types=[ResearchType.SPELL_CREATION]
    )

    test_project.modifiers.append(modifier)
    assert len(test_project.modifiers) == 1
    assert test_project.modifiers[0].bonus == 3


def test_conduct_research(test_project, test_character, test_laboratory):
    """Test conducting research."""
    result = SpellResearchManager.conduct_research(test_project, test_character, test_laboratory)

    assert isinstance(result, ResearchResult)
    assert result.points_gained > 0
    assert isinstance(result.outcome, ResearchOutcome)


def test_project_completion(test_project, test_character, test_laboratory):
    """Test research project completion."""
    # Manually add enough points to complete the project
    target_points = SpellResearchManager.POINTS_NEEDED[ResearchType.SPELL_CREATION](10)
    test_project.research_points = target_points

    result = SpellResearchManager.conduct_research(test_project, test_character, test_laboratory)

    assert result.new_spell is not None
    assert result.new_spell.level == test_project.target_level


def test_breakthrough_mechanics(test_project, test_character, test_laboratory, monkeypatch):
    """Test breakthrough mechanics."""

    # Mock the dice rolls to force a breakthrough
    def mock_breakthrough_roll():
        return 0

    monkeypatch.setattr("ars.dice.DiceRoller.simple_die", mock_breakthrough_roll)

    result = SpellResearchManager.conduct_research(test_project, test_character, test_laboratory)

    assert result.breakthrough_points > 0
    assert result.outcome == ResearchOutcome.BREAKTHROUGH


def test_save_load_project(test_project, tmp_path):
    """Test saving and loading research projects."""
    # Add some data to save
    test_project.add_note("Test note")
    test_project.research_points = 10

    # Save project
    test_project.save(directory=tmp_path)

    # Load project
    loaded_project = ResearchProject.load(test_project.researcher, directory=tmp_path)

    assert loaded_project.researcher == test_project.researcher
    assert loaded_project.research_type == test_project.research_type
    assert loaded_project.research_points == test_project.research_points
    assert len(loaded_project.notes) == 1


def test_spell_modification(test_character, test_laboratory, test_spell):
    """Test spell modification research."""
    project = SpellResearchManager.create_research_project(
        researcher=test_character, research_type=ResearchType.SPELL_MODIFICATION, target_spell=test_spell
    )

    result = SpellResearchManager.conduct_research(project, test_character, test_laboratory)

    assert isinstance(result, ResearchResult)
    assert result.points_gained > 0


def test_spell_mastery(test_character, test_laboratory, test_spell):
    """Test spell mastery research."""
    project = SpellResearchManager.create_research_project(
        researcher=test_character, research_type=ResearchType.SPELL_MASTERY, target_spell=test_spell
    )

    result = SpellResearchManager.conduct_research(project, test_character, test_laboratory)

    assert isinstance(result, ResearchResult)
    assert result.points_gained > 0


def test_experimentation(test_character, test_laboratory):
    """Test experimental research."""
    project = SpellResearchManager.create_research_project(
        researcher=test_character,
        research_type=ResearchType.SPELL_EXPERIMENTATION,
        target_level=10,
        technique=Technique.CREO,
        form=Form.IGNEM,
    )

    result = SpellResearchManager.conduct_research(project, test_character, test_laboratory)

    assert isinstance(result, ResearchResult)
    assert result.outcome in [ResearchOutcome.SUCCESS, ResearchOutcome.FAILURE]


def test_botch_handling(test_project, test_character, test_laboratory, monkeypatch):
    """Test handling of botched research rolls."""

    # Mock the dice roll to force a botch
    def mock_botch_roll():
        class MockRoll:
            total = 0
            botch = True

        return MockRoll()

    monkeypatch.setattr("ars.dice.DiceRoller.stress_die", mock_botch_roll)

    result = SpellResearchManager.conduct_research(test_project, test_character, test_laboratory)

    assert result.outcome == ResearchOutcome.CATASTROPHIC_FAILURE
    assert result.warping_points > 0
    assert result.points_gained == 0


def test_research_modifiers_application(test_character):
    """Test application of character-based research modifiers."""
    test_character.virtues.append("Inventive Genius")

    modifiers = SpellResearchManager.get_available_modifiers(test_character, ResearchType.SPELL_CREATION)

    assert len(modifiers) > 0
    assert any(mod.name == "Inventive Genius" for mod in modifiers)
