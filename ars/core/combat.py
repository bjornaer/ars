from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum

from ars.core.character import Character
from ars.core.dice import DiceRoller, DiceResult
from ars.core.types import WeaponType, ArmorType


class CombatAction(Enum):
    """Available combat actions."""
    ATTACK = "attack"
    DEFEND = "defend"
    DODGE = "dodge"
    FEINT = "feint"
    CHARGE = "charge"
    RETREAT = "retreat"
    GRAPPLE = "grapple"
    AIM = "aim"


@dataclass
class CombatResult:
    """Results of a combat action."""
    # Roll results
    attack_roll: DiceResult
    defense_roll: DiceResult
    attack_total: int
    defense_total: int
    damage_roll: Optional[DiceResult] = None
    damage_total: Optional[int] = None
    
    # Status flags
    is_hit: bool = False
    is_botch: bool = False
    is_critical: bool = False
    
    # Additional information
    botch_details: Optional[str] = None
    critical_details: Optional[str] = None
    modifiers_applied: Dict[str, int] = None
    
    def __post_init__(self):
        if self.modifiers_applied is None:
            self.modifiers_applied = {}


@dataclass
class CombatantState:
    """Tracks a combatant's state during combat."""
    character: 'Character'
    current_weapon: str
    initiative: int
    actions_remaining: int = 1
    is_prone: bool = False
    is_stunned: bool = False
    fatigue_level: int = 0
    temporary_modifiers: Dict[str, int] = None
    
    def __post_init__(self):
        if self.temporary_modifiers is None:
            self.temporary_modifiers = {}

    def can_act(self) -> bool:
        """Check if combatant can still act this round."""
        return (
            self.actions_remaining > 0 
            and not self.is_stunned
            and self.fatigue_level < 5
        )

    def apply_modifier(self, name: str, value: int, duration: int = 1):
        """Apply a temporary combat modifier."""
        self.temporary_modifiers[name] = {
            "value": value,
            "duration": duration
        }

    def clear_expired_modifiers(self):
        """Clear expired temporary modifiers."""
        expired = []
        for name, mod in self.temporary_modifiers.items():
            mod["duration"] -= 1
            if mod["duration"] <= 0:
                expired.append(name)
                
        for name in expired:
            del self.temporary_modifiers[name]


class CombatRound:
    """Manages a round of combat."""
    
    def __init__(self):
        self.combatants: Dict[str, CombatantState] = {}
        self.initiative_order: List[str] = []
        self.current_turn: int = 0
        self.round_number: int = 1

    def add_combatant(
        self,
        character: 'Character',
        weapon: str,
        initiative_modifier: int = 0
    ) -> None:
        """Add a combatant to the combat round."""
        # Roll initiative
        init_roll = DiceRoller.simple_die()
        weapon_obj = character.weapons.get(weapon)
        if not weapon_obj:
            raise ValueError(f"Weapon '{weapon}' not found for {character.name}")
            
        init_total = (
            init_roll.total +
            character.characteristics.get('Quickness', 0) +
            weapon_obj.get('init_mod', 0) +
            initiative_modifier
        )
        
        # Create combatant state
        state = CombatantState(
            character=character,
            current_weapon=weapon,
            initiative=init_total
        )
        
        self.combatants[character.name] = state
        self._update_initiative_order()

    def _update_initiative_order(self):
        """Update the initiative order based on current combatants."""
        self.initiative_order = sorted(
            self.combatants.keys(),
            key=lambda x: self.combatants[x].initiative,
            reverse=True
        )

    def get_current_combatant(self) -> Optional[Tuple[str, CombatantState]]:
        """Get the current active combatant."""
        if not self.initiative_order:
            return None
            
        current = self.initiative_order[self.current_turn]
        return current, self.combatants[current]

    def next_turn(self) -> bool:
        """Advance to the next turn. Returns False if round is complete."""
        self.current_turn += 1
        
        if self.current_turn >= len(self.initiative_order):
            return self._start_new_round()
            
        return True

    def _start_new_round(self) -> bool:
        """Start a new combat round."""
        self.round_number += 1
        self.current_turn = 0
        
        # Reset combatant states
        for state in self.combatants.values():
            state.actions_remaining = 1
            state.clear_expired_modifiers()
            
        return True

    def get_initiative_order(self) -> List[Tuple[str, str, int]]:
        """Get the current initiative order as (name, weapon, initiative) tuples."""
        return [
            (
                name,
                self.combatants[name].current_weapon,
                self.combatants[name].initiative
            )
            for name in self.initiative_order
        ]


class CombatManager:
    """Manages combat mechanics and resolution."""
    
    @staticmethod
    def resolve_attack(
        attacker: 'Character',
        defender: 'Character',
        stress: bool = True,
        modifiers: Dict[str, int] | None = None
    ) -> CombatResult:
        """Resolve an attack between two characters."""
        if modifiers is None:
            modifiers = {}
            
        # Attack roll
        attack_roll = DiceRoller.stress_die() if stress else DiceRoller.simple_die()
        weapon = attacker.weapons.get(attacker.equipped_weapon or WeaponType.BRAWLING)
        
        # Calculate attack total
        attack_total = (
            attack_roll.total +
            attacker.get_combat_bonus(weapon['type']) +
            sum(modifiers.values())
        )
        
        # Defense roll
        defense_roll = DiceRoller.stress_die() if stress else DiceRoller.simple_die()
        def_weapon = defender.weapons.get(defender.equipped_weapon or WeaponType.BRAWLING)
        # Calculate defense total
        defense_total = (
            defense_roll.total +
            defender.get_defense_bonus(def_weapon['type'])
        )
        
        # Add armor defense if present
        if hasattr(defender, 'armor') and defender.armor:
            armor = next(iter(defender.armor.values()))  # Get first armor
            defense_total += armor.get('modifiers', 0)
        
        # Determine hit
        is_hit = attack_total > defense_total
        
        # Handle damage if hit
        damage_roll = None
        damage_total = None
        if is_hit:
            damage_roll = DiceRoller.stress_die()
            base_damage = (
                damage_roll.total +
                attacker.characteristics.get('Strength', 0) +
                weapon.get('damage_mod', 0)
            )
            
            # Calculate soak
            soak = defender.get_soak_bonus()
                
            damage_total = max(0, base_damage - soak)
        
        return CombatResult(
            attack_roll=attack_roll,
            defense_roll=defense_roll,
            damage_roll=damage_roll,
            attack_total=attack_total,
            defense_total=defense_total,
            damage_total=damage_total,
            is_hit=is_hit,
            is_botch=attack_roll.is_botch or defense_roll.is_botch,
            modifiers_applied=modifiers
        )

    @staticmethod
    def resolve_special_action(
        action: CombatAction,
        actor: 'Character',
        target: 'Character',
        stress: bool = True,
        modifiers: Dict[str, int] | None = None
    ) -> CombatResult:
        """Resolve special combat actions."""
        if modifiers is None:
            modifiers = {}
            
        if action == CombatAction.FEINT:
            # Feint uses Guile vs Awareness
            attack_roll = DiceRoller.stress_die() if stress else DiceRoller.simple_die()
            attack_total = (
                attack_roll.total +
                actor.abilities.get('Guile', 0) +
                sum(modifiers.values())
            )
            
            defense_roll = DiceRoller.stress_die() if stress else DiceRoller.simple_die()
            defense_total = (
                defense_roll.total +
                target.abilities.get('Awareness', 0)
            )
            
            success = attack_total > defense_total
            if success:
                # Apply penalty to next defense
                modifiers['feint_penalty'] = -3
                
        elif action == CombatAction.CHARGE:
            # Charge adds damage but reduces defense
            modifiers['charge_attack'] = 2
            modifiers['charge_defense'] = -1
            return CombatManager.resolve_attack(
                actor, target, stress, modifiers
            )
            
        # Add more special actions as needed
        
        return CombatResult(
            attack_roll=attack_roll,
            defense_roll=defense_roll,
            attack_total=attack_total,
            defense_total=defense_total,
            is_hit=success,
            modifiers_applied=modifiers
        )

    @staticmethod
    def calculate_initiative(
        quickness: int,
        weapon: dict,
        modifiers: Dict[str, int] = None
    ) -> DiceResult:
        """Calculate initiative for a combatant."""
        if modifiers is None:
            modifiers = {}
            
        roll = DiceRoller.simple_die()
        total = (
            roll.total +
            quickness +
            weapon.get('init_mod', 0) +
            sum(modifiers.values())
        )
        
        roll.total = total
        return roll 