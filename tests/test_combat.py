import pytest
from ars.core.combat import CombatManager, CombatRound, CombatAction, CombatResult
from ars.core.characters.grog import Grog
from ars.core.types import WeaponType, ArmorType, Characteristic


@pytest.fixture
def basic_grog():
    """Create a basic grog for testing."""
    grog = Grog(
        name="Test Grog",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        characteristics={
            Characteristic.STRENGTH: 0,
            Characteristic.STAMINA: 0,
            Characteristic.DEXTERITY: 0,
            Characteristic.QUICKNESS: 0,
        }
    )
    grog.weapons = {}  # Initialize weapons dict
    grog.armor = {}    # Initialize armor dict
    return grog

@pytest.fixture
def not_basic_grog():
    """Create a not-so-basic grog for testing."""
    grog = Grog(
        name="Test Grog",
        player="Test Player",
        saga="Test Saga",
        covenant="Test Covenant",
        characteristics={
            Characteristic.STRENGTH: 1,
            Characteristic.STAMINA: 1,
            Characteristic.DEXTERITY: 0,
            Characteristic.QUICKNESS: 0,
        }
    )
    grog.weapons = {}  # Initialize weapons dict
    grog.armor = {}    # Initialize armor dict
    return grog


def test_combat_round(basic_grog, not_basic_grog, monkeypatch):
    """Test combat round management."""
    round = CombatRound()
    
    # Create combatants with weapons
    attacker = basic_grog
    attacker.name = "Attacker"
    attacker.weapon_skills = {'Sword': 3}
    
    defender = not_basic_grog
    defender.name = "Defender"
    defender.weapon_skills = {'Brawling': 1}
    
    # Add weapons to both characters
    attacker.weapons['Long Sword'] = {
        'type': WeaponType.SWORD,
        'init_mod': 1,
        'attack_mod': 2,
        'defense_mod': 1,
        'damage_mod': 3
    }
    
    defender.weapons['Fist'] = {
        'type': WeaponType.BRAWLING,
        'init_mod': 0,
        'attack_mod': 0,
        'defense_mod': 0,
        'damage_mod': 0
    }
    
    # Test initiative order
    with monkeypatch.context() as m:
        m.setattr('random.randint', lambda x, y: 5)
        round.add_combatant(attacker, "Long Sword")
        round.add_combatant(defender, "Fist")
        
        order = round.get_initiative_order()
        assert len(order) == 2
        assert order[0][0] == "Attacker"  # Higher initiative due to weapon mod


def test_combat_state_tracking(basic_grog, not_basic_grog):
    """Test combat state tracking."""
    round = CombatRound()
    
    char1 = not_basic_grog
    char1.name = "Fighter 1"
    char1.weapon_skills = {'Sword': 2}
    
    char2 = basic_grog
    char2.name = "Fighter 2"
    char2.weapon_skills = {'Dagger': 2}
    
    # Add weapons to both characters
    char1.weapons['Sword'] = {
        'type': WeaponType.SWORD,
        'init_mod': 0,
        'attack_mod': 2,
        'defense_mod': 1,
        'damage_mod': 3
    }
    
    char2.weapons['Dagger'] = {
        'type': WeaponType.DAGGER,
        'init_mod': 2,
        'attack_mod': 1,
        'defense_mod': 1,
        'damage_mod': 1
    }
    
    round.add_combatant(char1, "Sword")
    round.add_combatant(char2, "Dagger")

    # Test initiative order, Daggers have higher initiative due to weapon mod

    order = round.get_initiative_order()
    assert len(order) == 2
    assert order[0][0] == "Fighter 2"  # Higher initiative due to weapon mod
    
    # Test turn progression
    current, state = round.get_current_combatant()
    assert current == "Fighter 2"
    assert state.actions_remaining == 1
    
    # Test next turn
    round.next_turn()
    current, state = round.get_current_combatant()
    assert current == "Fighter 1"
    
    # Test round completion
    round.next_turn()
    assert round.round_number == 2
    assert round.current_turn == 0


def test_combat_resolution(basic_grog, not_basic_grog):
    """Test combat resolution mechanics."""
    # Setup combatants
    attacker = not_basic_grog
    attacker.name = "Attacker"
    attacker.weapon_skills = {'Sword': 3}
    attacker.characteristics[Characteristic.STRENGTH] = 2
    
    # Add and equip weapon
    attacker.weapons['Long Sword'] = {
        'type': WeaponType.SWORD,
        'attack_mod': 2,
        'damage_mod': 3
    }
    attacker.equipped_weapon = 'Long Sword'  # Set equipped weapon
    
    defender = basic_grog
    defender.name = "Defender"
    defender.characteristics[Characteristic.STAMINA] = 1
    defender.armor['Chain Mail'] = {
        'type': ArmorType.CHAIN,
        'protection': 3,
        'modifiers': 1
    }
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr('random.randint', lambda x, y: 5)
        result = CombatManager.resolve_attack(
            attacker=attacker,
            defender=defender
        )
        
        assert result.is_hit
        assert result.attack_total == 10
        assert result.defense_total == 6


def test_special_actions(basic_grog, not_basic_grog):
    """Test special combat actions."""
    actor = not_basic_grog
    actor.name = "Actor"
    actor.abilities = {'Guile': 2}
    
    
    target = basic_grog
    target.name = "Target"
    target.abilities = {'Awareness': 1}
    
    # Test feint
    with pytest.MonkeyPatch().context() as m:
        m.setattr('random.randint', lambda x, y: 5)
        result = CombatManager.resolve_special_action(
            action=CombatAction.FEINT,
            actor=actor,
            target=target,
        )
        
        assert result.is_hit  # Feint succeeds
        assert result.modifiers_applied['feint_penalty'] == -3 