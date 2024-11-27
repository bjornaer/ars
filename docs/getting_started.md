# Getting Started

## Basic Setup

1. Install the package:
<<<
poetry add ars-magica
>>>

2. Initialize a new saga:
<<<
ars saga init "My First Saga"
>>>

## First Steps

### Creating Characters

Create a basic magus:
<<<
ars character create "Bonisagus Wizard" \
    --house Bonisagus \
    --player "Your Name" \
    --age 25 \
    --magic-theory 4
>>>

Add characteristics:
<<<
ars character edit "Bonisagus Wizard" \
    --intelligence 3 \
    --stamina 2 \
    --communication 1
>>>

### Setting Up a Covenant

Create a basic covenant:
<<<
ars covenant create "Valley Covenant" \
    --size small \
    --aura 3 \
    --season spring \
    --year 1220
>>>

Add resources:
<<<
ars covenant edit "Valley Covenant" \
    --add-resource "Vis Source" \
    --type "Raw Vis" \
    --form "Creo" \
    --amount 5
>>>

### Basic Laboratory Setup

Create a laboratory:
<<<
ars lab setup "Bonisagus Wizard" \
    --size 0 \
    --refinement 1 \
    --safety 1
>>>

Add specializations:
<<<
ars lab modify "Bonisagus Wizard" \
    --add-specialization "Experimentation" 2
>>>

## Next Steps

- Learn about [seasonal activities](seasons.md)
- Explore the [magic system](magic/README.md)
- Set up [advanced covenant features](covenant.md) 