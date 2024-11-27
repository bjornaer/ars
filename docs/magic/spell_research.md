# Spell Research Guide

## Basic Research Project

Start a new research project:
<<<
ars spell research start "Bonisagus Wizard" \
    --name "Pilum of Fire" \
    --technique Creo \
    --form Ignem \
    --level 20
>>>

Check progress:
<<<
ars spell research status "Bonisagus Wizard"
>>>

## Advanced Research

### Experimental Research

Start experimental research:
<<<
ars spell research start "Bonisagus Wizard" \
    --name "Enhanced Pilum of Fire" \
    --technique Creo \
    --form Ignem \
    --level 25 \
    --experimental
>>>

### Integration with Laboratory

Use laboratory features:
<<<
ars spell research start "Bonisagus Wizard" \
    --name "Greater Pilum of Fire" \
    --technique Creo \
    --form Ignem \
    --level 30 \
    --use-lab-text \
    --use-familiar \
    --use-aura
>>>

## Research Modifiers

Add research modifiers:
<<<
ars spell research modify "Bonisagus Wizard" \
    --add-bonus "Magical Focus" 3 \
    --add-bonus "Experimentation" 2
>>> 