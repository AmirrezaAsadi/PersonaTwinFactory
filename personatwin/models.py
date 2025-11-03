"""
Core data models for PersonaTwin system.

This module defines the fundamental data structures used throughout the system:
- Person: Original individual with demographics and events
- Event: Individual occurrence (extensible for any domain)
- Persona: Merged, privacy-protected synthetic entity
- Demographics: Demographic information with privacy protection

The system is domain-agnostic and supports:
- Criminal Justice (arrests, sentencing, etc.)
- Healthcare (visits, treatments, diagnoses)
- Education (enrollments, assessments, graduations)
- Social Services (benefits, case management, outcomes)
- And any other people-events domain
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid


@dataclass
class Demographics:
    """Demographic information for a person."""
    age: Optional[int] = None
    age_range: Optional[str] = None  # e.g., "30-35"
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    geography: Optional[str] = None  # Will be generalized to county/region
    socioeconomic_indicators: Dict[str, Any] = field(default_factory=dict)
    confidence_level: float = 1.0  # How much noise was added (1.0 = original, 0.0 = heavily noised)
    
    def generalize_age(self, bin_size: int = 5) -> str:
        """Convert exact age to age range."""
        if self.age is None:
            return "Unknown"
        lower = (self.age // bin_size) * bin_size
        upper = lower + bin_size - 1
        return f"{lower}-{upper}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "age": self.age,
            "age_range": self.age_range or (self.generalize_age() if self.age else None),
            "gender": self.gender,
            "ethnicity": self.ethnicity,
            "geography": self.geography,
            "socioeconomic_indicators": self.socioeconomic_indicators,
            "confidence_level": self.confidence_level,
        }


@dataclass
class Event:
    """
    Individual event in a person's history.
    
    Domain-agnostic event structure supporting any type of occurrence:
    - Criminal Justice: arrest, trial, sentencing
    - Healthcare: visit, diagnosis, treatment, discharge
    - Education: enrollment, assessment, graduation
    - Social Services: application, case_opened, benefit_received
    
    Events are timestamped occurrences with outcomes and details.
    Privacy protection involves generalizing dates, locations, and adding noise.
    """
    event_id: str
    date: datetime
    event_type: str  # Flexible string (e.g., "arrest", "hospital_visit", "enrollment")
    outcome: Optional[str] = None  # Flexible outcome (e.g., "guilty", "recovered", "graduated")
    details: Dict[str, Any] = field(default_factory=dict)
    location: Optional[str] = None  # Will be generalized
    associated_people: List[str] = field(default_factory=list)  # Person IDs (will be anonymized)
    category: Optional[str] = None  # Domain category (e.g., "criminal_justice", "healthcare")
    severity: Optional[str] = None  # Event severity/priority (e.g., "high", "medium", "low")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "date": self.date.isoformat() if self.date else None,
            "event_type": self.event_type,
            "outcome": self.outcome,
            "details": self.details,
            "location": self.location,
            "associated_people": self.associated_people,
            "category": self.category,
            "severity": self.severity,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create Event from dictionary."""
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            date=datetime.fromisoformat(data["date"]) if data.get("date") else datetime.now(),
            event_type=data.get("event_type", "unknown"),
            outcome=data.get("outcome"),
            details=data.get("details", {}),
            location=data.get("location"),
            associated_people=data.get("associated_people", []),
            category=data.get("category"),
            severity=data.get("severity"),
        )


@dataclass
class Person:
    """
    Original person with demographics and event history.
    
    This represents the sensitive input data that will be transformed
    into privacy-protected personas.
    """
    person_id: str
    demographics: Demographics
    events: List[Event] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # IDs of connected people
    social_circle_ids: List[str] = field(default_factory=list)  # Community/group memberships
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "person_id": self.person_id,
            "demographics": self.demographics.to_dict(),
            "events": [event.to_dict() for event in self.events],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        """Create Person from dictionary."""
        demographics_data = data.get("demographics", {})
        demographics = Demographics(
            age=demographics_data.get("age"),
            age_range=demographics_data.get("age_range"),
            gender=demographics_data.get("gender"),
            ethnicity=demographics_data.get("ethnicity"),
            geography=demographics_data.get("geography"),
            socioeconomic_indicators=demographics_data.get("socioeconomic_indicators", {}),
            confidence_level=demographics_data.get("confidence_level", 1.0),
        )
        
        events = [Event.from_dict(e) for e in data.get("events", [])]
        
        return cls(
            person_id=data["person_id"],
            demographics=demographics,
            events=events,
        )


@dataclass
class PrivacyMetadata:
    """Metadata about privacy protection applied to a persona."""
    traceability_score: float  # Risk level for this persona (0-1)
    noise_level: float  # Amount of noise added (0-1)
    merge_count: int  # Number of people merged
    generation_method: str  # Algorithm used
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "traceability_score": self.traceability_score,
            "noise_level": self.noise_level,
            "merge_count": self.merge_count,
            "generation_method": self.generation_method,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class EventPatterns:
    """Statistical patterns extracted from events."""
    event_types: List[str] = field(default_factory=list)
    temporal_patterns: Dict[str, Any] = field(default_factory=dict)
    outcome_distributions: Dict[str, float] = field(default_factory=dict)
    recidivism_indicators: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_types": self.event_types,
            "temporal_patterns": self.temporal_patterns,
            "outcome_distributions": self.outcome_distributions,
            "recidivism_indicators": self.recidivism_indicators,
        }


@dataclass
class Persona:
    """
    Privacy-protected synthetic persona.
    
    Generated by merging similar people and adding noise to reduce
    re-identification risk while preserving statistical utility.
    """
    persona_id: str
    merged_from: int  # Number of real people merged
    demographics: Demographics
    event_patterns: EventPatterns
    privacy_metadata: PrivacyMetadata
    events: List[Event] = field(default_factory=list)  # Combined events from merged people
    connections: List[str] = field(default_factory=list)  # IDs of connected personas
    connection_count: int = 0  # Approximate number of connections (with noise)
    social_circles: List[str] = field(default_factory=list)  # Community memberships
    merged_person_ids: List[str] = field(default_factory=list)  # Track which people were merged
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_id": self.persona_id,
            "merged_from": self.merged_from,
            "demographics": self.demographics.to_dict(),
            "event_patterns": self.event_patterns.to_dict(),
            "privacy_metadata": self.privacy_metadata.to_dict(),
            "events": [event.to_dict() for event in self.events],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Persona':
        """Create Persona from dictionary."""
        demographics_data = data.get("demographics", {})
        demographics = Demographics(
            age=demographics_data.get("age"),
            age_range=demographics_data.get("age_range"),
            gender=demographics_data.get("gender"),
            ethnicity=demographics_data.get("ethnicity"),
            geography=demographics_data.get("geography"),
            socioeconomic_indicators=demographics_data.get("socioeconomic_indicators", {}),
            confidence_level=demographics_data.get("confidence_level", 1.0),
        )
        
        event_patterns_data = data.get("event_patterns", {})
        event_patterns = EventPatterns(
            event_types=event_patterns_data.get("event_types", []),
            temporal_patterns=event_patterns_data.get("temporal_patterns", {}),
            outcome_distributions=event_patterns_data.get("outcome_distributions", {}),
            recidivism_indicators=event_patterns_data.get("recidivism_indicators", {}),
        )
        
        privacy_metadata_data = data.get("privacy_metadata", {})
        privacy_metadata = PrivacyMetadata(
            traceability_score=privacy_metadata_data.get("traceability_score", 0.0),
            noise_level=privacy_metadata_data.get("noise_level", 0.0),
            merge_count=privacy_metadata_data.get("merge_count", 1),
            generation_method=privacy_metadata_data.get("generation_method", "unknown"),
        )
        
        events = [Event.from_dict(e) for e in data.get("events", [])]
        
        return cls(
            persona_id=data["persona_id"],
            merged_from=data.get("merged_from", 1),
            demographics=demographics,
            event_patterns=event_patterns,
            privacy_metadata=privacy_metadata,
            events=events,
        )
