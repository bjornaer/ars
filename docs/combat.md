# Combat System

## Overview
The Ars Magica combat system manages weapon-based combat, including initiative, attacks, defenses, and damage calculation. The system supports both simple and stress dice rolls.

## Command Reference

### Initialize Combat Round 

```bash
ars combat init-round
```

Interactive command that will prompt for:
- Participant names
- Weapon selections
- Calculate initiative order


### Process Attack

```bash
ars combat attack <attacker_name> <defender_name> [options]
```

Options:
- -w, --weapon WEAPON_NAME: Specify weapon for attacker (text)
- --stress/--no-stress: Use stress die (default: stress)
- -m, --modifiers MODIFIERS: Additional modifiers (integer)

Example:
```bash
ars combat attack "MagusName" "OpponentName" -w "WeaponName" -m 2 --stress
```


### Add Weapon

```bash
ars combat add-weapon <character_name> <weapon_name> [options]
```

Options:
- -t, --type WEAPON_TYPE: Specify weapon type (text)
- -i, --init INT Initiative modifier
- -a, --attack INT Attack modifier
- -d, --defense INT Defense modifier
- -m, --damage INT Damage modifier
- -r, --range TEXT Weapon range
- -s, --strength-req INT Strength requirement

Example:
```bash
ars combat add-weapon "MagusName" "WeaponName" -t "Blade" -i 2 -a 3 -d 1 -m 2 -r "Melee" -s 10
```


## Combat Mechanics

### Initiative Calculation

> Initiative = Quickness + Weapon Initiative Modifier  + Simple Die Roll


### Attack Resolution

> Attack Total = Weapon Skill + Weapon Attack Modifier + Modifiers + Die Roll
> Defense Total = Defense Skill + Weapon Defense Modifier + Modifiers + Die Roll

### Damage Calculation

> Base Damage = Strength + Weapon Damage Modifier
> Attack Advantage = (Attack Total - Defense Total) ÷ 5
> Final Damage = Base Damage + Attack Advantage - Soak


## Weapon Types

### Single Weapons
- Standard one-handed weapons
- Balanced initiative/attack/defense
- Examples: Sword, Mace, Axe

### Great Weapons
- Two-handed weapons
- Higher damage, lower defense
- Examples: Great Sword, Battle Axe, Pole Arm

### Missile Weapons
- Ranged weapons
- Range-based modifiers
- Examples: Bow, Crossbow, Thrown Weapon

## Combat Round Structure

1. **Initiative Phase**
   - Each participant rolls initiative
   - Order determined high to low

2. **Action Phase**
   - Each participant acts in initiative order
   - Standard actions:
     - Attack
     - Defend
     - Move
     - Ready weapon

3. **Resolution Phase**
   - Resolve all attacks
   - Apply damage
   - Update character states

## Combat Modifiers

### Situational Modifiers
- Higher ground: +3
- Flanking: +2
- Poor footing: -3
- Darkness: -3
- Fatigue: -1 per level

### Range Modifiers (Missile Weapons)
- Point blank: +3
- Short range: +0
- Medium range: -3
- Long range: -6

### Weapon Quality
- Superior: +1
- Fine: +2
- Exceptional: +3
- Poor: -1
- Inferior: -2

## Combat Results

### Success Levels
- Marginal: 1-5 points over defense
- Clear: 6-10 points over defense
- Superior: 11+ points over defense

### Botch Results
On a botch (stress die roll of 0):
- Weapon dropped
- Loss of balance
- Exposed position
- Weapon damage