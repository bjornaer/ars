import pytest

from ars.adventure import Adventure, AdventureManager, AdventureType, Encounter, EncounterType, RewardType
from ars.character import Character
from ars.core.types import House


@pytest.fixture
def test_character():
    char = Character(
        name="Testus",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        house=House.BJORNAER,
        age=45,
    )
    # Add some abilities and arts
    char.abilities = {"Magic Theory": 4, "Single Weapon": 3, "Leadership": 2}
    char.techniques = {"Creo": 10, "Rego": 8}
    char.forms = {"Ignem": 8, "Vim": 6}
    return char


@pytest.fixture
def test_adventure():
    return Adventure(
        name="Test Quest",
        type=AdventureType.QUEST,
        description="A test adventure",
        location="Test Location",
        season="Spring",
        year=1220,
        difficulty=3,
    )


@pytest.fixture
def test_manager():
    return AdventureManager()


def test_create_adventure(test_manager):
    """Test adventure creation."""
    adv = test_manager.create_adventure(
        name="New Quest",
        type=AdventureType.QUEST,
        description="Test description",
        location="Test Location",
        season="Spring",
        year=1220,
        difficulty=3,
    )

    assert adv.name == "New Quest"
    assert adv.type == AdventureType.QUEST
    assert adv.status == "Not Started"
    assert len(adv.encounters) == 0
    assert adv in test_manager.adventures.values()


def test_add_encounter(test_manager, test_adventure):
    """Test adding encounters to an adventure."""
    test_manager.adventures["Test Quest"] = test_adventure

    success = test_manager.add_encounter(
        adventure_name="Test Quest",
        encounter_type=EncounterType.COMBAT,
        difficulty=4,
        description="Test combat",
        requirements={"Single Weapon": 2},
        rewards={RewardType.EXPERIENCE: {"Single Weapon": 5}},
    )

    assert success
    assert len(test_adventure.encounters) == 1
    assert test_adventure.encounters[0].type == EncounterType.COMBAT


def test_start_adventure(test_manager, test_adventure, test_character):
    """Test starting an adventure."""
    test_manager.adventures["Test Quest"] = test_adventure

    result = test_manager.start_adventure("Test Quest", [test_character])

    assert "error" not in result
    assert result["status"] == "started"
    assert test_character.name in result["participants"]
    assert test_adventure.status == "In Progress"


def test_resolve_encounter(test_manager, test_adventure, test_character):
    """Test resolving encounters."""
    # Setup
    test_manager.adventures["Test Quest"] = test_adventure
    test_manager.add_encounter(
        "Test Quest",
        EncounterType.MAGICAL,
        4,
        "Test magic encounter",
        {"Magic Theory": 3},
        {RewardType.VIS: {"Ignem": 2}},
    )
    test_manager.start_adventure("Test Quest", [test_character])

    # Test resolution
    actions = {test_character.name: {"technique": "Creo", "form": "Ignem"}}

    result = test_manager.resolve_encounter(0, actions)

    assert "error" not in result
    assert "success" in result
    assert "results" in result
    assert test_character.name in result["results"]


def test_participant_requirements(test_manager, test_adventure, test_character):
    """Test participant requirement checking."""
    test_adventure.type = AdventureType.MAGICAL
    test_adventure.difficulty = 8
    test_manager.adventures["Test Quest"] = test_adventure

    # Character meets requirements
    assert test_manager._check_participant_requirements(test_character, test_adventure)

    # Character doesn't meet requirements
    test_character.abilities["Magic Theory"] = 2
    assert not test_manager._check_participant_requirements(test_character, test_adventure)


def test_calculate_base_chance(test_manager, test_character):
    """Test base chance calculations."""
    encounter = Encounter(type=EncounterType.MAGICAL, difficulty=4, description="Test")

    # Test magical action
    action_data = {"technique": "Creo", "form": "Ignem"}
    base = test_manager._calculate_base_chance(test_character, action_data, encounter)
    assert base == 18  # Creo 10 + Ignem 8

    # Test combat action
    encounter.type = EncounterType.COMBAT
    action_data = {"weapon_ability": "Single Weapon", "characteristic": "Dexterity"}
    base = test_manager._calculate_base_chance(test_character, action_data, encounter)
    assert base == 9  # Single Weapon 3 * 3


def test_distribute_rewards(test_manager, test_adventure, test_character):
    """Test reward distribution."""
    # Setup
    test_manager.adventures["Test Quest"] = test_adventure
    test_manager.add_encounter(
        "Test Quest",
        EncounterType.MAGICAL,
        4,
        "Test encounter",
        {},
        {RewardType.VIS: {"Ignem": 3}, RewardType.EXPERIENCE: {"Magic Theory": 5}},
    )

    # Start and complete adventure
    test_manager.start_adventure("Test Quest", [test_character])
    test_manager.active_adventure.encounters[0].completed = True

    # Distribute rewards
    test_manager._distribute_rewards()

    # Check character received rewards
    assert test_character.vis.get("Ignem", 0) == 3
    assert test_character.experience.get("Magic Theory", 0) == 5


def test_save_load_state(test_manager, test_adventure, tmp_path):
    """Test saving and loading adventure state."""
    # Setup
    test_manager.adventures["Test Quest"] = test_adventure
    test_manager.add_encounter("Test Quest", EncounterType.COMBAT, 4, "Test combat")

    # Save state
    filepath = tmp_path / "test_adventures.yml"
    test_manager.save_state(filepath)

    # Load state
    loaded_manager = AdventureManager.load_state(filepath)

    # Verify
    assert "Test Quest" in loaded_manager.adventures
    loaded_adv = loaded_manager.adventures["Test Quest"]
    assert loaded_adv.name == test_adventure.name
    assert loaded_adv.type == test_adventure.type
    assert len(loaded_adv.encounters) == 1


def test_adventure_completion(test_manager, test_adventure, test_character):
    """Test adventure completion mechanics."""
    # Setup
    test_manager.adventures["Test Quest"] = test_adventure
    test_manager.add_encounter("Test Quest", EncounterType.MAGICAL, 4, "Test encounter 1")
    test_manager.add_encounter("Test Quest", EncounterType.COMBAT, 3, "Test encounter 2")

    test_manager.start_adventure("Test Quest", [test_character])

    # Complete first encounter
    actions = {test_character.name: {"technique": "Creo", "form": "Ignem"}}
    result = test_manager.resolve_encounter(0, actions)
    assert test_adventure.status == "In Progress"

    # Complete second encounter
    actions = {test_character.name: {"weapon_ability": "Single Weapon", "characteristic": "Dexterity"}}
    result = test_manager.resolve_encounter(1, actions)

    assert "success" in result
    assert "results" in result
    assert test_character.name in result["results"]

    # Check if adventure completed
    assert all(e.completed for e in test_adventure.encounters)
    assert test_adventure.status == "Completed"


def test_botch_and_critical(test_manager, test_character):
    """Test botch and critical success mechanics."""
    encounter = Encounter(type=EncounterType.MAGICAL, difficulty=4, description="Test")

    # Test botch
    effects = test_manager._calculate_effects(success=False, roll=0, base_chance=10, encounter=encounter)  # Botch roll
    assert "botch" in effects

    # Test critical
    effects = test_manager._calculate_effects(
        success=True, roll=9, base_chance=10, encounter=encounter  # Critical roll
    )
    assert effects["critical"]


def test_invalid_adventure_operations(test_manager):
    """Test handling of invalid operations."""
    # Test invalid adventure name
    result = test_manager.start_adventure("NonexistentQuest", [])
    assert "error" in result

    # Test invalid encounter index
    result = test_manager.resolve_encounter(99, {})
    assert "error" in result

    # Test resolving encounter with no active adventure
    result = test_manager.resolve_encounter(0, {})
    assert "error" in result
