# Ars Magica Python Implementation

A Python implementation of the Ars Magica 5th Edition mechanics. This project provides a framework for managing Ars Magica sagas, characters, covenants, and magical activities.

> Note: This is a fan-made implementation of the game mechanics and is not affiliated with or endorsed by Atlas Games. Ars Magica is a trademark of Trident, Inc. d/b/a Atlas Games.

## Features

- Character creation and management
- Covenant management
- Laboratory activities
- Spell research system
- Seasonal activities
- Vis and aura management
- Magic item creation
- Command-line interface for all features

## Installation

You can install the package from PyPI:

```bash
pip install ars-magica
```

## Usage

To use the CLI, run `ars` in your terminal. You can see the available commands by running `ars --help`.

### Quick Start

To get started quickly, you can use the following commands:

1. Create a character:

```bash
ars character create "Bonisagus Wizardus" --house Bonisagus --player "Your Name"

``` 

2. Create a covenant:

```bash
ars covenant create "The Order of Hermes" --size small --aura 1
```

3. Start a seasonal activity:

```bash
ars season schedule "Bonisagus Wizardus" --activity research --subject "Arcane Lore"
```

For more detailed usage and examples, see the [CLI Usage](docs/cli.md) documentation.

## Development

Clone the repository:

```bash
git clone https://github.com/bjornaer/ars.git
```

Install poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Install the dependencies:

```bash
poetry install
```

### Running tests

```bash
poetry run pytest
```

Use the makefile for ease of use:

```bash
make test
```

## Project Structure

TBD

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Note about Ars Magica:
Ars Magica is a trademark of Trident, Inc. d/b/a Atlas Games. This software is not affiliated with or endorsed by Atlas Games. This is a fan-made implementation of the game mechanics and does not include any copyrighted content from the Ars Magica books.

---

_"We are the ancient shapeshifters, guardians of the old ways. Our magic flows from the heart-beast within."_

*- A common saying among House Bjornaer magi*

