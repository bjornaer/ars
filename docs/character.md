# Character Management Guide

## Character Creation

### Interactive Wizard

The easiest way to create a character is using the interactive wizard:
<<<
ars character wizard
>>>

This will guide you through the character creation process step by step, including:
- Basic information
- Characteristics
- Virtues and Flaws
- Magical Arts
- Abilities
- Final details

### Basic Creation

Create a basic magus:
<<<
ars character create "Bonisagus Wizard" \
    --house Bonisagus \
    --player "Your Name" \
    --age 25 \
    --gender male \
    --nationality "Norman" \
    --size 0
>>>

### Characteristics

Set characteristics:
<<<
ars character characteristics "Bonisagus Wizard" \
    --intelligence 3 \
    --perception 2 \
    --strength 0 \
    --stamina 1 \
    --presence 0 \
    --communication 2 \
    --dexterity 1 \
    --quickness -1
>>>

### Arts

Set magical arts:
<<<
ars character arts "Bonisagus Wizard" \
    --creo 10 \
    --intellego 5 \
    --muto 3 \
    --perdo 4 \
    --rego 8 \
    --animal 2 \
    --aquam 3 \
    --auram 4 \
    --corpus 6 \
    --herbam 2 \
    --ignem 8 \
    --imaginem 3 \
    --mentem 5 \
    --terram 4 \
    --vim 7
>>>

## Character Development

### Abilities

Add or improve abilities:
<<<
ars character abilities "Bonisagus Wizard" \
    --add "Magic Theory" 4 \
    --add "Parma Magica" 2 \
    --add "Latin" 4 \
    --add "Concentration" 2 \
    --add "Finesse" 2
>>>

### Virtues and Flaws

Add virtues and flaws:
<<<
ars character virtues "Bonisagus Wizard" \
    --add "The Gift" \
    --add "Hermetic Magus" \
    --add "Skilled Parens" \
    --add "Good Teacher"

ars character flaws "Bonisagus Wizard" \
    --add "Driven" \
    --add "Study Requirement" \
    --add "Weak Magic Resistance"
>>>

## Advanced Features

### Familiar Binding

Bind a familiar:
<<<
ars character familiar "Bonisagus Wizard" \
    --bind "Shadow Cat" \
    --might 10 \
    --bond-strength 3 \
    --magical true
>>>

### Laboratory Setup

Initialize laboratory:
<<<
ars character laboratory "Bonisagus Wizard" \
    --setup new \
    --size 0 \
    --specialization "Experimentation"
>>>

### Spell Mastery

Add mastered spells:
<<<
ars character spells "Bonisagus Wizard" \
    --master "Pilum of Fire" \
    --specializations "Fast Cast,Penetration" \
    --mastery-score 2
>>>

## Character Management

### Experience

Add experience points:
<<<
ars character experience "Bonisagus Wizard" \
    --add-xp "Magic Theory" 5 \
    --add-xp "Creo" 15 \
    --add-xp "Ignem" 10
>>>

### Aging

Process aging:
<<<
ars character age "Bonisagus Wizard" \
    --year 1220 \
    --longevity-ritual-bonus 6
>>>

### Equipment

Manage equipment:
<<<
ars character equipment "Bonisagus Wizard" \
    --add "Spellbook" \
    --add "Magic Staff" \
    --add "Laboratory Texts"
>>> 