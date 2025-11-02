"""
Noise generation for privacy protection.

This module implements intelligent noise addition to events while preserving
statistical patterns and research utility.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import numpy as np

from personatwin.models import Event
from personatwin.privacy import PrivacyLevel


@dataclass
class NoiseConfig:
    """Configuration for noise generation."""
    temporal_noise_days: int = 14  # ±14 days
    outcome_noise_probability: float = 0.05  # 5% chance of outcome variation
    location_generalization_level: str = "county"  # address → city → county → state
    add_synthetic_events: bool = False
    synthetic_event_probability: float = 0.1  # 10% chance per persona


class EventNoiseGeneration:
    """
    Add intelligent noise to events while preserving patterns.
    
    Implements multiple noise strategies:
    1. Temporal noise: Blur exact dates
    2. Outcome noise: Add uncertainty to outcomes
    3. Location generalization: Remove specific addresses
    4. Synthetic events: Add fake events for privacy
    """
    
    def __init__(
        self,
        privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM,
        config: Optional[NoiseConfig] = None
    ):
        self.privacy_level = privacy_level
        self.config = config or self._default_config()
    
    def _default_config(self) -> NoiseConfig:
        """Get default noise configuration based on privacy level."""
        if self.privacy_level == PrivacyLevel.LOW:
            return NoiseConfig(
                temporal_noise_days=7,
                outcome_noise_probability=0.02,
                location_generalization_level="city",
                add_synthetic_events=False,
            )
        elif self.privacy_level == PrivacyLevel.MEDIUM:
            return NoiseConfig(
                temporal_noise_days=14,
                outcome_noise_probability=0.05,
                location_generalization_level="county",
                add_synthetic_events=False,
            )
        elif self.privacy_level == PrivacyLevel.HIGH:
            return NoiseConfig(
                temporal_noise_days=30,
                outcome_noise_probability=0.10,
                location_generalization_level="county",
                add_synthetic_events=True,
                synthetic_event_probability=0.1,
            )
        else:  # MAXIMUM
            return NoiseConfig(
                temporal_noise_days=60,
                outcome_noise_probability=0.15,
                location_generalization_level="state",
                add_synthetic_events=True,
                synthetic_event_probability=0.2,
            )
    
    def add_temporal_noise(self, events: List[Event]) -> List[Event]:
        """
        Add noise to event dates while preserving temporal sequences.
        
        Requirements:
        - Blur exact dates to time periods
        - Preserve temporal sequences (Event A before Event B)
        - Maintain seasonal patterns if relevant
        """
        if not events:
            return events
        
        # Sort events by date to preserve order
        sorted_events = sorted(events, key=lambda e: e.date)
        
        noised_events = []
        cumulative_shift = timedelta(0)
        
        for i, event in enumerate(sorted_events):
            # Add random noise
            noise_days = random.randint(
                -self.config.temporal_noise_days,
                self.config.temporal_noise_days
            )
            noise = timedelta(days=noise_days)
            
            # Ensure ordering is preserved
            if i > 0:
                # Make sure this event is still after previous event
                prev_date = noised_events[i-1].date
                min_date = prev_date + timedelta(days=1)
                noised_date = event.date + noise
                
                if noised_date < min_date:
                    noised_date = min_date
            else:
                noised_date = event.date + noise
            
            # Create new event with noised date
            noised_event = Event(
                event_id=event.event_id,
                date=noised_date,
                event_type=event.event_type,
                outcome=event.outcome,
                details=event.details.copy(),
                location=event.location,
                associated_people=event.associated_people.copy(),
                category=event.category,
                severity=event.severity,
            )
            
            noised_events.append(noised_event)
        
        return noised_events
    
    def add_outcome_noise(self, events: List[Event], valid_outcomes: Optional[List[str]] = None) -> List[Event]:
        """
        Add noise to event outcomes while maintaining realism.
        
        Requirements:
        - Slightly modify outcomes within realistic ranges
        - Preserve overall statistical distributions
        - Ensure legal/logical realism
        """
        noised_events = []
        
        for event in events:
            if random.random() < self.config.outcome_noise_probability:
                # Add noise to this outcome
                if valid_outcomes and event.outcome in valid_outcomes:
                    # Choose a similar valid outcome
                    new_outcome = random.choice(valid_outcomes)
                else:
                    # Keep original
                    new_outcome = event.outcome
            else:
                new_outcome = event.outcome
            
            # Create new event with potentially noised outcome
            noised_event = Event(
                event_id=event.event_id,
                date=event.date,
                event_type=event.event_type,
                outcome=new_outcome,
                details=event.details.copy(),
                location=event.location,
                associated_people=event.associated_people.copy(),
                category=event.category,
                severity=event.severity,
            )
            
            noised_events.append(noised_event)
        
        return noised_events
    
    def generalize_locations(self, events: List[Event]) -> List[Event]:
        """
        Generalize geographic locations to reduce specificity.
        
        Levels: address → city → county → state → country
        """
        generalized_events = []
        
        for event in events:
            if event.location:
                generalized_location = self._generalize_location(
                    event.location,
                    self.config.location_generalization_level
                )
            else:
                generalized_location = None
            
            generalized_event = Event(
                event_id=event.event_id,
                date=event.date,
                event_type=event.event_type,
                outcome=event.outcome,
                details=event.details.copy(),
                location=generalized_location,
                associated_people=event.associated_people.copy(),
                category=event.category,
                severity=event.severity,
            )
            
            generalized_events.append(generalized_event)
        
        return generalized_events
    
    def _generalize_location(self, location: str, level: str) -> str:
        """
        Generalize a specific location to a broader area.
        
        Args:
            location: Original location string
            level: Target generalization level (city, county, state, country)
            
        Returns:
            Generalized location string
        """
        # Parse location (assuming format: "address, city, county, state, country")
        parts = [p.strip() for p in location.split(",")]
        
        if level == "address":
            return location  # No generalization
        elif level == "city" and len(parts) >= 2:
            return ", ".join(parts[1:2])  # City only
        elif level == "county" and len(parts) >= 3:
            return ", ".join(parts[2:3])  # County only
        elif level == "state" and len(parts) >= 4:
            return ", ".join(parts[3:4])  # State only
        elif level == "country" and len(parts) >= 5:
            return ", ".join(parts[4:5])  # Country only
        else:
            # Return what we have
            return parts[0] if parts else location
    
    def add_noise_to_events(
        self,
        events: List[Event],
        valid_outcomes: Optional[List[str]] = None
    ) -> List[Event]:
        """
        Apply all noise strategies to events.
        
        Args:
            events: Original events
            valid_outcomes: Valid outcomes for domain (for realistic outcome noise)
            
        Returns:
            Events with noise applied
        """
        # Apply temporal noise
        noised_events = self.add_temporal_noise(events)
        
        # Apply outcome noise
        noised_events = self.add_outcome_noise(noised_events, valid_outcomes)
        
        # Generalize locations
        noised_events = self.generalize_locations(noised_events)
        
        return noised_events
    
    def generalize_temporal_precision(
        self,
        events: List[Event],
        precision: str = "month"
    ) -> List[Event]:
        """
        Generalize dates to broader time periods.
        
        Args:
            events: Original events
            precision: "day", "week", "month", "quarter", "year"
            
        Returns:
            Events with generalized dates
        """
        generalized_events = []
        
        for event in events:
            date = event.date
            
            if precision == "week":
                # First day of week
                date = date - timedelta(days=date.weekday())
            elif precision == "month":
                # First day of month
                date = date.replace(day=1)
            elif precision == "quarter":
                # First day of quarter
                quarter_month = ((date.month - 1) // 3) * 3 + 1
                date = date.replace(month=quarter_month, day=1)
            elif precision == "year":
                # First day of year
                date = date.replace(month=1, day=1)
            # "day" precision keeps the date as-is
            
            generalized_event = Event(
                event_id=event.event_id,
                date=date,
                event_type=event.event_type,
                outcome=event.outcome,
                details=event.details.copy(),
                location=event.location,
                associated_people=event.associated_people.copy(),
                category=event.category,
                severity=event.severity,
            )
            
            generalized_events.append(generalized_event)
        
        return generalized_events
