"""
Intelligent event merging strategies for PersonaTwin PrivacyForge.

This module provides sophisticated event merging that creates realistic personas
by preserving logical sequences and combining similar events.
"""

from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from collections import defaultdict

from .models import Event, Person, Persona
from .domains import Domain


class EventMergingStrategy(Enum):
    """Strategy for merging events from multiple people."""
    CONCATENATE = "concatenate"  # Simple concatenation (current, problematic)
    INTERLEAVE = "interleave"    # Chronological interleaving
    SIMILARITY = "similarity"     # Merge similar events using cosine similarity
    AGGREGATE = "aggregate"       # Create composite events
    SAMPLE = "sample"             # Sample representative events
    RULE_BASED = "rule_based"     # Follow domain-specific logic


@dataclass
class EventSimilarity:
    """Similarity score between two events."""
    event1: Event
    event2: Event
    similarity: float  # 0.0 to 1.0
    reasons: List[str]  # Why they're similar


@dataclass
class EventSequenceRule:
    """Domain-specific rule for event sequences."""
    event_type: str
    must_follow: Optional[List[str]] = None  # Events that must come before
    cannot_follow: Optional[List[str]] = None  # Events that cannot come before
    max_occurrences: Optional[int] = None  # Max times this can occur
    requires_closure: bool = False  # Requires a closing event (e.g., discharge after admission)
    closure_event_type: Optional[str] = None


class DomainEventRules:
    """Event sequence rules for different domains."""
    
    @staticmethod
    def get_rules(domain: Domain) -> Dict[str, EventSequenceRule]:
        """Get event rules for a domain."""
        
        if domain == Domain.CRIMINAL_JUSTICE:
            return {
                "arrest": EventSequenceRule("arrest", max_occurrences=None),
                "charge": EventSequenceRule("charge", must_follow=["arrest"]),
                "trial": EventSequenceRule("trial", must_follow=["charge"]),
                "sentencing": EventSequenceRule("sentencing", must_follow=["trial"]),
                "incarceration": EventSequenceRule(
                    "incarceration", 
                    must_follow=["sentencing"],
                    requires_closure=True,
                    closure_event_type="release"
                ),
                "release": EventSequenceRule("release", must_follow=["incarceration"]),
                "probation": EventSequenceRule("probation", must_follow=["sentencing"]),
                "appeal": EventSequenceRule("appeal", must_follow=["sentencing"]),
            }
        
        elif domain == Domain.HEALTHCARE:
            return {
                "admission": EventSequenceRule(
                    "admission",
                    requires_closure=True,
                    closure_event_type="discharge"
                ),
                "discharge": EventSequenceRule("discharge", must_follow=["admission"]),
                "diagnosis": EventSequenceRule("diagnosis"),
                "treatment": EventSequenceRule("treatment", must_follow=["diagnosis"]),
                "surgery": EventSequenceRule("surgery", must_follow=["admission"]),
                "medication": EventSequenceRule("medication", must_follow=["diagnosis"]),
                "follow_up": EventSequenceRule("follow_up", must_follow=["discharge"]),
            }
        
        elif domain == Domain.EDUCATION:
            return {
                "enrollment": EventSequenceRule("enrollment", max_occurrences=None),
                "assessment": EventSequenceRule("assessment", must_follow=["enrollment"]),
                "grade": EventSequenceRule("grade", must_follow=["enrollment"]),
                "promotion": EventSequenceRule("promotion", must_follow=["grade"]),
                "graduation": EventSequenceRule("graduation", must_follow=["enrollment"]),
                "suspension": EventSequenceRule("suspension", must_follow=["enrollment"]),
            }
        
        else:
            return {}  # No specific rules for other domains


class EventSimilarityCalculator:
    """Calculate similarity between events for intelligent merging."""
    
    @staticmethod
    def calculate_similarity(event1: Event, event2: Event, domain: Domain) -> EventSimilarity:
        """
        Calculate cosine similarity between two events.
        
        Events are similar if they have:
        - Same event type
        - Similar dates (within timeframe)
        - Same outcome
        - Similar locations
        """
        similarity_score = 0.0
        reasons = []
        
        # Event type similarity (most important)
        if event1.event_type == event2.event_type:
            similarity_score += 0.4
            reasons.append(f"Same event type: {event1.event_type}")
        
        # Outcome similarity
        if event1.outcome == event2.outcome:
            similarity_score += 0.2
            reasons.append(f"Same outcome: {event1.outcome}")
        
        # Temporal similarity (within 6 months)
        date_diff = abs((event1.date - event2.date).days)
        if date_diff <= 180:  # 6 months
            temporal_sim = 1.0 - (date_diff / 180.0)
            similarity_score += 0.2 * temporal_sim
            reasons.append(f"Similar dates: {date_diff} days apart")
        
        # Location similarity
        if event1.location and event2.location:
            if event1.location == event2.location:
                similarity_score += 0.2
                reasons.append(f"Same location: {event1.location}")
            elif EventSimilarityCalculator._same_county(event1.location, event2.location):
                similarity_score += 0.1
                reasons.append("Same county")
        
        return EventSimilarity(event1, event2, similarity_score, reasons)
    
    @staticmethod
    def _same_county(loc1: str, loc2: str) -> bool:
        """Check if two locations are in the same county."""
        # Simple heuristic: check if "County" appears and matches
        if "County" in loc1 and "County" in loc2:
            county1 = loc1.split("County")[0].strip()
            county2 = loc2.split("County")[0].strip()
            return county1 == county2
        return False


class IntelligentEventMerger:
    """Merge events from multiple people into realistic persona events."""
    
    def __init__(self, domain: Domain, strategy: EventMergingStrategy = EventMergingStrategy.SIMILARITY):
        self.domain = domain
        self.strategy = strategy
        self.rules = DomainEventRules.get_rules(domain)
        self.similarity_calculator = EventSimilarityCalculator()
    
    def merge_events(self, people: List[Person]) -> List[Event]:
        """
        Merge events from multiple people into persona events.
        
        Args:
            people: List of people to merge
            
        Returns:
            List of merged events that create a realistic persona
        """
        if self.strategy == EventMergingStrategy.CONCATENATE:
            return self._concatenate_events(people)
        elif self.strategy == EventMergingStrategy.INTERLEAVE:
            return self._interleave_events(people)
        elif self.strategy == EventMergingStrategy.SIMILARITY:
            return self._merge_by_similarity(people)
        elif self.strategy == EventMergingStrategy.AGGREGATE:
            return self._aggregate_events(people)
        elif self.strategy == EventMergingStrategy.SAMPLE:
            return self._sample_events(people)
        elif self.strategy == EventMergingStrategy.RULE_BASED:
            return self._rule_based_merge(people)
        else:
            return self._merge_by_similarity(people)  # Default
    
    def _concatenate_events(self, people: List[Person]) -> List[Event]:
        """Simple concatenation (current problematic approach)."""
        all_events = []
        for person in people:
            all_events.extend(person.events)
        return sorted(all_events, key=lambda e: e.date)
    
    def _interleave_events(self, people: List[Person]) -> List[Event]:
        """Interleave events chronologically."""
        all_events = []
        for person in people:
            all_events.extend(person.events)
        return sorted(all_events, key=lambda e: e.date)
    
    def _merge_by_similarity(self, people: List[Person]) -> List[Event]:
        """
        Merge similar events using cosine similarity.
        
        Strategy:
        1. Collect all events from all people
        2. Group similar events together
        3. Merge each group into a single representative event
        4. Validate sequence follows domain rules
        """
        all_events = []
        for person in people:
            all_events.extend(person.events)
        
        if not all_events:
            return []
        
        # Sort by date
        all_events.sort(key=lambda e: e.date)
        
        # Group similar events
        event_groups = self._group_similar_events(all_events)
        
        # Merge each group into representative event
        merged_events = []
        for group in event_groups:
            merged_event = self._create_representative_event(group)
            merged_events.append(merged_event)
        
        # Validate and fix sequence
        merged_events = self._validate_and_fix_sequence(merged_events)
        
        return merged_events
    
    def _group_similar_events(self, events: List[Event], similarity_threshold: float = 0.6) -> List[List[Event]]:
        """
        Group similar events together.
        
        Uses greedy clustering: each event joins the first group where
        similarity to any member exceeds threshold.
        """
        groups = []
        
        for event in events:
            # Find best matching group
            best_group_idx = None
            best_similarity = 0.0
            
            for idx, group in enumerate(groups):
                # Check similarity to any member of the group
                for group_event in group:
                    sim = self.similarity_calculator.calculate_similarity(
                        event, group_event, self.domain
                    )
                    if sim.similarity > best_similarity:
                        best_similarity = sim.similarity
                        best_group_idx = idx
            
            # Add to group if similar enough, otherwise create new group
            if best_similarity >= similarity_threshold and best_group_idx is not None:
                groups[best_group_idx].append(event)
            else:
                groups.append([event])
        
        return groups
    
    def _create_representative_event(self, event_group: List[Event]) -> Event:
        """
        Create a single representative event from a group of similar events.
        
        Uses median/mode for aggregation.
        """
        if len(event_group) == 1:
            return event_group[0]
        
        # Use most common values
        event_types = [e.event_type for e in event_group]
        outcomes = [e.outcome for e in event_group]
        locations = [e.location for e in event_group]
        dates = [e.date for e in event_group]
        
        # Most common event type
        event_type = max(set(event_types), key=event_types.count)
        
        # Most common outcome
        outcome = max(set(outcomes), key=outcomes.count)
        
        # Most common location (or generalize if different)
        location = max(set(locations), key=locations.count) if locations else None
        if location and len(set(locations)) > len(event_group) / 2:
            # Too diverse, generalize
            filtered_locations = [loc for loc in locations if loc is not None]
            if filtered_locations:
                location = self._generalize_location(filtered_locations)
        
        # Median date
        dates_sorted = sorted(dates)
        median_date = dates_sorted[len(dates_sorted) // 2]
        
        # Merge details
        merged_data = {}
        for event in event_group:
            merged_data.update(event.details)
        
        return Event(
            event_id=f"merged_{event_group[0].event_id}",
            date=median_date,
            event_type=event_type,
            outcome=outcome,
            location=location,
            details={
                **merged_data,
                "_merged_count": len(event_group),
                "_merged_from": [e.event_id for e in event_group]
            }
        )
    
    def _generalize_location(self, locations: List[str]) -> str:
        """Generalize diverse locations to common area."""
        # Extract counties
        counties = set()
        for loc in locations:
            if "County" in loc:
                county = loc.split("County")[0].strip() + " County"
                counties.add(county)
        
        if len(counties) == 1:
            return list(counties)[0]
        
        # Extract states
        states = set()
        for loc in locations:
            parts = loc.split()
            if len(parts) >= 2:
                potential_state = parts[-1]
                if len(potential_state) == 2:  # State abbreviation
                    states.add(potential_state)
        
        if len(states) == 1:
            return list(states)[0]
        
        return "Multiple locations"
    
    def _validate_and_fix_sequence(self, events: List[Event]) -> List[Event]:
        """
        Validate event sequence follows domain rules and fix violations.
        
        Examples:
        - Can't have trial before arrest -> Insert missing arrest
        - Can't have admission without discharge -> Add discharge
        - Can't be hospitalized twice simultaneously -> Merge or add discharge
        """
        if not self.rules:
            return events  # No rules for this domain
        
        validated_events = []
        open_events = {}  # Track events requiring closure
        
        for event in events:
            rule = self.rules.get(event.event_type)
            
            if rule:
                # Check if required predecessor events exist
                if rule.must_follow:
                    missing_predecessors = []
                    for required_type in rule.must_follow:
                        if not any(e.event_type == required_type for e in validated_events):
                            missing_predecessors.append(required_type)
                    
                    # Insert missing predecessor events
                    for missing_type in missing_predecessors:
                        synthetic_event = self._create_synthetic_event(
                            missing_type,
                            before_date=event.date,
                            reason=f"Required before {event.event_type}"
                        )
                        validated_events.append(synthetic_event)
                
                # Check if this closes an open event
                if event.event_type in [v for v in open_events.values()]:
                    # Close the open event
                    for open_type, closure_type in list(open_events.items()):
                        if closure_type == event.event_type:
                            del open_events[open_type]
                            break
                
                # Check if this requires closure
                if rule.requires_closure and rule.closure_event_type:
                    if rule.event_type in open_events:
                        # Already have an open event of this type
                        # Need to close it first
                        closure_event = self._create_synthetic_event(
                            rule.closure_event_type,
                            before_date=event.date,
                            reason=f"Closing previous {rule.event_type}"
                        )
                        validated_events.append(closure_event)
                    
                    # Mark this event as open
                    open_events[rule.event_type] = rule.closure_event_type
            
            validated_events.append(event)
        
        # Close any remaining open events
        for open_type, closure_type in open_events.items():
            last_date = validated_events[-1].date if validated_events else datetime.now()
            closure_event = self._create_synthetic_event(
                closure_type,
                after_date=last_date,
                reason=f"Closing open {open_type}"
            )
            validated_events.append(closure_event)
        
        return sorted(validated_events, key=lambda e: e.date)
    
    def _create_synthetic_event(self, event_type: str, 
                                before_date: Optional[datetime] = None,
                                after_date: Optional[datetime] = None,
                                reason: str = "") -> Event:
        """Create a synthetic event to maintain logical sequence."""
        if before_date:
            date = before_date - timedelta(days=30)  # 1 month before
        elif after_date:
            date = after_date + timedelta(days=30)  # 1 month after
        else:
            date = datetime.now()
        
        return Event(
            event_id=f"synthetic_{event_type}_{date.strftime('%Y%m%d')}",
            date=date,
            event_type=event_type,
            outcome="unknown",
            location="Unknown",
            details={
                "_synthetic": True,
                "_reason": reason
            }
        )
    
    def _aggregate_events(self, people: List[Person]) -> List[Event]:
        """Create composite/aggregate events."""
        # Group events by type
        events_by_type = defaultdict(list)
        for person in people:
            for event in person.events:
                events_by_type[event.event_type].append(event)
        
        # Create aggregate events
        aggregated = []
        for event_type, events in events_by_type.items():
            if len(events) == 1:
                aggregated.append(events[0])
            else:
                # Create aggregate
                dates = sorted([e.date for e in events])
                date_range = f"{dates[0].strftime('%Y-%m')} to {dates[-1].strftime('%Y-%m')}"
                
                aggregate = Event(
                    event_id=f"aggregate_{event_type}",
                    date=dates[0],  # Start date
                    event_type=event_type,
                    outcome="multiple",
                    location=f"{len(set(e.location for e in events if e.location))} locations",
                    details={
                        "_aggregate": True,
                        "_count": len(events),
                        "_date_range": date_range,
                        "_outcomes": list(set(e.outcome for e in events if e.outcome))
                    }
                )
                aggregated.append(aggregate)
        
        return sorted(aggregated, key=lambda e: e.date)
    
    def _sample_events(self, people: List[Person], max_events: int = 10) -> List[Event]:
        """Sample representative events (avoid too many)."""
        all_events = []
        for person in people:
            all_events.extend(person.events)
        
        if len(all_events) <= max_events:
            return sorted(all_events, key=lambda e: e.date)
        
        # Sample diverse events
        # Strategy: Keep first, last, and evenly spaced middle events
        sorted_events = sorted(all_events, key=lambda e: e.date)
        
        sampled = [sorted_events[0]]  # First
        
        # Middle events
        step = len(sorted_events) // (max_events - 1)
        for i in range(step, len(sorted_events) - 1, step):
            sampled.append(sorted_events[i])
        
        sampled.append(sorted_events[-1])  # Last
        
        return sorted(sampled, key=lambda e: e.date)
    
    def _rule_based_merge(self, people: List[Person]) -> List[Event]:
        """Merge using strict domain rules."""
        # Combine similarity and rule validation
        merged = self._merge_by_similarity(people)
        validated = self._validate_and_fix_sequence(merged)
        return validated
