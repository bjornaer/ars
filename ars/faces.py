from enum import Enum

from .character import Character


class House(Enum):
    BONISAGUS = "Bonisagus"
    FLAMBEAU = "Flambeau"
    TREMERE = "Tremere"
    JERBITON = "Jerbiton"
    MERCERE = "Mercere"
    MERINITA = "Merinita"
    BJORNAER = "Bjornaer"
    CRIAMON = "Criamon"
    TYTALUS = "Tytalus"
    VERDITIUS = "Verditius"
    GUERNICUS = "Guernicus"
    EX_MISCELLANEA = "Ex Miscellanea"


class MagusFace:
    """Collection of ASCII art faces for different magi combinations."""

    # Flambeau + Fire themed faces
    FLAMBEAU_IGNEM = """
    ╭━━━━━━━━━━━╮
    │  🔥 ⚡️ 🔥  │
    │  ┏━━━━━┓  │
    │ ╭┫👁️👁️┣╮ │
    │ ││ 👃 ││ │
    │ ╰┫━👄━┣╯ │
    │  ┗━━━━━┛  │
    │  🔥 ⚡️ 🔥  │
    ╰━━━━━━━━━━━╯
    """

    # Bonisagus + Knowledge themed
    BONISAGUS_INTELLEGO = """
    ╭━━━━━━━━━━━╮
    │  📚 ✨ 📚  │
    │  ┏━━━━━┓  │
    │ ╭┫🔮🔮┣╮ │
    │ ││ 📖 ││ │
    │ ╰┫━💭━┣╯ │
    │  ┗━━━━━┛  │
    │  📚 ✨ 📚  │
    ╰━━━━━━━━━━━╯
    """

    # Merinita + Nature themed
    MERINITA_HERBAM = """
    ╭━━━━━━━━━━━╮
    │  🌿 🍃 🌿  │
    │  ┏━━━━━┓  │
    │ ╭┫🌳🌳┣╮ │
    │ ││ 🌸 ││ │
    │ ╰┫━🍂━┣╯ │
    │  ┗━━━━━┛  │
    │  🌿 🍃 🌿  │
    ╰━━━━━━━━━━━╯
    """

    # Tremere + Control themed
    TREMERE_REGO = """
    ╭━━━━━━━━━━━╮
    │  ⚔️ 🎯 ⚔️  │
    │  ┏━━━━━┓  │
    │ ╭┫👁️👁️┣╮ │
    │ ││ 🎭 ││ │
    │ ╰┫━⚡️━┣╯ │
    │  ┗━━━━━┛  │
    │  ⚔️ 🎯 ⚔️  │
    ╰━━━━━━━━━━━╯
    """

    # Bjornaer + Animal themed
    BJORNAER_ANIMAL = """
    ╭━━━━━━━━━━━╮
    │  🐺 🦅 🐺  │
    │  ┏━━━━━┓  │
    │ ╭┫🦊🦊┣╮ │
    │ ││ 🦁 ││ │
    │ ╰┫━🐾━┣╯ │
    │  ┗━━━━━┛  │
    │  🐺 🦅 🐺  │
    ╰━━━━━━━━━━━╯
    """

    # Default face for other combinations
    DEFAULT = """
    ╭━━━━━━━━━━━╮
    │  ✨ 🌟 ✨  │
    │  ┏━━━━━┓  │
    │ ╭┫👁️👁️┣╮ │
    │ ││ 👃 ││ │
    │ ╰┫━👄━┣╯ │
    │  ┗━━━━━┛  │
    │  ✨ 🌟 ✨  │
    ╰━━━━━━━━━━━╯
    """


class FaceGenerator:
    """Generates appropriate face for a magus based on house and arts."""

    @staticmethod
    def get_highest_art(character: Character) -> tuple[str, str]:
        """Get the highest technique and form for the character."""
        highest_technique = max(character.techniques.items(), key=lambda x: x[1])
        highest_form = max(character.forms.items(), key=lambda x: x[1])
        return highest_technique[0], highest_form[0]

    @staticmethod
    def get_face(house: House, character: Character) -> str:
        """Get appropriate face based on house and highest arts."""
        technique, form = FaceGenerator.get_highest_art(character)

        # Define combinations that yield specific faces
        face_mapping = {
            (House.FLAMBEAU, "Ignem"): MagusFace.FLAMBEAU_IGNEM,
            (House.BONISAGUS, "Intellego"): MagusFace.BONISAGUS_INTELLEGO,
            (House.MERINITA, "Herbam"): MagusFace.MERINITA_HERBAM,
            (House.TREMERE, "Rego"): MagusFace.TREMERE_REGO,
            (House.BJORNAER, "Animal"): MagusFace.BJORNAER_ANIMAL,
        }

        return face_mapping.get((house, form), MagusFace.DEFAULT)
