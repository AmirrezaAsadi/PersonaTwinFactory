"""Data models for Digital Persona Twin attributes and behaviors."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PersonaAttributes(BaseModel):
    """Core attributes defining a digital persona twin."""

    persona_id: str = Field(..., description="Unique identifier for the persona")
    name: str = Field(..., description="Name of the persona")
    age: Optional[int] = Field(None, ge=0, le=150, description="Age of the persona")
    gender: Optional[str] = Field(None, description="Gender identity")
    occupation: Optional[str] = Field(None, description="Occupation or role")
    interests: List[str] = Field(default_factory=list, description="List of interests")
    traits: Dict[str, Any] = Field(
        default_factory=dict, description="Personality traits and characteristics"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of creation"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of last update"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class PersonaBehavior(BaseModel):
    """Behavioral patterns and interaction history of a persona twin."""

    persona_id: str = Field(..., description="Reference to the persona")
    behavior_type: str = Field(..., description="Type of behavior recorded")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Context of the behavior"
    )
    response: Optional[str] = Field(None, description="Response or action taken")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="When the behavior occurred"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class DataSnapshot(BaseModel):
    """Snapshot of persona data at a specific point in time."""

    snapshot_id: str = Field(..., description="Unique identifier for this snapshot")
    persona_id: str = Field(..., description="Reference to the persona")
    attributes: PersonaAttributes = Field(..., description="Persona attributes")
    behaviors: List[PersonaBehavior] = Field(
        default_factory=list, description="Recent behaviors"
    )
    snapshot_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="When snapshot was created"
    )
    checksum: Optional[str] = Field(None, description="Data integrity checksum")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
