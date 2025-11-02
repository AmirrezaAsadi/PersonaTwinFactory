"""
Basic tests for PersonaTwin package.
"""

import pytest
from datetime import datetime
import personatwin as pt


def test_demographics_creation():
    """Test Demographics model creation."""
    demo = pt.Demographics(
        age=30,
        gender="Male",
        ethnicity="White",
        geography="Test County"
    )
    assert demo.age == 30
    assert demo.gender == "Male"
    assert demo.generalize_age() == "30-34"


def test_event_creation():
    """Test Event model creation."""
    event = pt.Event(
        event_id="E001",
        date=datetime.now(),
        event_type="test_event",
        outcome="completed",
        location="Test Location"
    )
    assert event.event_id == "E001"
    assert event.event_type == "test_event"
    assert event.outcome == "completed"


def test_person_creation():
    """Test Person model creation."""
    demo = pt.Demographics(age=25, gender="Female")
    event = pt.Event(
        event_id="E001",
        date=datetime.now(),
        event_type="test"
    )
    person = pt.Person(
        person_id="P001",
        demographics=demo,
        events=[event]
    )
    assert person.person_id == "P001"
    assert len(person.events) == 1


def test_domain_configs():
    """Test domain configurations are available."""
    assert pt.CRIMINAL_JUSTICE_CONFIG is not None
    assert pt.HEALTHCARE_CONFIG is not None
    assert pt.EDUCATION_CONFIG is not None
    assert pt.SOCIAL_SERVICES_CONFIG is not None
    assert pt.EMPLOYMENT_CONFIG is not None
    
    # Test event types
    assert "arrest" in pt.CRIMINAL_JUSTICE_CONFIG.event_types
    assert "admission" in pt.HEALTHCARE_CONFIG.event_types
    assert "enrollment" in pt.EDUCATION_CONFIG.event_types


def test_custom_domain_config():
    """Test custom domain configuration creation."""
    config = pt.create_custom_config(
        event_types=["event1", "event2"],
        outcomes=["outcome1", "outcome2"],
        sensitive_fields={"field1"},
        preserve_fields={"field2"},
        temporal_precision="month",
        geographic_precision="county"
    )
    assert config.domain == pt.Domain.CUSTOM
    assert len(config.event_types) == 2
    assert len(config.outcomes) == 2


def test_people_merging():
    """Test people merging functionality."""
    # Create sample people
    people = []
    for i in range(10):
        demo = pt.Demographics(age=30+i, gender="Male", ethnicity="White")
        person = pt.Person(
            person_id=f"P{i}",
            demographics=demo,
            events=[]
        )
        people.append(person)
    
    # Merge them
    merger = pt.PeopleMerging(privacy_level=pt.PrivacyLevel.MEDIUM)
    personas = merger.merge_similar_people(people)
    
    # Should have fewer personas than people
    assert len(personas) <= len(people)
    assert all(p.merged_from >= 1 for p in personas)


def test_risk_calculation():
    """Test privacy risk calculation."""
    # Create sample personas
    personas = []
    for i in range(5):
        demo = pt.Demographics(age=30, gender="Male")
        privacy_meta = pt.PrivacyMetadata(
            traceability_score=0.1,
            noise_level=0.2,
            merge_count=5,
            generation_method="test"
        )
        persona = pt.Persona(
            persona_id=f"PA{i}",
            merged_from=5,
            demographics=demo,
            event_patterns=pt.EventPatterns(),
            privacy_metadata=privacy_meta,
            events=[]
        )
        personas.append(persona)
    
    # Calculate risk
    calc = pt.PopulationTraceability()
    metrics = calc.calculate_population_risk(personas)
    
    assert metrics.population_average_risk >= 0.0
    assert metrics.population_average_risk <= 1.0
    assert metrics.k_anonymity == 5


def test_privacy_levels():
    """Test privacy level enum."""
    assert pt.PrivacyLevel.LOW.value == "low"
    assert pt.PrivacyLevel.MEDIUM.value == "medium"
    assert pt.PrivacyLevel.HIGH.value == "high"
    assert pt.PrivacyLevel.MAXIMUM.value == "maximum"


def test_noise_generation():
    """Test noise generation."""
    event = pt.Event(
        event_id="E001",
        date=datetime.now(),
        event_type="test",
        location="123 Main St, City, County, State"
    )
    
    noise_gen = pt.EventNoiseGeneration(privacy_level=pt.PrivacyLevel.MEDIUM)
    noised_events = noise_gen.add_temporal_noise([event])
    
    assert len(noised_events) == 1
    # Date should be different (with high probability)
    # (Could be same if random noise is 0, but unlikely)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
