import pytest

from ars.covenant import Building, BuildingType, Covenant, CovenantSize, VisSource
from ars.types import Form


@pytest.fixture
def sample_covenant():
    return Covenant(name="Test Covenant", size=CovenantSize.SMALL, age=10, aura=3)


@pytest.fixture
def sample_building():
    return Building(
        type=BuildingType.LABORATORY,
        name="Test Laboratory",
        size=2,
        quality=3,
        description="A well-equipped laboratory",
        maintenance_cost=5,
    )


@pytest.fixture
def sample_vis_source():
    return VisSource(
        name="Magic Spring",
        form=Form.AQUAM,
        amount=3,
        season="Spring",
        description="A magical spring that produces Aquam vis",
    )


def test_covenant_creation(sample_covenant):
    """Test basic covenant creation."""
    assert sample_covenant.name == "Test Covenant"
    assert sample_covenant.size == CovenantSize.SMALL
    assert sample_covenant.age == 10
    assert sample_covenant.aura == 3
    assert len(sample_covenant.buildings) == 0
    assert len(sample_covenant.vis_sources) == 0


def test_add_building(sample_covenant, sample_building):
    """Test adding a building to the covenant."""
    initial_expenses = sample_covenant.expenses
    sample_covenant.add_building(sample_building)

    assert len(sample_covenant.buildings) == 1
    assert sample_covenant.buildings[0].name == "Test Laboratory"
    assert sample_covenant.expenses == initial_expenses + sample_building.maintenance_cost


def test_add_vis_source(sample_covenant, sample_vis_source):
    """Test adding a vis source to the covenant."""
    sample_covenant.add_vis_source(sample_vis_source)

    assert len(sample_covenant.vis_sources) == 1
    assert sample_covenant.vis_sources[0].name == "Magic Spring"
    assert sample_covenant.vis_sources[0].form == Form.AQUAM


def test_collect_vis(sample_covenant, sample_vis_source):
    """Test collecting vis from sources."""
    sample_covenant.add_vis_source(sample_vis_source)

    # First collection
    collected = sample_covenant.collect_vis("Spring")
    assert collected[Form.AQUAM] == 3
    assert sample_covenant.vis_stocks[Form.AQUAM] == 3

    # Second collection in same season should yield nothing as source is claimed
    collected = sample_covenant.collect_vis("Spring")
    assert collected[Form.AQUAM] == 0


def test_library_management(sample_covenant):
    """Test library book management."""
    sample_covenant.add_book("Art of Magic", 5)

    assert "Art of Magic" in sample_covenant.library.books
    assert sample_covenant.library.books["Art of Magic"] == 5

    # Test library capacity
    for i in range(sample_covenant.library.capacity):
        sample_covenant.add_book(f"Book {i}", 1)

    with pytest.raises(ValueError):
        sample_covenant.add_book("One Too Many", 1)


def test_covenant_finances(sample_covenant, sample_building):
    """Test covenant financial calculations."""
    initial_income = sample_covenant.calculate_income()
    initial_expenses = sample_covenant.calculate_expenses()

    sample_covenant.add_building(sample_building)

    # Expenses should increase by building maintenance
    assert sample_covenant.calculate_expenses() == initial_expenses + sample_building.maintenance_cost
    # Income should remain the same
    assert sample_covenant.calculate_income() == initial_income


def test_save_load(sample_covenant, sample_building, sample_vis_source, tmp_path):
    """Test saving and loading covenant data."""
    # Add some data to save
    sample_covenant.add_building(sample_building)
    sample_covenant.add_vis_source(sample_vis_source)
    sample_covenant.add_book("Test Book", 3)

    # Save covenant
    sample_covenant.save(directory=tmp_path)

    # Load covenant
    loaded_covenant = Covenant.load(sample_covenant.name, directory=tmp_path)

    # Verify data
    assert loaded_covenant.name == sample_covenant.name
    assert loaded_covenant.size == sample_covenant.size
    assert len(loaded_covenant.buildings) == 1
    assert loaded_covenant.buildings[0].name == "Test Laboratory"
    assert len(loaded_covenant.vis_sources) == 1
    assert loaded_covenant.vis_sources[0].name == "Magic Spring"
    assert "Test Book" in loaded_covenant.library.books


def test_building_types():
    """Test building type enumeration."""
    assert BuildingType.LABORATORY.value == "Laboratory"
    assert BuildingType.LIBRARY.value == "Library"
    building = Building(type=BuildingType.TOWER, name="Wizard's Tower", size=3, quality=4)
    assert building.type == BuildingType.TOWER


def test_covenant_size():
    """Test covenant size enumeration."""
    assert CovenantSize.SMALL.value == "Small"
    assert CovenantSize.MEDIUM.value == "Medium"
    covenant = Covenant(name="Test Covenant", size=CovenantSize.LARGE, age=50)
    assert covenant.size == CovenantSize.LARGE


def test_vis_source_claiming():
    """Test vis source claiming mechanism."""
    source = VisSource(name="Test Source", form=Form.IGNEM, amount=5, season="Summer", description="Test")

    assert not source.claimed
    source.claimed = True
    assert source.claimed


def test_covenant_population(sample_covenant):
    """Test covenant population management."""
    sample_covenant.magi.append("Testus of Bonisagus")
    sample_covenant.covenfolk = 20
    sample_covenant.grogs = 10

    assert len(sample_covenant.magi) == 1
    assert sample_covenant.covenfolk == 20
    assert sample_covenant.grogs == 10
