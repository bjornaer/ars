# Magic Item Creation Guide

## Basic Item Creation

Create a simple charged item:
<<<
ars enchant create "Ring of Fire" \
    --creator "Bonisagus Wizard" \
    --type charged \
    --material "Silver Ring" \
    --size 0
>>>

Add an effect:
<<<
ars enchant add-effect "Ring of Fire" \
    --name "Flame Burst" \
    --technique Creo \
    --form Ignem \
    --level 15 \
    --uses 5
>>>

## Advanced Enchantment

### Invested Devices

Create an invested device:
<<<
ars enchant create "Staff of Elements" \
    --creator "Bonisagus Wizard" \
    --type invested \
    --material "Heartwood Staff" \
    --size 3 \
    --shape-bonus 3 \
    --material-bonus 2
>>>

Add multiple effects:
<<<
ars enchant add-effect "Staff of Elements" \
    --name "Flame Strike" \
    --technique Creo \
    --form Ignem \
    --level 20 \
    --trigger "When commanded" \
    --penetration 10

ars enchant add-effect "Staff of Elements" \
    --name "Water Blast" \
    --technique Creo \
    --form Aquam \
    --level 15 \
    --trigger "When tapped"
>>>

### Talismans

Create a talisman:
<<<
ars enchant create "Magus Staff" \
    --creator "Bonisagus Wizard" \
    --type talisman \
    --material "Oak Staff" \
    --size 3 \
    --attunement-bonus 5
>>>

Add talisman powers:
<<<
ars enchant add-effect "Magus Staff" \
    --name "Power Storage" \
    --technique Creo \
    --form Vim \
    --level 25 \
    --installation-type "Environmental" \
    --trigger "Constant"
>>> 