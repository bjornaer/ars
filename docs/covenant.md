# Covenant Management Guide

## Covenant Creation

### Basic Setup

Create a new covenant:
<<<
ars covenant create "Valley Covenant" \
    --size small \
    --aura 3 \
    --season spring \
    --year 1220
>>>

### Advanced Setup

Create a detailed covenant:
<<<
ars covenant create "Mountain Sanctuary" \
    --size large \
    --aura 4 \
    --season summer \
    --year 1220 \
    --location "Alpine Peaks" \
    --resources high \
    --defenses strong \
    --reputation 3
>>>

## Resource Management

### Basic Resources

Add basic resources:
<<<
ars covenant resources "Mountain Sanctuary" \
    --add-income "Local Taxes" 10 \
    --add-income "Magical Services" 15 \
    --add-expense "Maintenance" 8
>>>

### Vis Sources

Add vis sources:
<<<
ars covenant vis "Mountain Sanctuary" \
    --add-source "Crystal Cave" \
    --form Creo \
    --amount 5 \
    --season summer

ars covenant vis "Mountain Sanctuary" \
    --add-source "Ancient Grove" \
    --form Herbam \
    --amount 3 \
    --season spring
>>>

## Covenant Development

### Building Projects

Start construction:
<<<
ars covenant build "Mountain Sanctuary" \
    --project "New Tower" \
    --cost 50 \
    --seasons 4 \
    --workers 10
>>>

Add improvements:
<<<
ars covenant improve "Mountain Sanctuary" \
    --aspect defenses \
    --investment 20 \
    --duration 2
>>>

### Staff Management

Add covenant staff:
<<<
ars covenant staff "Mountain Sanctuary" \
    --add-member "Master Scribe" \
    --role specialist \
    --ability "Profession: Scribe" 6

ars covenant staff "Mountain Sanctuary" \
    --add-member "Guard Captain" \
    --role specialist \
    --ability "Leadership" 5 \
    --ability "Weapon Skill" 6
>>>

## Seasonal Activities

### Basic Activities

Process season:
<<<
ars covenant process "Mountain Sanctuary" \
    --season summer \
    --year 1220 \
    --collect-vis true \
    --maintain-buildings true
>>>

### Special Events

Handle covenant events:
<<<
ars covenant event "Mountain Sanctuary" \
    --type "Magical Surge" \
    --severity 3 \
    --duration 1
>>>

## Political Relations

### Tribunal Relations

Manage tribunal standing:
<<<
ars covenant politics "Mountain Sanctuary" \
    --tribunal "Greater Alps" \
    --improve-relations \
    --spend-resources 5
>>>

### Local Relations

Manage local relations:
<<<
ars covenant relations "Mountain Sanctuary" \
    --target "Local Nobility" \
    --action improve \
    --spend-resources 3 \
    --diplomatic-bonus 2
>>> 