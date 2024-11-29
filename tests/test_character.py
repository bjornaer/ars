import pytest
from pathlib import Path
import yaml

from ars.core.character import Character, CharacterError, InvalidCharacterDataError
from ars.core.types import (
    AbilityType, ArmorType, Characteristic, FatigueLevel, WeaponType
)


@pytest.fixture
def basic_character():
    """Create a basic character for testing."""
    return Character(
        name="Test Character",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant"
    )


@pytest.fixture
def temp_character_dir(tmp_path):
    """Create a temporary directory for character files."""
    char_dir = tmp_path / "characters"
    char_dir.mkdir()
    return char_dir


class TestCharacterBasics:
    """Test basic character functionality."""

    def test_character_creation(self, basic_character):
        """Test basic character creation."""
        assert basic_character.name == "Test Character"
        assert basic_character.player == "Test Player"
        assert basic_character.age == 25  # default value
        assert basic_character.fatigue_level == FatigueLevel.FRESH

    def test_default_characteristics(self, basic_character):
        """Test that characteristics are properly initialized."""
        for char in Characteristic:
            assert basic_character.characteristics[char] == 0

    def test_characteristic_bonus(self, basic_character):
        """Test characteristic bonus calculation."""
        basic_character.characteristics[Characteristic.STRENGTH] = 3
        assert basic_character.get_characteristic_bonus(Characteristic.STRENGTH) == 3


class TestAbilities:
    """Test ability management."""

    def test_add_valid_ability(self, basic_character):
        """Test adding a valid ability."""
        basic_character.add_ability(AbilityType.MARTIAL, "Athletics", 2)
        assert basic_character.get_ability_score(AbilityType.MARTIAL, "Athletics") == 2

    def test_add_invalid_ability(self, basic_character):
        """Test adding an invalid ability."""
        with pytest.raises(InvalidCharacterDataError):
            basic_character.add_ability(AbilityType.MARTIAL, "InvalidAbility", 2)

    def test_get_nonexistent_ability(self, basic_character):
        """Test getting score of nonexistent ability."""
        assert basic_character.get_ability_score(AbilityType.ACADEMIC, "Philosophy") == 0


class TestPersonalityAndReputation:
    """Test personality traits and reputation."""

    def test_add_valid_personality_trait(self, basic_character):
        """Test adding a valid personality trait."""
        basic_character.add_personality_trait("Brave", 2)
        assert basic_character.personality_traits["Brave"] == 2

    def test_add_invalid_personality_trait(self, basic_character):
        """Test adding an invalid personality trait value."""
        with pytest.raises(InvalidCharacterDataError):
            basic_character.add_personality_trait("Brave", 4)

    def test_add_valid_reputation(self, basic_character):
        """Test adding a valid reputation."""
        basic_character.add_reputation("Wise Magus", 3)
        assert basic_character.reputation["Wise Magus"] == 3

    def test_add_invalid_reputation(self, basic_character):
        """Test adding an invalid reputation value."""
        with pytest.raises(InvalidCharacterDataError):
            basic_character.add_reputation("Wise Magus", 6)


class TestEquipment:
    """Test equipment management."""

    def test_equip_weapon(self, basic_character):
        """Test equipping a weapon."""
        basic_character.equip_weapon(WeaponType.SWORD, attack_mod=3, damage_mod=0)
        assert basic_character.weapons[WeaponType.SWORD] == {
            'type': WeaponType.SWORD,
            'attack_mod': 3,
            'damage_mod': 0
        }

    def test_equip_invalid_weapon_skill(self, basic_character):
        """Test equipping a weapon with invalid skill."""
        with pytest.raises(InvalidCharacterDataError):
            basic_character.equip_weapon(WeaponType.SWORD, attack_mod=6, damage_mod=0)

    def test_equip_armor(self, basic_character):
        """Test equipping armor."""
        basic_character.equip_armor(ArmorType.CHAIN)
        assert basic_character.armor == ArmorType.CHAIN


class TestCombatCalculations:
    """Test combat-related calculations."""

    def test_combat_bonus(self, basic_character):
        """Test combat bonus calculation."""
        basic_character.characteristics[Characteristic.DEXTERITY] = 2
        basic_character.characteristics[Characteristic.STRENGTH] = 1
        basic_character.equip_weapon(WeaponType.SWORD, attack_mod=3, damage_mod=0)
        
        # Expected: weapon(3) + dex(2) + str(1) + fatigue(0) = 6
        assert basic_character.get_combat_bonus(WeaponType.SWORD) == 6

    def test_soak_bonus(self, basic_character):
        """Test soak bonus calculation."""
        basic_character.characteristics[Characteristic.STAMINA] = 2
        basic_character.equip_armor(ArmorType.CHAIN)
        
        # Expected: stamina(2) + chain_armor_protection
        armor_protection = ArmorType.get_stats(ArmorType.CHAIN)["protection"]
        assert basic_character.get_soak_bonus() == 2 + armor_protection


class TestFatigue:
    """Test fatigue management."""

    def test_fatigue_modification(self, basic_character):
        """Test modifying fatigue levels."""
        basic_character.modify_fatigue(2)
        assert basic_character.fatigue_level == FatigueLevel.WEARY

    def test_fatigue_limits(self, basic_character):
        """Test fatigue level limits."""
        # Test upper limit
        basic_character.modify_fatigue(10)
        assert basic_character.fatigue_level == FatigueLevel.UNCONSCIOUS
        
        # Test lower limit
        basic_character.modify_fatigue(-10)
        assert basic_character.fatigue_level == FatigueLevel.FRESH


class TestSerialization:
    """Test character serialization."""

    def test_to_dict(self, basic_character):
        """Test converting character to dictionary."""
        basic_character.add_ability(AbilityType.MARTIAL, "Athletics", 2)
        basic_character.equip_weapon(WeaponType.SWORD, attack_mod=3, damage_mod=0)
        
        data = basic_character.to_dict()
        assert data["name"] == "Test Character"
        assert data["abilities"][AbilityType.MARTIAL.value]["Athletics"] == 2
        assert data["weapons"][WeaponType.SWORD.value] == {
            'type': WeaponType.SWORD,
            'attack_mod': 3,
            'damage_mod': 0
        }

    def test_from_dict(self):
        """Test creating character from dictionary."""
        data = {
            "name": "Test Character",
            "player": "Test Player",
            "saga": "Test Saga",
            "covenant": "Test Covenant",
            "characteristics": {
                "Strength": 2,
                "Dexterity": 1
            }
        }
        
        character = Character.from_dict(data)
        assert character.name == "Test Character"
        assert character.characteristics[Characteristic.STRENGTH] == 2


class TestFileOperations:
    """Test character file operations."""

    def test_save_and_load(self, basic_character, temp_character_dir):
        """Test saving and loading character."""
        # Add some data
        basic_character.add_ability(AbilityType.MARTIAL, "Athletics", 2)
        basic_character.equip_weapon(WeaponType.SWORD, attack_mod=3, damage_mod=0)
        
        # Save
        basic_character.save(temp_character_dir)
        
        # Load
        loaded = Character.load(basic_character.name, temp_character_dir)
        
        # Verify
        assert loaded.name == basic_character.name
        assert loaded.get_ability_score(AbilityType.MARTIAL, "Athletics") == 2
        assert loaded.weapons[WeaponType.SWORD] == {
            'type': WeaponType.SWORD,
            'attack_mod': 3,
            'damage_mod': 0
        }

    def test_load_nonexistent_character(self, temp_character_dir):
        """Test loading a nonexistent character."""
        with pytest.raises(CharacterError):
            Character.load("NonexistentCharacter", temp_character_dir)

    def test_save_overwrites_existing(self, basic_character, temp_character_dir):
        """Test that saving overwrites existing character file."""
        # Initial save
        basic_character.add_ability(AbilityType.MARTIAL, "Athletics", 2)
        basic_character.save(temp_character_dir)
        
        # Modify and save again
        basic_character.add_ability(AbilityType.MARTIAL, "Athletics", 3)
        basic_character.save(temp_character_dir)
        
        # Load and verify
        loaded = Character.load(basic_character.name, temp_character_dir)
        assert loaded.get_ability_score(AbilityType.MARTIAL, "Athletics") == 3