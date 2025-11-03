"""
People merging strategies for privacy protection.

This module implements k-anonymity through merging similar people
into combined personas.
"""

from typing import List, Dict, Tuple
from collections import defaultdict
import uuid

from personatwin.models import Person, Persona, Demographics, EventPatterns, PrivacyMetadata
from personatwin.privacy import PrivacyLevel
from personatwin.event_merging import IntelligentEventMerger, EventMergingStrategy
from personatwin.domains import Domain


# Merging configuration
MERGING_CRITERIA = {
    "age_tolerance": 3,  # ±3 years
    "geography_level": "county",  # Same county required
    "gender_match": True,  # Must match
    "ethnicity_match": True,  # Must match
    "minimum_group_size": 5,  # At least 5 people per merged persona
    "maximum_group_size": 50,  # No more than 50 people per persona
}


class PeopleMerging:
    """
    Merge similar people to reduce uniqueness and improve k-anonymity.
    
    Groups people by demographics and combines their events into
    unified personas while preserving statistical patterns.
    """
    
    def __init__(
        self,
        privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM,
        min_group_size: int = 5,
        domain: Domain = Domain.CUSTOM,
        event_merging_strategy: EventMergingStrategy = EventMergingStrategy.SIMILARITY
    ):
        self.privacy_level = privacy_level
        self.min_group_size = min_group_size
        self.domain = domain
        self.criteria = self._get_merging_criteria()
        self.event_merger = IntelligentEventMerger(domain, event_merging_strategy)
    
    def _get_merging_criteria(self) -> Dict:
        """Get merging criteria based on privacy level."""
        base_criteria = MERGING_CRITERIA.copy()
        
        if self.privacy_level == PrivacyLevel.LOW:
            base_criteria["minimum_group_size"] = 3
            base_criteria["age_tolerance"] = 5
        elif self.privacy_level == PrivacyLevel.MEDIUM:
            base_criteria["minimum_group_size"] = 5
            base_criteria["age_tolerance"] = 3
        elif self.privacy_level == PrivacyLevel.HIGH:
            base_criteria["minimum_group_size"] = 10
            base_criteria["age_tolerance"] = 5
        else:  # MAXIMUM
            base_criteria["minimum_group_size"] = 20
            base_criteria["age_tolerance"] = 10
        
        return base_criteria
    
    def merge_similar_people(
        self,
        people: List[Person],
        similarity_threshold: float = 0.7
    ) -> List[Persona]:
        """
        Merge similar people into personas.
        
        Args:
            people: List of original people
            similarity_threshold: Minimum similarity to merge (0-1)
            
        Returns:
            List of merged personas
        """
        if not people:
            return []
        
        # Group people by similarity
        groups = self._group_by_similarity(people, similarity_threshold)
        
        # Create personas from groups
        personas = []
        for group in groups:
            persona = self._create_persona_from_group(group)
            personas.append(persona)
        
        return personas
    
    def _group_by_similarity(
        self,
        people: List[Person],
        threshold: float
    ) -> List[List[Person]]:
        """Group people by demographic similarity."""
        # Create demographic keys for grouping
        groups = defaultdict(list)
        
        for person in people:
            key = self._create_demographic_key(person.demographics)
            groups[key].append(person)
        
        # Ensure minimum group sizes
        final_groups = []
        small_groups = []
        
        for group in groups.values():
            if len(group) >= self.criteria["minimum_group_size"]:
                final_groups.append(group)
            else:
                small_groups.extend(group)
        
        # Merge small groups
        if small_groups:
            if len(small_groups) >= self.criteria["minimum_group_size"]:
                final_groups.append(small_groups)
            elif final_groups:
                # Add to closest existing group
                final_groups[0].extend(small_groups)
            else:
                # No choice but to keep small group
                final_groups.append(small_groups)
        
        return final_groups
    
    def _create_demographic_key(self, demographics: Demographics) -> str:
        """Create a key for grouping similar demographics."""
        # Age bin
        age = demographics.age or 30  # Default if missing
        age_bin = (age // self.criteria["age_tolerance"]) * self.criteria["age_tolerance"]
        
        # Geographic generalization
        geo = demographics.geography or "unknown"
        if "county" in self.criteria["geography_level"]:
            # Keep only county-level info
            geo = geo.split(",")[0] if "," in geo else geo
        
        # Create key
        key_parts = []
        
        if self.criteria["gender_match"]:
            key_parts.append(demographics.gender or "unknown")
        
        if self.criteria["ethnicity_match"]:
            key_parts.append(demographics.ethnicity or "unknown")
        
        key_parts.append(str(age_bin))
        key_parts.append(geo)
        
        return "|".join(key_parts)
    
    def _create_persona_from_group(self, group: List[Person]) -> Persona:
        """Create a persona by merging a group of people."""
        persona_id = str(uuid.uuid4())
        
        # Merge demographics
        demographics = self._merge_demographics([p.demographics for p in group])
        
        # Use intelligent event merging instead of naive concatenation
        merged_events = self.event_merger.merge_events(group)
        
        # Extract event patterns
        event_patterns = self._extract_event_patterns(merged_events)
        
        # Create privacy metadata
        privacy_metadata = PrivacyMetadata(
            traceability_score=1.0 / len(group),  # Lower with more merging
            noise_level=0.0,  # No noise yet
            merge_count=len(group),
            generation_method="demographic_merging"
        )
        
        return Persona(
            persona_id=persona_id,
            merged_from=len(group),
            demographics=demographics,
            event_patterns=event_patterns,
            privacy_metadata=privacy_metadata,
            events=merged_events,
            merged_person_ids=[p.person_id for p in group]
        )
    
    def _merge_demographics(self, demographics_list: List[Demographics]) -> Demographics:
        """Merge demographics from multiple people."""
        if not demographics_list:
            return Demographics()
        
        # Take most common values
        genders = [d.gender for d in demographics_list if d.gender]
        ethnicities = [d.ethnicity for d in demographics_list if d.ethnicity]
        geographies = [d.geography for d in demographics_list if d.geography]
        ages = [d.age for d in demographics_list if d.age]
        
        merged = Demographics(
            gender=max(set(genders), key=genders.count) if genders else None,
            ethnicity=max(set(ethnicities), key=ethnicities.count) if ethnicities else None,
            geography=max(set(geographies), key=geographies.count) if geographies else None,
            age=int(sum(ages) / len(ages)) if ages else None,
            confidence_level=1.0 / len(demographics_list)  # Decreases with merging
        )
        
        # Create age range
        if ages:
            merged.age_range = merged.generalize_age()
        
        return merged
    
    def _extract_event_patterns(self, events: List) -> EventPatterns:
        """Extract statistical patterns from events."""
        if not events:
            return EventPatterns()
        
        # Extract event types (now always strings)
        event_types = [str(e.event_type) for e in events if hasattr(e, 'event_type')]
        
        # Calculate outcome distributions
        outcomes = [str(e.outcome) if hasattr(e, 'outcome') and e.outcome else "unknown" for e in events]
        outcome_dist = {}
        for outcome in set(outcomes):
            outcome_dist[outcome] = outcomes.count(outcome) / len(outcomes)
        
        # Temporal patterns (simplified)
        temporal_patterns = {
            "total_events": len(events),
            "event_density": len(events) / max(1, len(set(e.date.year for e in events if hasattr(e, 'date') and e.date)))
        }
        
        # Recidivism indicators (simplified)
        recidivism = {
            "repeat_events": len(events) > 1,
            "event_count": len(events)
        }
        
        return EventPatterns(
            event_types=list(set(event_types)),
            temporal_patterns=temporal_patterns,
            outcome_distributions=outcome_dist,
            recidivism_indicators=recidivism
        )
    
    def calculate_similarity(self, person1: Person, person2: Person) -> float:
        """
        Calculate similarity between two people.
        
        Returns:
            Similarity score (0-1, higher = more similar)
        """
        score = 0.0
        total_weight = 0.0
        
        demo1 = person1.demographics
        demo2 = person2.demographics
        
        # Age similarity (weight: 0.2)
        if demo1.age is not None and demo2.age is not None:
            age_diff = abs(demo1.age - demo2.age)
            age_sim = max(0, 1 - age_diff / 20)  # Normalize by 20 years
            score += age_sim * 0.2
            total_weight += 0.2
        
        # Gender match (weight: 0.3)
        if demo1.gender and demo2.gender:
            if demo1.gender == demo2.gender:
                score += 0.3
            total_weight += 0.3
        
        # Ethnicity match (weight: 0.3)
        if demo1.ethnicity and demo2.ethnicity:
            if demo1.ethnicity == demo2.ethnicity:
                score += 0.3
            total_weight += 0.3
        
        # Geography proximity (weight: 0.2)
        if demo1.geography and demo2.geography:
            if demo1.geography == demo2.geography:
                score += 0.2
            elif self._same_county(demo1.geography, demo2.geography):
                score += 0.1
            total_weight += 0.2
        
        # Normalize by total weight
        if total_weight > 0:
            return score / total_weight
        return 0.0
    
    def _same_county(self, geo1: str, geo2: str) -> bool:
        """Check if two geographies are in the same county."""
        # Simplified: check if they share a common prefix
        parts1 = geo1.split(",")
        parts2 = geo2.split(",")
        
        if len(parts1) > 0 and len(parts2) > 0:
            return parts1[0].strip().lower() == parts2[0].strip().lower()
        
        return False
