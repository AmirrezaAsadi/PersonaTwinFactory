"""
Example: Criminal Justice Data Privacy Protection

This example demonstrates how to use PersonaTwin to generate privacy-protected
personas from criminal justice data while preserving bias analysis capabilities.
"""

import personatwin as pt
from datetime import datetime, timedelta
import random

# Generate sample criminal justice data
def generate_sample_data(n_people=100):
    """Generate synthetic criminal justice data for demonstration."""
    people = []
    
    genders = ["Male", "Female"]
    ethnicities = ["White", "Black", "Hispanic", "Asian", "Other"]
    counties = ["Hamilton County", "Franklin County", "Cuyahoga County"]
    event_types = ["arrest", "charge", "trial", "sentencing", "probation", "release"]
    outcomes = ["guilty", "not_guilty", "dismissed", "plea_bargain", "completed"]
    
    for i in range(n_people):
        demographics = pt.Demographics(
            age=random.randint(18, 65),
            gender=random.choice(genders),
            ethnicity=random.choice(ethnicities),
            geography=random.choice(counties),
        )
        
        # Generate 1-5 events per person
        events = []
        n_events = random.randint(1, 5)
        base_date = datetime.now() - timedelta(days=random.randint(0, 365*3))
        
        for j in range(n_events):
            event = pt.Event(
                event_id=f"E{i}_{j}",
                date=base_date + timedelta(days=j*30),
                event_type=random.choice(event_types),
                outcome=random.choice(outcomes),
                location=f"Court Building, {demographics.geography}",
                category="criminal_justice",
            )
            events.append(event)
        
        person = pt.Person(
            person_id=f"P{i:04d}",
            demographics=demographics,
            events=events
        )
        people.append(person)
    
    return people


def main():
    print("=" * 70)
    print("PersonaTwin Example: Criminal Justice Data")
    print("=" * 70)
    
    # Step 1: Generate sample data
    print("\n📊 Generating sample criminal justice data...")
    people = generate_sample_data(n_people=100)
    print(f"Created {len(people)} people with events")
    
    # Step 2: Generate personas with different privacy levels
    privacy_levels = ["medium", "high"]
    
    for privacy_level in privacy_levels:
        print(f"\n{'='*70}")
        print(f"Testing {privacy_level.upper()} privacy level")
        print(f"{'='*70}")
        
        result = pt.create_safe_personas(
            data=people,
            privacy_level=privacy_level,
            domain="criminal_justice",
            target_risk=0.05  # 5% risk for research use
        )
        
        # Display results
        print(f"\n✅ Generated {len(result.personas)} personas")
        print(f"🔒 Population risk: {result.risk_metrics.population_average_risk:.3%}")
        print(f"📊 K-anonymity: {result.risk_metrics.k_anonymity}")
        print(f"🎯 Risk level: {result.risk_metrics.get_risk_level()}")
        print(f"🔄 Processing iterations: {result.iterations}")
        print(f"💡 Recommendation: {result.risk_metrics.recommendation}")
        
        # Check safety
        if result.is_safe_for_research():
            print(f"\n✅ SAFE FOR RESEARCH USE")
        if result.is_safe_for_public():
            print(f"✅ SAFE FOR PUBLIC RELEASE")
        
        # Export results
        output_prefix = f"criminal_justice_{privacy_level}"
        pt.export_personas(result.personas, f"examples/{output_prefix}_personas.csv")
        pt.export_privacy_report(result, f"examples/{output_prefix}_report.html")
        print(f"\n📁 Exported to examples/{output_prefix}_personas.csv")
        print(f"📁 Privacy report: examples/{output_prefix}_report.html")
    
    # Step 3: Demonstrate utility preservation
    print(f"\n{'='*70}")
    print("Utility Preservation Analysis")
    print(f"{'='*70}")
    
    # Convert to DataFrames for analysis
    result = pt.create_safe_personas(
        data=people,
        privacy_level="medium",
        domain="criminal_justice"
    )
    
    personas_df = pt.personas_to_dataframe(result.personas)
    events_df = pt.personas_to_event_dataframe(result.personas)
    
    print(f"\n📊 Persona-level statistics:")
    print(personas_df[['gender', 'ethnicity', 'event_count']].describe())
    
    print(f"\n📊 Event-level statistics:")
    print(events_df['event_type'].value_counts())
    
    print(f"\n✅ Example complete!")
    print(f"PersonaTwin successfully generated privacy-safe criminal justice personas.")


if __name__ == "__main__":
    main()
