import pytest

from ars.character import Character
from ars.laboratory import Laboratory
from ars.magic_items import InstallationType, ItemCreationManager, ItemEffect, ItemType, MagicItem
from ars.types import Form, Technique
from ars.vis_aura import VisManager


@pytest.fixture
def test_character():
    char = Character(name="Testus", player="Test Player", saga="Test Saga", covenant="Test Covenant")
    char.techniques["Creo"] = 10
    char.forms["Ignem"] = 8
    return char


@pytest.fixture
def test_laboratory():
    return Laboratory(owner="Testus", size=0, magical_aura=3)


@pytest.fixture
def test_item():
    return MagicItem(
        name="Test Ring",
        type=ItemType.INVESTED,
        creator="Testus",
        base_material="Silver",
        size=1,
        shape_bonus=1,
        material_bonus=2,
        vis_capacity=15,
    )


@pytest.fixture
def test_effect():
    return ItemEffect(
        name="Flame Burst",
        technique=Technique.CREO,
        form=Form.IGNEM,
        level=10,
        installation_type=InstallationType.EFFECT,
        uses_per_day=5,
    )


@pytest.fixture
def item_manager():
    return ItemCreationManager()


class TestMagicItem:
    """Tests for magic item functionality."""

    def test_item_creation(self):
        """Test basic item creation."""
        item = MagicItem(name="Test Item", type=ItemType.INVESTED, creator="Testus", base_material="Iron", size=2)

        assert item.name == "Test Item"
        assert item.type == ItemType.INVESTED
        assert len(item.effects) == 0

    def test_total_bonus_calculation(self, test_item):
        """Test bonus calculation."""
        test_item.shape_bonus = 2
        test_item.material_bonus = 3
        test_item.attunement_bonus = 1
        test_item.aura_bonus = 2

        assert test_item.calculate_total_bonus() == 8

    def test_capacity_management(self, test_item, test_effect):
        """Test vis capacity management."""
        initial_capacity = test_item.vis_capacity
        test_effect.vis_required = {Form.CREO: 3, Form.IGNEM: 2}

        assert test_item.can_add_effect(test_effect)
        test_item.effects.append(test_effect)
        test_item.current_capacity += sum(test_effect.vis_required.values())

        assert test_item.calculate_remaining_capacity() == initial_capacity - 5

    def test_item_type_restrictions(self):
        """Test item type specific restrictions."""
        charged_item = MagicItem(
            name="Charged Item", type=ItemType.CHARGED, creator="Testus", base_material="Wood", size=1
        )

        effect1 = ItemEffect(name="Effect 1", technique=Technique.CREO, form=Form.IGNEM, level=5)
        effect2 = ItemEffect(name="Effect 2", technique=Technique.CREO, form=Form.IGNEM, level=5)

        assert charged_item.can_add_effect(effect1)
        charged_item.effects.append(effect1)
        assert not charged_item.can_add_effect(effect2)


class TestItemEffect:
    """Tests for magical effects."""

    def test_effect_creation(self):
        """Test effect creation."""
        effect = ItemEffect(
            name="Test Effect",
            technique=Technique.CREO,
            form=Form.IGNEM,
            level=15,
            installation_type=InstallationType.TRIGGER,
            trigger_condition="When touched",
        )

        assert effect.name == "Test Effect"
        assert effect.level == 15
        assert effect.trigger_condition == "When touched"

    def test_effect_installation_types(self):
        """Test different installation types."""
        effect = ItemEffect(name="Complex Effect", technique=Technique.CREO, form=Form.IGNEM, level=20)

        for installation_type in InstallationType:
            effect.installation_type = installation_type
            assert effect.installation_type == installation_type


class TestItemCreationManager:
    """Tests for item creation process."""

    def test_project_start(self, item_manager, test_character, test_laboratory, test_item, test_effect):
        """Test starting a new project."""
        success = item_manager.start_project(test_character, test_laboratory, test_item, test_effect)

        assert success
        assert test_character.name in item_manager.current_projects
        assert test_effect.lab_total > 0
        assert test_effect.seasons_required > 0

    def test_vis_requirements(self, item_manager, test_effect):
        """Test vis requirement calculations."""
        vis_reqs = item_manager._calculate_vis_requirements(test_effect, ItemType.INVESTED)

        assert Form.CREO in vis_reqs
        assert Form.IGNEM in vis_reqs
        assert vis_reqs[Form.CREO] > vis_reqs[Form.IGNEM]

    def test_project_continuation(self, item_manager, test_character, test_laboratory, test_item, test_effect):
        """Test project progression."""
        vis_manager = VisManager()
        # Add sufficient vis
        vis_manager.stocks[Form.CREO] = 10
        vis_manager.stocks[Form.IGNEM] = 10

        # Start project
        item_manager.start_project(test_character, test_laboratory, test_item, test_effect)

        # Continue project
        result = item_manager.continue_project(test_character, test_laboratory, vis_manager)

        assert "status" in result
        if result["status"] == "completed":
            assert test_effect in test_item.effects
        else:
            assert "seasons_remaining" in result

    def test_project_serialization(
        self, item_manager, test_character, test_laboratory, test_item, test_effect, tmp_path
    ):
        """Test saving and loading project state."""
        # Start a project
        item_manager.start_project(test_character, test_laboratory, test_item, test_effect)

        # Save state
        filepath = tmp_path / "test_projects.yml"
        item_manager.save_state(filepath)

        # Load state
        loaded_manager = ItemCreationManager.load_state(filepath)

        assert test_character.name in loaded_manager.current_projects
        loaded_item, loaded_effect = loaded_manager.current_projects[test_character.name]
        assert loaded_item.name == test_item.name
        assert loaded_effect.name == test_effect.name


def test_integration_with_laboratory(item_manager, test_character, test_laboratory, test_item, test_effect):
    """Test integration with laboratory system."""
    # Add laboratory specialization
    test_laboratory.specializations = {"enchantment": 3}

    item_manager.start_project(test_character, test_laboratory, test_item, test_effect)

    # Lab total should include specialization
    assert test_effect.lab_total > (
        test_character.techniques["Creo"] + test_character.forms["Ignem"] + test_laboratory.magical_aura
    )


def test_integration_with_vis_system(item_manager, test_character, test_laboratory, test_item, test_effect):
    """Test integration with vis system."""
    vis_manager = VisManager()

    # Start project without vis
    item_manager.start_project(test_character, test_laboratory, test_item, test_effect)

    # Should fail due to lack of vis
    result = item_manager.continue_project(test_character, test_laboratory, vis_manager)
    assert "error" in result

    # Add vis and try again
    vis_manager.stocks[Form.CREO] = 10
    vis_manager.stocks[Form.IGNEM] = 10

    result = item_manager.continue_project(test_character, test_laboratory, vis_manager)
    assert "error" not in result


def test_complex_item_creation(item_manager, test_character, test_laboratory):
    """Test creating a complex item with multiple effects."""
    # Create a greater enchanted item
    item = MagicItem(
        name="Staff of Elements",
        type=ItemType.GREATER,
        creator=test_character.name,
        base_material="Heartwood",
        size=3,
        shape_bonus=3,
        material_bonus=3,
        vis_capacity=25,
    )

    # Create multiple effects
    effects = [
        ItemEffect(
            name="Flame Strike",
            technique=Technique.CREO,
            form=Form.IGNEM,
            level=15,
            installation_type=InstallationType.TRIGGER,
            trigger_condition="When commanded",
        ),
        ItemEffect(
            name="Water Blast",
            technique=Technique.CREO,
            form=Form.AQUAM,
            level=10,
            installation_type=InstallationType.TRIGGER,
            trigger_condition="When tapped",
        ),
    ]

    # Add effects sequentially
    vis_manager = VisManager()
    vis_manager.stocks = {form: 20 for form in Form}  # Add plenty of vis

    for effect in effects:
        assert item_manager.start_project(test_character, test_laboratory, item, effect)

        while True:
            result = item_manager.continue_project(test_character, test_laboratory, vis_manager)
            if result.get("status") == "completed":
                break

    assert len(item.effects) == 2
    assert item.current_capacity > 0
    assert item.calculate_remaining_capacity() < item.vis_capacity
