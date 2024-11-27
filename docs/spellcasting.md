# Spell Casting System

## Overview
The Ars Magica spell casting system allows magi to cast spells using their Arts (Techniques and Forms). The system handles spontaneous and formulaic magic, with support for stress dice and botch mechanics.

## Command Reference

### Cast a Spell 
```bash
ars spell cast <character_name> <spell_name> [options]
Options:
-a, --aura INTEGER Magical aura modifier
--stress/--no-stress Use stress die (default: stress)
-m, --modifiers INTEGER Additional modifiers
```

Example:
```bash
ars spell cast "MagusName" "SpellName" --aura 1 --stress --modifiers 2
```

### Create New Spell

```bash
ars spell create <character_name> <template_name> <specific_name> [options]
Options:
-r, --range TEXT Spell range [Personal/Touch/Voice/Sight/Arcane Connection]
-d, --duration TEXT Duration [Momentary/Concentration/Diameter/Sun/Moon/Year]
-t, --target TEXT Target type [Individual/Group/Room/Structure/Boundary]
```

Example:
```bash
ars spell create "MagusName" "fire_bolt" "Fire Bolt" --range "Sight" --duration "Momentary" --target "Individual"
```

### List Character's Spells
```bash
ars spell list <character_name>
```


## Spell Parameters

### Ranges
- Personal: Affects only the caster
- Touch: Must touch the target
- Voice: Target must be able to hear the caster
- Sight: Target must be visible to caster
- Arcane Connection: Requires an arcane connection

### Durations
- Momentary: Instant effect
- Concentration: Lasts while concentrating
- Diameter: About 2 minutes
- Sun: Until next sunrise/sunset
- Moon: Until next full moon
- Year: One year

### Targets
- Individual: Single target
- Group: Small group of related targets
- Room: Room-sized area
- Structure: Building-sized area
- Boundary: Defines a magical boundary

## Spell Templates
Pre-defined templates for common spells:

### Ball of Fire Template

```python
{
"name_pattern": "Ball of {element} Fire",
"technique": "Creo",
"form": "Ignem",
"base_level": 10,
"effects": ["Create fire"],
"modifiers": {"size": 2, "heat": 3}
}
```


### Shield of Protection Template

```python
{
"name_pattern": "Shield of {element} Protection",
"technique": "Rego",
"form": "Vim",
"base_level": 15,
"effects": ["Magical shield"],
"modifiers": {"duration": 2}
}
```


## Casting Mechanics

### Casting Total

> Casting Total = Technique + Form + Mastery + Aura + Modifiers + Die Roll


### Success Determination
- Success if Casting Total ≥ Spell Level
- Botch possible on stress die roll of 0
- Critical success on multiplication of stress die

### Modifiers
- Aura: Local magical aura
- Mastery: Spell mastery level
- Circumstances: Environmental and situational modifiers