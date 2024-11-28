from unittest.mock import Mock, patch

import pytest

from ars.character import Character
from ars.events import EventType
from ars.laboratory import Laboratory
from ars.core.types import Season
from ars.spell_research import ResearchProject, ResearchResult, ResearchType, SpellResearchManager
from ars.core.types import Form, Technique


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def research_manager(event_manager):
    return SpellResearchManager(event_manager)


@pytest.fixture
def test_character():
    char = Character(
        name="Testus of Bonisagus", player="Test Player", saga="Test Saga", covenant="Test Covenant", house="Bonisagus"
    )
    char.techniques = {"Creo": 10, "Rego": 8}
    char.forms = {"Ignem": 8, "Vim": 6}
    return char


@pytest.fixture
def test_laboratory():
    return Laboratory(owner="Testus of Bonisagus", size=3, magical_aura=3)


@pytest.fixture
def test_project():
    return ResearchProject(
        researcher="Testus of Bonisagus",
        research_type=ResearchType.SPELL_CREATION,
        target_level=15,
        technique=Technique.CREO,
        form=Form.IGNEM,
    )


class TestSpellResearch:
    def test_conduct_research(self, research_manager, test_character, test_laboratory, test_project, event_manager):
        """Test basic research conduct with event recording."""
        result = research_manager.conduct_research(
            test_project, test_character, test_laboratory, year=1220, season=Season.SPRING
        )

        assert isinstance(result, ResearchResult)
        assert result.points_gained > 0

        event = event_manager.record_event.call_args[0][0]
        assert event.type == EventType.RESEARCH
        assert test_character.name in event.description
        assert event.details["points_gained"] == result.points_gained

    def test_breakthrough_research(
        self, research_manager, test_character, test_laboratory, test_project, event_manager
    ):
        """Test research with breakthrough."""
        # Patch to ensure high research points
        with patch("ars.laboratory.Laboratory.calculate_lab_total", return_value=50):
            result = research_manager.conduct_research(
                test_project, test_character, test_laboratory, year=1220, season=Season.SPRING
            )

            assert result.breakthrough
            event = event_manager.record_event.call_args[0][0]
            assert event.details["breakthrough"] is True

    def test_warping_from_research(
        self, research_manager, test_character, test_laboratory, test_project, event_manager
    ):
        """Test warping points from high-aura research."""
        # Set high aura
        test_laboratory.magical_aura = 8

        result = research_manager.conduct_research(
            test_project, test_character, test_laboratory, year=1220, season=Season.SPRING
        )

        assert result.warping_points > 0
        event = event_manager.record_event.call_args[0][0]
        assert event.details["warping_points"] > 0

    def test_laboratory_conditions(
        self, research_manager, test_character, test_laboratory, test_project, event_manager
    ):
        """Test research with various laboratory conditions."""
        # Add some lab conditions
        test_laboratory.specializations = ["Ignem research"]
        test_laboratory.features = ["Well-organized"]

        result = research_manager.conduct_research(
            test_project, test_character, test_laboratory, year=1220, season=Season.SPRING
        )

        assert result.points_gained > 0

        event = event_manager.record_event.call_args[0][0]
        assert "laboratory_conditions" in event.details
        assert event.details["laboratory_conditions"]["aura"] == test_laboratory.magical_aura

    def test_seasonal_research_tracking(
        self, research_manager, test_character, test_laboratory, test_project, event_manager
    ):
        """Test research across multiple seasons."""
        # Conduct research in different seasons
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]

        for season in seasons:
            result = research_manager.conduct_research(
                test_project, test_character, test_laboratory, year=1220, season=season
            )

            assert result.points_gained > 0

            event = event_manager.record_event.call_args[0][0]
            assert event.season == season
            assert event.year == 1220
