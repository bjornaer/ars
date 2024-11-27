import pytest

from ars.covenant_economy import (
    Book,
    BuildingProject,
    CovenantEconomy,
    MagicalResource,
    MundaneResource,
    Personnel,
    ResourceCategory,
)
from ars.types import Form


@pytest.fixture
def test_economy():
    return CovenantEconomy("Test Covenant")


@pytest.fixture
def test_mundane_resource():
    return MundaneResource(
        name="Test Building",
        category=ResourceCategory.INFRASTRUCTURE,
        quality=5,
        maintenance_cost=2.0,
        type="building",
        size=2,
        workers_required=3,
    )


@pytest.fixture
def test_magical_resource():
    return MagicalResource(
        name="Magic Item",
        category=ResourceCategory.MAGICAL,
        quality=7,
        maintenance_cost=1.0,
        magical_bonus=3,
        form=Form.IGNEM,
        charges=10,
    )


@pytest.fixture
def test_book():
    return Book(
        name="Summa on Magic Theory",
        category=ResourceCategory.BOOKS,
        quality=6,
        maintenance_cost=0.5,
        level=10,
        subject="Magic Theory",
        author="Bonisagus",
        copies=2,
    )


@pytest.fixture
def test_personnel():
    return Personnel(
        name="Master Craftsman",
        category=ResourceCategory.PERSONNEL,
        quality=8,
        maintenance_cost=5.0,
        role="craftsman",
        abilities={"Craft": 5, "Leadership": 3},
        salary=10.0,
        loyalty=75,
    )


def test_add_resource(test_economy, test_mundane_resource):
    """Test adding resources."""
    assert test_economy.add_resource(test_mundane_resource)
    assert test_mundane_resource.name in test_economy.resources

    # Test adding duplicate resource
    assert not test_economy.add_resource(test_mundane_resource)


def test_remove_resource(test_economy, test_mundane_resource):
    """Test removing resources."""
    test_economy.add_resource(test_mundane_resource)
    removed = test_economy.remove_resource(test_mundane_resource.name)

    assert removed == test_mundane_resource
    assert test_mundane_resource.name not in test_economy.resources


def test_income_management(test_economy):
    """Test income source management."""
    test_economy.add_income_source("Taxes", 50.0)
    test_economy.add_income_source("Trade", 30.0)

    assert "Taxes" in test_economy.income_sources
    assert test_economy.income_sources["Taxes"] == 50.0
    assert test_economy.income_sources["Trade"] == 30.0


def test_expense_management(test_economy):
    """Test expense management."""
    test_economy.add_expense("Maintenance", 20.0)
    test_economy.add_expense("Salaries", 40.0)

    assert "Maintenance" in test_economy.expenses
    assert test_economy.expenses["Maintenance"] == 20.0
    assert test_economy.expenses["Salaries"] == 40.0


def test_project_management(test_economy):
    """Test building project management."""
    project = BuildingProject(name="New Tower", type="tower", cost=100.0, seasons_required=4)

    # Test starting project with insufficient funds
    assert not test_economy.start_project(project)

    # Test starting project with sufficient funds
    test_economy.treasury = 200.0
    assert test_economy.start_project(project)
    assert project.name in test_economy.projects
    assert test_economy.treasury == 100.0  # Cost deducted

    # Test starting duplicate project
    assert not test_economy.start_project(project)


def test_season_processing(test_economy, test_mundane_resource, test_personnel):
    """Test seasonal processing."""
    # Setup initial state
    test_economy.treasury = 100.0
    test_economy.add_resource(test_mundane_resource)
    test_economy.add_resource(test_personnel)
    test_economy.add_income_source("Taxes", 50.0)
    test_economy.add_expense("Maintenance", 20.0)

    results = test_economy.process_season("Spring", 1220)

    assert results["income"] == 50.0
    assert results["expenses"] > 0
    assert len(results["resources"]) > 0
    assert test_economy.treasury > 0


def test_resource_deterioration(test_economy, test_mundane_resource):
    """Test resource deterioration mechanics."""
    test_economy.add_resource(test_mundane_resource)
    initial_condition = test_mundane_resource.condition

    test_economy.process_season("Winter", 1220)  # Winter should cause more wear

    assert test_mundane_resource.condition < initial_condition


def test_project_progress(test_economy):
    """Test project progress tracking."""
    test_economy.treasury = 200.0
    project = BuildingProject(name="New Tower", type="tower", cost=100.0, seasons_required=2, workers_assigned=3)

    test_economy.start_project(project)

    # Add necessary workers
    for i in range(3):
        test_economy.add_resource(
            Personnel(
                name=f"Worker_{i}",
                category=ResourceCategory.PERSONNEL,
                quality=3,
                role="worker",
                abilities={},
                salary=5.0,
            )
        )

    # Process two seasons
    test_economy.process_season("Spring", 1220)
    assert project.seasons_completed == 1
    assert project.status == "In Progress"

    test_economy.process_season("Summer", 1220)
    assert project.seasons_completed == 2
    assert project.status == "Completed"


def test_resource_requirements(test_economy):
    """Test resource requirement checking."""
    project = BuildingProject(
        name="New Tower", type="tower", cost=100.0, seasons_required=2, resources_committed={"Stone": 10}
    )

    # Add stone resource
    stone = MundaneResource(name="Stone", category=ResourceCategory.MUNDANE, quality=5, type="material", size=1)
    test_economy.add_resource(stone)

    test_economy.treasury = 200.0
    assert test_economy.start_project(project)


def test_save_load_state(test_economy, tmp_path):
    """Test saving and loading economic state."""
    # Setup initial state
    test_economy.treasury = 100.0
    test_economy.add_income_source("Taxes", 50.0)
    test_economy.add_expense("Maintenance", 20.0)
    test_economy.add_resource(
        MundaneResource(
            name="Test Building", category=ResourceCategory.INFRASTRUCTURE, quality=5, type="building", size=2
        )
    )

    # Save state
    filepath = tmp_path / "test_economy.yml"
    test_economy.save_state(filepath)

    # Load state
    loaded_economy = CovenantEconomy.load_state(filepath)

    # Verify
    assert loaded_economy.covenant_name == test_economy.covenant_name
    assert loaded_economy.treasury == test_economy.treasury
    assert loaded_economy.income_sources == test_economy.income_sources
    assert loaded_economy.expenses == test_economy.expenses
    assert len(loaded_economy.resources) == len(test_economy.resources)


def test_magical_resource_handling(test_economy, test_magical_resource):
    """Test magical resource specific features."""
    test_economy.add_resource(test_magical_resource)

    # Test charge usage
    initial_charges = test_magical_resource.charges
    test_economy.process_season("Spring", 1220)

    # Charges should decrease with use
    assert test_magical_resource.charges <= initial_charges


def test_book_management(test_economy, test_book):
    """Test book resource specific features."""
    test_economy.add_resource(test_book)

    # Books should maintain condition differently
    initial_condition = test_book.condition
    test_economy.process_season("Spring", 1220)

    # Books should deteriorate more slowly
    assert test_book.condition > initial_condition - 5


def test_personnel_loyalty(test_economy, test_personnel):
    """Test personnel loyalty mechanics."""
    test_economy.add_resource(test_personnel)

    # Test loyalty effects when unable to pay salary
    test_economy.treasury = 0.0  # Can't pay salary
    test_economy.process_season("Spring", 1220)

    assert test_personnel.loyalty < 75  # Should decrease


def test_seasonal_effects(test_economy, test_mundane_resource):
    """Test seasonal effects on resources and activities."""
    test_economy.add_resource(test_mundane_resource)

    # Winter should be harder on resources
    winter_results = test_economy.process_season("Winter", 1220)
    test_mundane_resource.condition = 100  # Reset condition

    # Spring should be easier on resources
    spring_results = test_economy.process_season("Spring", 1220)

    # Compare deterioration rates
    winter_deterioration = winter_results["resources"][0]["deterioration"]
    spring_deterioration = spring_results["resources"][0]["deterioration"]

    assert winter_deterioration > spring_deterioration
