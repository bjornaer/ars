# Seasonal Activities Guide

## Basic Season Management

### Planning Seasons

Schedule a basic season:
<<<
ars season schedule "Bonisagus Wizard" \
    --activity study \
    --subject "Magic Theory" \
    --season spring \
    --year 1220
>>>

Schedule multiple seasons:
<<<
ars season schedule "Bonisagus Wizard" \
    --activity study --subject "Creo" --season spring --year 1220
    --activity research --season summer --year 1220
    --activity teach --student "Apprentice" --subject "Magic Theory" --season autumn --year 1220
    --activity invent --spell "Ball of Abyssal Flame" --season winter --year 1220
>>>

### Executing Seasons

Process a single season:
<<<
ars season execute "Bonisagus Wizard" \
    --season spring \
    --year 1220
>>>

Process a year:
<<<
ars season execute-year "Bonisagus Wizard" \
    --year 1220 \
    --include-events true
>>>

## Study Activities

### Book Study

Study from books:
<<<
ars season study "Bonisagus Wizard" \
    --source "Summa on Magic Theory" \
    --quality 10 \
    --level 5
>>>

### Vis Study

Study with vis:
<<<
ars season study "Bonisagus Wizard" \
    --source vis \
    --art Creo \
    --pawns 5
>>>

### Teaching and Learning

Teach another character:
<<<
ars season teach "Bonisagus Wizard" \
    --student "Apprentice" \
    --subject "Magic Theory" \
    --communication-roll true
>>>

## Research Activities

### Spell Research

Research new spell:
<<<
ars season research "Bonisagus Wizard" \
    --type spell \
    --name "Enhanced Flame Arrow" \
    --technique Creo \
    --form Ignem \
    --level 20
>>>

### Item Enchantment

Create magic items:
<<<
ars season enchant "Bonisagus Wizard" \
    --item "Ring of Protection" \
    --effect "Grant Magic Resistance" \
    --level 15
>>>

## Adventure and Story

### Story Participation

Participate in story:
<<<
ars season story "Bonisagus Wizard" \
    --story "The Lost Covenant" \
    --role primary \
    --exposure-xp true
>>>

### Service Activities

Perform covenant service:
<<<
ars season service "Bonisagus Wizard" \
    --type "Vis Hunting" \
    --location "Magical Forest" \
    --expected-yield 5
>>>

## Advanced Season Management

### Custom Activities

Define custom activity:
<<<
ars season custom "Bonisagus Wizard" \
    --name "Magical Research Project" \
    --duration 2 \
    --requirements "Magic Theory 4" \
    --results "New Breakthrough" \
    --seasons "spring,summer" \
    --year 1220
>>>

### Interruptions

Handle season interruption:
<<<
ars season interrupt "Bonisagus Wizard" \
    --reason "Emergency Council" \
    --duration "2 weeks" \
    --save-progress true
>>>

### Multiple Characters

Coordinate multiple characters:
<<<
ars season coordinate \
    --characters "Bonisagus Wizard,Flambeau Maga" \
    --activity "Joint Research" \
    --season summer \
    --year 1220
>>> 