"""Tests for data models."""

import pytest
from datetime import datetime
from personatwinfactory.data_models import (
    PersonaAttributes,
    PersonaBehavior,
    DataSnapshot,
)


class TestPersonaAttributes:
    """Test PersonaAttributes model."""

    def test_create_basic_attributes(self):
        """Test creating basic persona attributes."""
        attrs = PersonaAttributes(
            persona_id="test-123",
            name="Test User",
        )
        assert attrs.persona_id == "test-123"
        assert attrs.name == "Test User"
        assert attrs.age is None
        assert isinstance(attrs.created_at, datetime)

    def test_create_full_attributes(self):
        """Test creating persona attributes with all fields."""
        attrs = PersonaAttributes(
            persona_id="test-456",
            name="Jane Doe",
            age=30,
            gender="Female",
            occupation="Engineer",
            interests=["coding", "reading"],
            traits={"openness": 0.8},
        )
        assert attrs.age == 30
        assert attrs.gender == "Female"
        assert len(attrs.interests) == 2
        assert attrs.traits["openness"] == 0.8

    def test_age_validation(self):
        """Test age validation constraints."""
        with pytest.raises(Exception):  # Pydantic validation error
            PersonaAttributes(
                persona_id="test-789",
                name="Invalid Age",
                age=200,  # Invalid age
            )


class TestPersonaBehavior:
    """Test PersonaBehavior model."""

    def test_create_behavior(self):
        """Test creating a behavior record."""
        behavior = PersonaBehavior(
            persona_id="test-123",
            behavior_type="interaction",
            context={"platform": "web"},
            response="clicked_button",
        )
        assert behavior.persona_id == "test-123"
        assert behavior.behavior_type == "interaction"
        assert behavior.context["platform"] == "web"
        assert isinstance(behavior.timestamp, datetime)

    def test_behavior_with_metadata(self):
        """Test behavior with metadata."""
        behavior = PersonaBehavior(
            persona_id="test-456",
            behavior_type="preference",
            metadata={"source": "survey", "confidence": 0.95},
        )
        assert behavior.metadata["source"] == "survey"
        assert behavior.metadata["confidence"] == 0.95


class TestDataSnapshot:
    """Test DataSnapshot model."""

    def test_create_snapshot(self):
        """Test creating a data snapshot."""
        attrs = PersonaAttributes(persona_id="test-123", name="Test")
        snapshot = DataSnapshot(
            snapshot_id="snap-001",
            persona_id="test-123",
            attributes=attrs,
            behaviors=[],
        )
        assert snapshot.snapshot_id == "snap-001"
        assert snapshot.attributes.name == "Test"
        assert len(snapshot.behaviors) == 0

    def test_snapshot_with_behaviors(self):
        """Test snapshot with behaviors."""
        attrs = PersonaAttributes(persona_id="test-123", name="Test")
        behaviors = [
            PersonaBehavior(
                persona_id="test-123",
                behavior_type="test",
            )
        ]
        snapshot = DataSnapshot(
            snapshot_id="snap-002",
            persona_id="test-123",
            attributes=attrs,
            behaviors=behaviors,
            checksum="abc123",
        )
        assert len(snapshot.behaviors) == 1
        assert snapshot.checksum == "abc123"
