"""
Example demonstrating intelligent event merging in PersonaTwin PrivacyForge.

Shows how PersonaTwin creates realistic personas by intelligently merging
events using similarity and domain-specific rules.
"""

from personatwin.models import Person, Event, Demographics
from personatwin.merging import PeopleMerging
from personatwin.privacy import PrivacyLevel
from personatwin.event_merging import EventMergingStrategy
from personatwin.domains import Domain
from datetime import datetime, timedelta


def create_sample_healthcare_data():
    """Create sample healthcare data with logical sequences."""
    people = []
    
    # Patient 1: Complete admission-discharge cycle
    people.append(Person(
        person_id="P001",
        demographics=Demographics(age=65, gender="Female", ethnicity="White", geography="Hamilton County OH"),
        events=[
            Event("E1", datetime(2023, 1, 10), "admission", "admitted", {"facility": "Memorial Hospital"}, "Memorial Hospital"),
            Event("E2", datetime(2023, 1, 12), "diagnosis", "pneumonia", {"severity": "moderate"}, "Memorial Hospital"),
            Event("E3", datetime(2023, 1, 15), "treatment", "antibiotics", {"drug": "azithromycin"}, "Memorial Hospital"),
            Event("E4", datetime(2023, 1, 20), "discharge", "recovered", {"status": "stable"}, "Memorial Hospital"),
        ]
    ))
    
    # Patient 2: Similar admission-discharge (should merge with P001)
    people.append(Person(
        person_id="P002",
        demographics=Demographics(age=67, gender="Female", ethnicity="White", geography="Hamilton County OH"),
        events=[
            Event("E5", datetime(2023, 1, 15), "admission", "admitted", {"facility": "Memorial Hospital"}, "Memorial Hospital"),
            Event("E6", datetime(2023, 1, 17), "diagnosis", "pneumonia", {"severity": "mild"}, "Memorial Hospital"),
            Event("E7", datetime(2023, 1, 22), "treatment", "antibiotics", {"drug": "amoxicillin"}, "Memorial Hospital"),
            Event("E8", datetime(2023, 1, 28), "discharge", "recovered", {"status": "stable"}, "Memorial Hospital"),
        ]
    ))
    
    # Patient 3: Missing discharge (should be auto-added)
    people.append(Person(
        person_id="P003",
        demographics=Demographics(age=66, gender="Female", ethnicity="White", geography="Hamilton County OH"),
        events=[
            Event("E9", datetime(2023, 2, 5), "admission", "admitted", {"facility": "Memorial Hospital"}, "Memorial Hospital"),
            Event("E10", datetime(2023, 2, 7), "diagnosis", "heart_attack", {"severity": "severe"}, "Memorial Hospital"),
            Event("E11", datetime(2023, 2, 10), "surgery", "stent_placement", {"type": "cardiac"}, "Memorial Hospital"),
            # Missing discharge!
        ]
    ))
    
    return people


def create_sample_criminal_justice_data():
    """Create sample criminal justice data."""
    people = []
    
    # Person 1: Complete arrest-trial-sentencing
    people.append(Person(
        person_id="D001",
        demographics=Demographics(age=28, gender="Male", ethnicity="Black", geography="Hamilton County OH"),
        events=[
            Event("E1", datetime(2022, 3, 15), "arrest", "arrested", {"charge": "possession"}, "Cincinnati PD"),
            Event("E2", datetime(2022, 5, 10), "charge", "filed", {"type": "misdemeanor"}, "Hamilton County Court"),
            Event("E3", datetime(2022, 8, 20), "trial", "guilty", {"plea": "guilty"}, "Hamilton County Court"),
            Event("E4", datetime(2022, 9, 15), "sentencing", "probation", {"duration": "12 months"}, "Hamilton County Court"),
        ]
    ))
    
    # Person 2: Similar case (should merge)
    people.append(Person(
        person_id="D002",
        demographics=Demographics(age=29, gender="Male", ethnicity="Black", geography="Hamilton County OH"),
        events=[
            Event("E5", datetime(2022, 4, 1), "arrest", "arrested", {"charge": "possession"}, "Cincinnati PD"),
            Event("E6", datetime(2022, 6, 5), "charge", "filed", {"type": "misdemeanor"}, "Hamilton County Court"),
            Event("E7", datetime(2022, 9, 10), "trial", "guilty", {"plea": "no_contest"}, "Hamilton County Court"),
            Event("E8", datetime(2022, 10, 5), "sentencing", "probation", {"duration": "18 months"}, "Hamilton County Court"),
        ]
    ))
    
    # Person 3: Missing arrest (should be auto-added)
    people.append(Person(
        person_id="D003",
        demographics=Demographics(age=30, gender="Male", ethnicity="Black", geography="Hamilton County OH"),
        events=[
            # Missing arrest!
            Event("E9", datetime(2022, 7, 1), "trial", "not_guilty", {"plea": "not_guilty"}, "Hamilton County Court"),
        ]
    ))
    
    return people


def demonstrate_healthcare_merging():
    """Demonstrate healthcare event merging with different strategies."""
    
    print("=" * 80)
    print("HEALTHCARE: INTELLIGENT EVENT MERGING DEMONSTRATION")
    print("=" * 80)
    
    people = create_sample_healthcare_data()
    
    print(f"\nOriginal Data: {len(people)} patients")
    for person in people:
        print(f"\n  {person.person_id} (Age: {person.demographics.age}):")
        for event in person.events:
            print(f"    {event.date.strftime('%Y-%m-%d')}: {event.event_type} -> {event.outcome}")
    
    # Strategy 1: Similarity-based merging (RECOMMENDED)
    print("\n" + "-" * 80)
    print("STRATEGY 1: SIMILARITY-BASED MERGING (Recommended)")
    print("-" * 80)
    
    merger1 = PeopleMerging(
        privacy_level=PrivacyLevel.MEDIUM,
        min_group_size=3,
        domain=Domain.HEALTHCARE,
        event_merging_strategy=EventMergingStrategy.SIMILARITY
    )
    
    personas1 = merger1.merge_similar_people(people)
    
    print(f"\nResult: {len(personas1)} personas created")
    for persona in personas1:
        print(f"\n  Persona {persona.persona_id[:8]}... (merged from {persona.merged_from} people):")
        print(f"    Demographics: Age {persona.demographics.age}, {persona.demographics.gender}, {persona.demographics.geography}")
        print(f"    Events: {len(persona.events)}")
        for event in persona.events:
            synthetic_marker = " 🔧 [SYNTHETIC]" if event.details.get("_synthetic") else ""
            merged_marker = f" 📊 [MERGED FROM {event.details.get('_merged_count', 1)}]" if "_merged_count" in event.details else ""
            print(f"      {event.date.strftime('%Y-%m-%d')}: {event.event_type} -> {event.outcome}{synthetic_marker}{merged_marker}")
            if event.details.get("_reason"):
                print(f"        Reason: {event.details['_reason']}")
    
    # Strategy 2: Rule-based merging
    print("\n" + "-" * 80)
    print("STRATEGY 2: RULE-BASED MERGING (Validates Sequences)")
    print("-" * 80)
    
    merger2 = PeopleMerging(
        privacy_level=PrivacyLevel.MEDIUM,
        min_group_size=3,
        domain=Domain.HEALTHCARE,
        event_merging_strategy=EventMergingStrategy.RULE_BASED
    )
    
    personas2 = merger2.merge_similar_people(people)
    
    print(f"\nResult: {len(personas2)} personas created")
    for persona in personas2:
        print(f"\n  Persona {persona.persona_id[:8]}... (merged from {persona.merged_from} people):")
        print(f"    Events: {len(persona.events)}")
        for event in persona.events:
            if event.details.get("_synthetic"):
                reason = event.details.get("_reason", "")
                print(f"      {event.date.strftime('%Y-%m-%d')}: {event.event_type} ✨ [AUTO-ADDED: {reason}]")
            else:
                print(f"      {event.date.strftime('%Y-%m-%d')}: {event.event_type} -> {event.outcome}")
    
    # Strategy 3: Aggregate merging
    print("\n" + "-" * 80)
    print("STRATEGY 3: AGGREGATE MERGING (Combines Similar Events)")
    print("-" * 80)
    
    merger3 = PeopleMerging(
        privacy_level=PrivacyLevel.MEDIUM,
        min_group_size=3,
        domain=Domain.HEALTHCARE,
        event_merging_strategy=EventMergingStrategy.AGGREGATE
    )
    
    personas3 = merger3.merge_similar_people(people)
    
    print(f"\nResult: {len(personas3)} personas created")
    for persona in personas3:
        print(f"\n  Persona {persona.persona_id[:8]}... (merged from {persona.merged_from} people):")
        for event in persona.events:
            if event.details.get("_aggregate"):
                count = event.details.get("_count", 1)
                date_range = event.details.get("_date_range", "")
                print(f"      {event.event_type}: {count} occurrences ({date_range})")
            else:
                print(f"      {event.date.strftime('%Y-%m-%d')}: {event.event_type}")


def demonstrate_criminal_justice_merging():
    """Demonstrate criminal justice event merging."""
    
    print("\n\n" + "=" * 80)
    print("CRIMINAL JUSTICE: RULE-BASED EVENT VALIDATION")
    print("=" * 80)
    
    people = create_sample_criminal_justice_data()
    
    print(f"\nOriginal Data: {len(people)} defendants")
    for person in people:
        print(f"\n  {person.person_id}:")
        for event in person.events:
            print(f"    {event.date.strftime('%Y-%m-%d')}: {event.event_type}")
    
    # Use rule-based merging to fix missing events
    merger = PeopleMerging(
        privacy_level=PrivacyLevel.MEDIUM,
        min_group_size=3,
        domain=Domain.CRIMINAL_JUSTICE,
        event_merging_strategy=EventMergingStrategy.RULE_BASED
    )
    
    personas = merger.merge_similar_people(people)
    
    print(f"\n\nResult: {len(personas)} personas created")
    for persona in personas:
        print(f"\n  Persona {persona.persona_id[:8]}... (merged from {persona.merged_from} people):")
        print(f"    Demographics: Age {persona.demographics.age}, {persona.demographics.gender}")
        print(f"    Event Sequence:")
        for event in persona.events:
            if event.details.get("_synthetic"):
                reason = event.details.get("_reason", "")
                print(f"      {event.date.strftime('%Y-%m-%d')}: {event.event_type} ✨ [ADDED: {reason}]")
            else:
                print(f"      {event.date.strftime('%Y-%m-%d')}: {event.event_type} -> {event.outcome}")


def print_summary():
    """Print summary of intelligent event merging."""
    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS: INTELLIGENT EVENT MERGING")
    print("=" * 80)
    print("""
1. ✅ SIMILARITY-BASED MERGING (Recommended)
   - Merges similar events (same type, date, outcome, location)
   - Creates realistic personas by combining similar experiences
   - Uses cosine similarity (threshold: 0.6)
   - Example: 3 "pneumonia admissions" in Jan 2023 → 1 representative admission

2. ✅ RULE-BASED MERGING (Validates Logic)
   - Ensures domain-specific rules are followed
   - Healthcare: Can't be hospitalized twice without discharge
   - Criminal Justice: Can't have trial before arrest
   - Automatically inserts missing prerequisite events

3. ✅ AGGREGATE MERGING (Reduces Event Count)
   - Combines multiple occurrences into composite events
   - Example: 5 arrests → "5 arrests between 2020-2023"
   - Useful when personas have too many events

4. 🚨 PROBLEM SOLVED: Naive Concatenation
   - OLD: Just concatenated all events → unrealistic sequences
   - NEW: Intelligent merging → logical, realistic personas

5. 🔧 SYNTHETIC EVENTS (When Needed)
   - Automatically added to maintain logical sequences
   - Clearly marked with "_synthetic": True
   - Example: Adding discharge after open admission
   - Example: Adding arrest before trial

RECOMMENDATION:
- Use SIMILARITY or RULE_BASED for most cases
- Use AGGREGATE when dealing with high-frequency events
- Synthetic events are minimal and clearly documented
    """)


if __name__ == "__main__":
    demonstrate_healthcare_merging()
    demonstrate_criminal_justice_merging()
    print_summary()
