import pytest
from unittest.mock import Mock
from pathlib import Path

from ars.character import Character
from ars.laboratory import Laboratory, LabEquipment, LabFeature, LabSpecialization
from ars.covenant import Covenant, CovenantSize
from ars.spell_research import ResearchProject, ResearchType
from ars.magic_items import MagicItem, ItemType, ItemEffect, InstallationType
from ars.core.types import (
    House, Form, Technique,
    AbilityType, Characteristic,
    Range, Duration, Target, Season
)
from ars.events import EventContext

@pytest.fixture
def game_context():
    """Provides the current game state context."""
    return EventContext(
        year=1220,
        season=Season.SPRING
    )

@pytest.fixture
def event_manager(game_context):
    """Provides a mock event manager that uses the game context."""
    manager = Mock()
    manager.context = game_context
    return manager

@pytest.fixture
def base_character(event_manager):
    """
    Provides a basic character fixture with:
    - Basic identification
    - House affiliation
    - Starting arts scores
    - Event manager integration
    """
    char = Character(
        name="Testus of Bonisagus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BONISAGUS
    )
    
    # Initialize basic arts scores
    char.techniques[Technique.CREO] = 10
    char.techniques[Technique.REGO] = 8
    char.forms[Form.IGNEM] = 8
    char.forms[Form.VIM] = 6
    
    # Set up event manager
    char.event_manager = event_manager
    
    # Initialize some basic characteristics
    char.characteristics[Characteristic.INTELLIGENCE] = 3
    char.characteristics[Characteristic.STAMINA] = 2
    
    # Initialize some basic abilities
    char.abilities[AbilityType.ARCANE]["Magic Theory"] = 4
    char.abilities[AbilityType.ARCANE]["Parma Magica"] = 1
    
    return char

@pytest.fixture
def base_laboratory():
    """
    Provides a basic laboratory fixture with:
    - Standard size and aura
    - Basic equipment
    - Standard features
    """
    lab = Laboratory(
        owner="Testus of Bonisagus",
        size=2,
        magical_aura=3,
        safety=1
    )
    
    # Add a basic feature
    lab.add_feature(LabFeature.ORGANIZED)
    
    return lab

@pytest.fixture
def base_covenant():
    """
    Provides a basic covenant fixture with:
    - Standard size and aura
    - Basic facilities
    """
    return Covenant(
        name="Test Covenant",
        size=CovenantSize.SMALL,
        age=10,
        aura=3,
        location="Test Location"
    )

@pytest.fixture
def base_equipment():
    """Provides a basic laboratory equipment fixture."""
    return LabEquipment(
        name="Precision Alembic",
        bonus=3,
        specialization=LabSpecialization.POTIONS,
        forms={Form.AQUAM},
        techniques={Technique.CREO},
        description="A finely crafted alembic for potion brewing"
    )

@pytest.fixture
def base_research_project(base_character):
    """Provides a basic research project fixture."""
    return ResearchProject(
        researcher=base_character.name,
        research_type=ResearchType.SPELL_CREATION,
        target_level=15,
        technique=Technique.CREO,
        form=Form.IGNEM
    )

@pytest.fixture
def base_magic_item():
    """Provides a basic magic item fixture."""
    return MagicItem(
        name="Test Ring",
        type=ItemType.INVESTED,
        creator="Testus of Bonisagus",
        base_material="Silver",
        size=1,
        shape_bonus=1,
        material_bonus=2,
        vis_capacity=10
    )

@pytest.fixture
def base_item_effect():
    """Provides a basic item effect fixture."""
    return ItemEffect(
        name="Flame Burst",
        technique=Technique.CREO,
        form=Form.IGNEM,
        level=10,
        installation_type=InstallationType.EFFECT
    )

@pytest.fixture
def tmp_saga_path(tmp_path):
    """Provides a temporary saga directory for file operations."""
    saga_path = tmp_path / "test_saga"
    saga_path.mkdir()
    return saga_path