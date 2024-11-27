import pytest

from ars.spells import Duration, Form, Range, SpellEffect, SpellTemplate, Target, Technique


@pytest.fixture
def fireball_template():
    return SpellTemplate(
        name_pattern="Ball of {element} Fire",
        technique=Technique.CREO,
        form=Form.IGNEM,
        base_level=10,
        effects=[SpellEffect("Create fire", 5, {"size": 2})],
        description_pattern="Creates a ball of {element} fire.",
    )


def test_spell_creation(fireball_template):
    spell = fireball_template.create_spell(
        specific_name="Ball of Intense Fire", range=Range.VOICE, duration=Duration.MOMENTARY, target=Target.INDIVIDUAL
    )

    assert spell.name == "Ball of Intense Fire"
    assert spell.technique == "Creo"
    assert spell.form == "Ignem"
    assert spell.description == "Creates a ball of Intense fire."
    assert spell.level > 10  # Base level plus modifiers


def test_spell_effect_magnitude():
    effect = SpellEffect("Test effect", 5, {"power": 2, "range": 1})
    assert effect.calculate_magnitude() == 8
