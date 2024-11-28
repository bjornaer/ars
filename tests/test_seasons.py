import pytest

from ars.character import Character
from ars.covenant import Covenant
from ars.laboratory import Laboratory
from ars.seasons import ActivityType, GameYear, Season, SeasonManager
from ars.core.types import House


@pytest.fixture
def test_saga():
    return "Test Saga"


@pytest.fixture
def test_character():
    return Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS,
    )


@pytest.fixture
def test_covenant():
    return Covenant(name="Test Covenant", size="Small", age=10, aura=3)


@pytest.fixture
def season_manager(test_saga):
    manager = SeasonManager(test_saga)
    return manager


def test_season_progression():
    """Test season progression mechanics."""
    assert Season.next_season(Season.SPRING) == Season.SUMMER
    assert Season.next_season(Season.SUMMER) == Season.AUTUMN
    assert Season.next_season(Season.AUTUMN) == Season.WINTER
    assert Season.next_season(Season.WINTER) == Season.SPRING


def test_game_year():
    """Test game year mechanics."""
    year = GameYear(year=1220)
    assert year.current_season == Season.SPRING

    # Test year advancement
    next_season = year.advance_season()
    assert next_season == Season.SUMMER
    assert year.year == 1220

    # Test year change
    for _ in range(3):  # Advance to next spring
        year.advance_season()
    assert year.year == 1221
    assert year.current_season == Season.SPRING


def test_activity_scheduling(season_manager, test_character):
    """Test scheduling activities."""
    season_manager.register_character(test_character)

    activity = season_manager.schedule_activity(
        test_character.name, ActivityType.STUDY, {"source": "Summa", "subject": "Magic Theory", "quality": 10}
    )

    assert activity in season_manager.current_year.activities[test_character.name]
    assert activity.type == ActivityType.STUDY
    assert not activity.completed


def test_study_execution(season_manager, test_character):
    """Test study activity execution."""
    season_manager.register_character(test_character)
    initial_exp = test_character.experience.get("Magic Theory", 0)

    season_manager.schedule_activity(
        test_character.name, ActivityType.STUDY, {"source": "Summa", "subject": "Magic Theory", "quality": 10}
    )

    results = season_manager.execute_season()

    assert test_character.name in results
    assert results[test_character.name]["Study"]["subject"] == "Magic Theory"
    assert test_character.experience.get("Magic Theory", 0) > initial_exp


def test_research_execution(season_manager, test_character, tmp_path):
    """Test research activity execution."""
    from ars.spell_research import ResearchProject, ResearchType
    from ars.core.types import Form, Technique

    # Setup research project
    project = ResearchProject(
        researcher=test_character.name,
        research_type=ResearchType.SPELL_CREATION,
        target_level=10,
        technique=Technique.CREO,
        form=Form.IGNEM,
    )
    project.save(directory=tmp_path)

    # Setup laboratory
    lab = Laboratory(owner=test_character.name, size=0, magical_aura=3)
    lab.save(directory=tmp_path)

    season_manager.register_character(test_character)
    season_manager.schedule_activity(test_character.name, ActivityType.RESEARCH, {"project": "spell_creation"})

    results = season_manager.execute_season()
    assert test_character.name in results
    assert "Research" in results[test_character.name]
    assert "points" in results[test_character.name]["Research"]


def test_practice_execution(season_manager, test_character):
    """Test practice activity execution."""
    season_manager.register_character(test_character)
    initial_exp = test_character.experience.get("Parma Magica", 0)

    season_manager.schedule_activity(test_character.name, ActivityType.PRACTICE, {"ability": "Parma Magica"})

    results = season_manager.execute_season()
    assert test_character.name in results
    assert "Practice" in results[test_character.name]
    assert "points" in results[test_character.name]["Practice"]
    assert test_character.experience.get("Parma Magica", 0) > initial_exp


def test_covenant_integration(season_manager, test_covenant, test_character):
    """Test covenant integration with seasonal system."""
    season_manager.set_covenant(test_covenant)
    season_manager.register_character(test_character)

    # Test vis collection in appropriate seasons
    season_manager.current_year.current_season = Season.SPRING
    season_manager.execute_season()

    # Should have collected vis if sources exist
    if test_covenant.vis_sources:
        assert any(amount > 0 for amount in test_covenant.vis_stocks.values())


def test_save_load_saga(season_manager, test_character, tmp_path):
    """Test saving and loading saga state."""
    season_manager.register_character(test_character)
    season_manager.schedule_activity(
        test_character.name, ActivityType.STUDY, {"source": "Summa", "subject": "Magic Theory", "quality": 10}
    )

    # Save saga
    season_manager.save_saga()

    # Load saga
    new_manager = SeasonManager(season_manager.saga_name)
    new_manager.load_saga()

    assert new_manager.current_year.year == season_manager.current_year.year
    assert new_manager.current_year.current_season == season_manager.current_year.current_season
    assert test_character.name in new_manager.current_year.activities


def test_multiple_characters(season_manager):
    """Test handling multiple characters' activities."""
    char1 = Character(name="Testus1", player="P1", saga="Test Saga", house=House.BONISAGUS)
    char2 = Character(name="Testus2", player="P2", saga="Test Saga", house=House.BONISAGUS)

    season_manager.register_character(char1)
    season_manager.register_character(char2)

    season_manager.schedule_activity(char1.name, ActivityType.STUDY, {"subject": "Magic Theory"})
    season_manager.schedule_activity(char2.name, ActivityType.PRACTICE, {"ability": "Parma Magica"})

    results = season_manager.execute_season()
    assert char1.name in results and char2.name in results


def test_invalid_activity(season_manager, test_character):
    """Test handling invalid activity scheduling."""
    season_manager.register_character(test_character)

    with pytest.raises(ValueError):
        season_manager.schedule_activity("NonexistentCharacter", ActivityType.STUDY)


def test_season_advancement(season_manager):
    """Test proper season advancement and year changes."""
    initial_year = season_manager.current_year.year
    initial_season = season_manager.current_year.current_season

    # Advance through all seasons
    for _ in range(4):
        season_manager.execute_season()

    assert season_manager.current_year.year == initial_year + 1
    assert season_manager.current_year.current_season == initial_season
