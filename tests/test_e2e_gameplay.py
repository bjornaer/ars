from unittest.mock import Mock

import pytest

from ars.certamen import CertamenManager
from ars.character import Character
from ars.combat import CombatManager, WoundSeverity
from ars.covenant import Covenant
from ars.events import EventType
from ars.laboratory import Laboratory
from ars.seasons import SeasonManager
from ars.spell_research import ResearchProject, ResearchType
from ars.spells import Spell, SpellCaster, SpellParameters
from ars.core.types import AbilityType, Duration, Form, House, Range, Target, Technique


class TestEndToEndGameplay:
    """
    Comprehensive end-to-end testing of core gameplay mechanics.
    Tests the complete lifecycle of characters, spells, and interactions.
    """

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test environment with all necessary components."""
        self.data_path = tmp_path / "data"
        self.data_path.mkdir()

        # Create event manager
        self.event_manager = Mock()

        # Create covenant
        self.covenant = Covenant(name="Test Covenant", size="Small", age=10, aura=3)
        self.covenant.event_manager = self.event_manager

        # Create characters
        self.mage = Character(
            name="Marcus of Bonisagus",
            player="Test Player",
            saga="Test Saga",
            covenant="Test Covenant",
            house=House.BONISAGUS,
        )
        self.mage.event_manager = self.event_manager

        # Set up mage's abilities and arts
        self.mage.techniques = {"Creo": 10, "Intellego": 8, "Muto": 6, "Perdo": 5, "Rego": 7}
        self.mage.forms = {
            "Animal": 5,
            "Aquam": 4,
            "Auram": 6,
            "Corpus": 7,
            "Herbam": 3,
            "Ignem": 8,
            "Imaginem": 4,
            "Mentem": 5,
            "Terram": 6,
            "Vim": 7,
        }
        self.mage.abilities[AbilityType.ARCANE]["Magic Theory"] = 5
        self.mage.abilities[AbilityType.ARCANE]["Parma Magica"] = 3

        # Create laboratory
        self.laboratory = Laboratory(owner=self.mage.name, size=2, magical_aura=self.covenant.aura)
        self.laboratory.event_manager = self.event_manager

        # Save initial state
        self.covenant.save(directory=self.data_path)
        self.mage.save(directory=self.data_path)
        self.laboratory.save(directory=self.data_path)

    def test_complete_gameplay_cycle(self):
        """
        Test a complete gameplay cycle including:
        - Spell research and creation
        - Laboratory activities
        - Certamen
        - Combat
        - Seasonal activities
        - Event recording
        """
        # 1. Spell Research and Creation
        research_project = ResearchProject(
            researcher=self.mage.name,
            research_type=ResearchType.SPELL_CREATION,
            target_level=15,
            technique=Technique.CREO,
            form=Form.IGNEM,
        )

        # Conduct research for one season
        from ars.spell_research_manager import SpellResearchManager

        result = SpellResearchManager.conduct_research(research_project, self.mage, self.laboratory)

        assert result.outcome in ["Success", "Partial Success", "Breakthrough"]
        assert result.points_gained > 0

        # 2. Create and Cast Spell
        spell = Spell.create(
            SpellParameters(
                name="Ball of Abysmal Flame",
                technique=Technique.CREO,
                form=Form.IGNEM,
                level=15,
                range=Range.VOICE,
                duration=Duration.MOMENTARY,
                target=Target.INDIVIDUAL,
                description="Creates a powerful ball of flame",
            )
        )

        self.mage.spells = {spell.name: spell}

        # Cast the spell
        cast_result = SpellCaster.cast_spell(spell, self.mage, aura=self.covenant.aura)

        assert cast_result.success
        assert cast_result.fatigue_cost > 0

        # 3. Certamen Duel
        opponent = Character(
            name="Rivalus of Flambeau",
            player="Test Player",
            saga="Test Saga",
            covenant="Test Covenant",
            house=House.FLAMBEAU,
        )
        opponent.techniques = {"Creo": 8, "Rego": 9}
        opponent.forms = {"Ignem": 10, "Corpus": 6}

        certamen = CertamenManager(self.event_manager)
        duel = certamen.initiate_certamen(self.mage, opponent, Technique.CREO, Form.IGNEM)

        assert duel.winner in [self.mage.name, opponent.name]
        assert duel.rounds == 3

        # Conduct three exchanges
        for _ in range(3):
            result = certamen.resolve_exchange(self.mage, opponent)
            assert "results" in result
            assert "scores" in result

        final_result = certamen.end_certamen(self.mage, opponent)
        assert final_result.winner in [self.mage.name, opponent.name]
        assert final_result.rounds == 3

        # 4. Combat System
        combat = CombatManager(self.event_manager)

        # Add some combat abilities
        self.mage.abilities["Martial"] = {"Single Weapon": 3, "Dodge": 2}
        opponent.abilities["Martial"] = {"Single Weapon": 4, "Dodge": 3}

        combat_result = combat.resolve_attack(opponent, self.mage, "sword")

        # Verify combat results
        assert isinstance(combat_result.hit, bool)
        if combat_result.hit and combat_result.wound:
            assert combat_result.wound.severity in WoundSeverity
            assert combat_result.wound.recovery_time > 0

        # 5. Seasonal Activities
        season_manager = SeasonManager("Test Saga")
        season_manager.register_character(self.mage)
        season_manager.set_covenant(self.covenant)

        # Schedule activities
        season_manager.schedule_activity(self.mage.name, "Study", {"source": "Magic Theory Tractatus", "quality": 10})

        # Execute season
        results = season_manager.execute_season()
        assert self.mage.name in results
        assert "Study" in results[self.mage.name]

        # 6. Verify Event Recording
        event_calls = self.event_manager.record_event.call_args_list

        # Check for different types of events
        event_types = [call.kwargs["type"] for call in event_calls]
        assert EventType.RESEARCH in event_types
        assert EventType.SPELLCASTING in event_types
        assert EventType.CERTAMEN in event_types
        assert EventType.COMBAT in event_types

        # 7. Save and Load State
        self.mage.save(directory=self.data_path)
        loaded_mage = Character.load(self.mage.name, directory=self.data_path)

        # Verify state persistence
        assert loaded_mage.name == self.mage.name
        assert loaded_mage.spells.keys() == self.mage.spells.keys()
        assert len(loaded_mage.abilities) == len(self.mage.abilities)

        # 8. Verify Character State
        assert self.mage.fatigue_level > 0  # Should have accumulated fatigue
        if combat_result.hit:
            assert len(self.mage.wounds) > 0  # Should have wounds if hit

        # 9. Laboratory Integration
        assert self.laboratory.magical_aura == self.covenant.aura
        assert self.laboratory.owner == self.mage.name

        # 10. Covenant Integration
        assert self.mage.covenant == self.covenant.name
        assert self.covenant.aura > 0
