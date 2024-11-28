from unittest.mock import Mock

import pytest

from ars.events import EventType
from ars.core.types import Season
from ars.core.types import Form
from ars.vis_aura import VisManager, VisSource, VisType


@pytest.fixture
def event_manager():
    return Mock()


@pytest.fixture
def vis_manager(event_manager):
    return VisManager(event_manager)


@pytest.fixture
def test_source():
    return VisSource(
        form=Form.AQUAM,
        amount=3,
        type=VisType.RAW,
        season="Spring",
        location="Sacred Grove",
        description="A magical spring",
    )


class TestVisManager:
    def test_vis_collection_with_events(self, vis_manager, test_source, event_manager):
        """Test vis collection with event recording."""
        vis_manager.register_source("spring_source", test_source)

        form, amount = vis_manager.collect_vis(
            source_name="spring_source", year=1220, season="Spring", aura_strength=5, collector="Marcus"
        )

        assert form == Form.AQUAM
        assert amount == 4  # Base 3 + aura bonus

        # Verify events were recorded
        assert event_manager.add_event.call_count == 2  # Registration and collection
        collection_event = event_manager.add_event.call_args[0][0]
        assert collection_event.type == EventType.VIS_COLLECTION
        assert collection_event.details["amount"] == 4
        assert collection_event.details["collector"] == "Marcus"

    def test_vis_transfer_with_events(self, vis_manager, event_manager):
        """Test vis transfer with event recording."""
        target_manager = VisManager()
        vis_manager.stocks[Form.IGNEM] = 5

        success = vis_manager.transfer_vis(
            form=Form.IGNEM, amount=3, target_manager=target_manager, year=1220, season=Season.SPRING
        )

        assert success
        assert vis_manager.stocks[Form.IGNEM] == 2
        assert target_manager.stocks[Form.IGNEM] == 3

        event = event_manager.add_event.call_args[0][0]
        assert event.type == EventType.VIS_TRANSFER
        assert event.details["amount"] == 3
