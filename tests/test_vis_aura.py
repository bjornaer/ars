import pytest

from ars.core.types import Form
from ars.vis_aura import AuraManager, AuraProperties, AuraType, VisManager, VisSource, VisType


@pytest.fixture
def test_aura():
    return AuraProperties(
        type=AuraType.MAGIC,
        strength=3,
        properties=["Stable", "Strong at night"],
        modifiers={"magical_activities": 1, "vis_extraction": 2},
    )


@pytest.fixture
def test_vis_source():
    return VisSource(
        form=Form.IGNEM,
        amount=5,
        type=VisType.RAW,
        season="Summer",
        location="Sacred Grove",
        description="A mystical grove that produces vis",
    )


@pytest.fixture
def aura_manager():
    return AuraManager()


@pytest.fixture
def vis_manager():
    return VisManager()


class TestAuraSystem:
    """Tests for the aura management system."""

    def test_aura_registration(self, aura_manager, test_aura):
        """Test registering and retrieving auras."""
        location = "Test Location"
        aura_manager.register_aura(location, test_aura)

        retrieved_aura = aura_manager.get_aura(location)
        assert retrieved_aura == test_aura
        assert retrieved_aura.strength == 3
        assert retrieved_aura.type == AuraType.MAGIC
        assert "Stable" in retrieved_aura.properties

    def test_aura_strength_calculation(self, test_aura):
        """Test calculating effective aura strength."""
        test_aura.fluctuations = {"Summer": 1, "Winter": -1}

        assert test_aura.calculate_effective_strength("Summer") == 4
        assert test_aura.calculate_effective_strength("Winter") == 2
        assert test_aura.calculate_effective_strength() == 3

    def test_aura_effects(self, aura_manager, test_aura):
        """Test calculating aura effects on activities."""
        location = "Test Location"
        aura_manager.register_aura(location, test_aura)

        effects = aura_manager.calculate_aura_effects(location, "spell_casting", "Summer")

        assert effects["magical_activities"] == 3
        assert effects["spell_casting"] == 3
        assert effects["vis_extraction"] == 2

    def test_different_aura_types(self, aura_manager):
        """Test effects of different aura types."""
        for aura_type in AuraType:
            aura = AuraProperties(type=aura_type, strength=3)
            location = f"Test {aura_type.value}"
            aura_manager.register_aura(location, aura)

            effects = aura_manager.calculate_aura_effects(location, "generic_activity")

            if aura_type == AuraType.MAGIC:
                assert "magical_activities" in effects
            elif aura_type == AuraType.FAERIE:
                assert "faerie_magic" in effects
            elif aura_type == AuraType.DIVINE:
                assert "divine_power" in effects
            elif aura_type == AuraType.INFERNAL:
                assert "corruption" in effects


class TestVisSystem:
    """Tests for the vis management system."""

    def test_vis_source_registration(self, vis_manager, test_vis_source):
        """Test registering and retrieving vis sources."""
        vis_manager.register_source("Test Source", test_vis_source)
        assert "Test Source" in vis_manager.sources
        assert vis_manager.sources["Test Source"].form == Form.IGNEM
        assert vis_manager.sources["Test Source"].amount == 5

    def test_vis_collection(self, vis_manager, test_vis_source):
        """Test collecting vis from a source."""
        vis_manager.register_source("Test Source", test_vis_source)

        # Test collecting in wrong season
        form, amount = vis_manager.collect_vis("Test Source", 1220, "Winter", 0)
        assert amount == 0

        # Test collecting in correct season
        form, amount = vis_manager.collect_vis("Test Source", 1220, "Summer", 0)
        assert amount == 5
        assert form == Form.IGNEM
        assert vis_manager.stocks[Form.IGNEM] == 5

        # Test collecting twice in same year
        form, amount = vis_manager.collect_vis("Test Source", 1220, "Summer", 0)
        assert amount == 0

    def test_vis_collection_with_aura(self, vis_manager, test_vis_source):
        """Test vis collection with aura bonus."""
        vis_manager.register_source("Test Source", test_vis_source)

        form, amount = vis_manager.collect_vis("Test Source", 1220, "Summer", 4)
        assert amount == 7  # Base 5 + (4 // 2) = 7

    def test_vis_usage(self, vis_manager):
        """Test using vis from stocks."""
        vis_manager.stocks[Form.IGNEM] = 10

        # Test successful usage
        assert vis_manager.use_vis(Form.IGNEM, 5)
        assert vis_manager.stocks[Form.IGNEM] == 5

        # Test insufficient vis
        assert not vis_manager.use_vis(Form.IGNEM, 10)
        assert vis_manager.stocks[Form.IGNEM] == 5

    def test_vis_transfer(self, vis_manager):
        """Test transferring vis between managers."""
        other_manager = VisManager()
        vis_manager.stocks[Form.IGNEM] = 10

        # Test successful transfer
        assert vis_manager.transfer_vis(Form.IGNEM, 5, other_manager)
        assert vis_manager.stocks[Form.IGNEM] == 5
        assert other_manager.stocks[Form.IGNEM] == 5

        # Test insufficient vis
        assert not vis_manager.transfer_vis(Form.IGNEM, 10, other_manager)

    def test_vis_save_load(self, vis_manager, test_vis_source, tmp_path):
        """Test saving and loading vis data."""
        vis_manager.register_source("Test Source", test_vis_source)
        vis_manager.stocks[Form.IGNEM] = 10

        # Save
        filepath = tmp_path / "vis_test.yml"
        vis_manager.save(filepath)

        # Load
        loaded_manager = VisManager.load(filepath)

        assert "Test Source" in loaded_manager.sources
        assert loaded_manager.stocks[Form.IGNEM] == 10
        assert loaded_manager.sources["Test Source"].form == Form.IGNEM
        assert loaded_manager.sources["Test Source"].amount == 5


class TestIntegration:
    """Integration tests for vis and aura systems."""

    def test_aura_vis_interaction(self, aura_manager, vis_manager, test_vis_source):
        """Test interaction between auras and vis collection."""
        # Setup
        location = "Magic Grove"
        _ = AuraProperties(type=AuraType.MAGIC, strength=4, modifiers={"vis_extraction": 2})

        aura_manager.register_aura(location, test_vis_source.location)
        vis_manager.register_source("Grove Source", test_vis_source)

        # Test collection with aura effects
        effects = aura_manager.calculate_aura_effects(location, "vis_extraction", "Summer")
        _, amount = vis_manager.collect_vis("Grove Source", 1220, "Summer", effects.get("vis_extraction", 0))

        assert amount > test_vis_source.amount  # Should be boosted by aura

    def test_seasonal_variations(self, test_aura, test_vis_source):
        """Test seasonal variations in aura and vis collection."""
        test_aura.fluctuations = {"Spring": 1, "Summer": 2, "Autumn": -1, "Winter": -2}

        # Test each season
        seasons = ["Spring", "Summer", "Autumn", "Winter"]
        expected_strengths = [4, 5, 2, 1]

        for season, expected in zip(seasons, expected_strengths, strict=False):
            assert test_aura.calculate_effective_strength(season) == expected
