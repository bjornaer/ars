# Laboratory Guide

## Laboratory Setup

### Basic Setup

Create a new laboratory:
<<<
ars lab setup "Bonisagus Wizard" \
    --size 0 \
    --refinement 1 \
    --safety 1 \
    --organization 0
>>>

### Advanced Setup

Create a specialized laboratory:
<<<
ars lab setup "Bonisagus Wizard" \
    --size 2 \
    --refinement 3 \
    --safety 2 \
    --organization 2 \
    --upkeep-cost 5 \
    --sanctum-marker true \
    --magical-aura 3
>>>

## Laboratory Customization

### Adding Features

Add basic features:
<<<
ars lab modify "Bonisagus Wizard" \
    --add-feature "Superior Heating" \
    --add-feature "Extensive Storage" \
    --add-feature "Natural Light"
>>>

Add specialized equipment:
<<<
ars lab modify "Bonisagus Wizard" \
    --add-equipment "Precision Tools" \
    --add-equipment "Magical Crystals" \
    --equipment-bonus 3
>>>

### Specializations

Add research specializations:
<<<
ars lab modify "Bonisagus Wizard" \
    --add-specialization "Experimentation" 2 \
    --add-specialization "Enchantment" 3 \
    --add-specialization "Fire Magic" 2
>>>

## Laboratory Activities

### Basic Activities

Maintain laboratory:
<<<
ars lab maintain "Bonisagus Wizard" \
    --season spring \
    --year 1220
>>>

Improve laboratory:
<<<
ars lab improve "Bonisagus Wizard" \
    --aspect refinement \
    --investment 2
>>>

### Advanced Activities

Set up experimental controls:
<<<
ars lab experiment "Bonisagus Wizard" \
    --setup-controls \
    --safety-measures 2 \
    --backup-equipment true
>>>

## Integration Features

### Familiar Integration

Add familiar to laboratory:
<<<
ars lab modify "Bonisagus Wizard" \
    --add-familiar "Shadow Cat" \
    --familiar-bonus 3 \
    --familiar-specialization "Experimentation"
>>>

### Covenant Integration

Link to covenant aura:
<<<
ars lab link-covenant "Bonisagus Wizard" \
    --covenant "Valley Covenant" \
    --aura-bonus true \
    --resource-sharing true
>>> 