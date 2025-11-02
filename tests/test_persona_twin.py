"""Tests for PersonaTwin class."""

import pytest
import tempfile
from pathlib import Path
from personatwinfactory import PersonaTwin, TransparencyLogger


class TestPersonaTwin:
    """Test PersonaTwin functionality."""

    def test_create_persona(self):
        """Test creating a new persona."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="Test User", transparency_logger=logger)
            
            assert persona.attributes.name == "Test User"
            assert persona.persona_id is not None
            assert len(persona.behaviors) == 0

    def test_update_attributes(self):
        """Test updating persona attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="Alice", transparency_logger=logger)
            
            persona.update_attributes(
                age=25,
                occupation="Developer",
                user_id="admin",
            )
            
            assert persona.attributes.age == 25
            assert persona.attributes.occupation == "Developer"

    def test_add_behavior(self):
        """Test adding a behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="Bob", transparency_logger=logger)
            
            behavior = persona.add_behavior(
                behavior_type="interaction",
                context={"action": "click"},
                response="success",
            )
            
            assert behavior.behavior_type == "interaction"
            assert len(persona.behaviors) == 1

    def test_get_behaviors(self):
        """Test retrieving behaviors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="Charlie", transparency_logger=logger)
            
            persona.add_behavior("type1", context={"data": 1})
            persona.add_behavior("type2", context={"data": 2})
            persona.add_behavior("type1", context={"data": 3})
            
            all_behaviors = persona.get_behaviors()
            assert len(all_behaviors) == 3
            
            type1_behaviors = persona.get_behaviors(behavior_type="type1")
            assert len(type1_behaviors) == 2
            
            limited = persona.get_behaviors(limit=2)
            assert len(limited) == 2

    def test_create_snapshot(self):
        """Test creating a data snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="David", transparency_logger=logger)
            
            persona.add_behavior("test", context={})
            snapshot = persona.create_snapshot()
            
            assert snapshot.persona_id == persona.persona_id
            assert snapshot.checksum is not None
            assert len(snapshot.behaviors) >= 1

    def test_save_and_load(self):
        """Test saving and loading a persona."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "personas"
            logger = TransparencyLogger(log_directory=Path(tmpdir) / "logs")
            
            # Create and save
            persona = PersonaTwin(
                name="Eve",
                transparency_logger=logger,
                storage_path=storage_path,
            )
            persona.update_attributes(age=30, occupation="Analyst")
            persona.add_behavior("test", context={"key": "value"})
            
            file_path = persona.save()
            assert file_path.exists()
            
            # Load
            loaded = PersonaTwin.load(
                persona.persona_id,
                transparency_logger=logger,
                storage_path=storage_path,
            )
            
            assert loaded.persona_id == persona.persona_id
            assert loaded.attributes.name == "Eve"
            assert loaded.attributes.age == 30
            assert len(loaded.behaviors) == 1

    def test_load_nonexistent_persona(self):
        """Test loading a non-existent persona."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                PersonaTwin.load("nonexistent-id", storage_path=Path(tmpdir))

    def test_get_audit_trail(self):
        """Test retrieving audit trail for a persona."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="Frank", transparency_logger=logger)
            
            persona.update_attributes(age=40)
            persona.add_behavior("test", context={})
            
            audit_trail = persona.get_audit_trail()
            assert len(audit_trail) > 0
            assert all("operation" in log for log in audit_trail)

    def test_persona_repr(self):
        """Test persona string representation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="Grace", transparency_logger=logger)
            
            repr_str = repr(persona)
            assert "PersonaTwin" in repr_str
            assert "Grace" in repr_str
            assert persona.persona_id in repr_str

    def test_multiple_behavior_types(self):
        """Test handling multiple behavior types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            persona = PersonaTwin(name="Henry", transparency_logger=logger)
            
            # Add various behavior types
            persona.add_behavior("interaction", context={"type": "click"})
            persona.add_behavior("preference", context={"type": "privacy"})
            persona.add_behavior("interaction", context={"type": "scroll"})
            
            interactions = persona.get_behaviors(behavior_type="interaction")
            preferences = persona.get_behaviors(behavior_type="preference")
            
            assert len(interactions) == 2
            assert len(preferences) == 1
