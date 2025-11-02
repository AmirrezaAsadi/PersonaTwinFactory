"""
Example: Healthcare Data Privacy Protection

This example demonstrates how to use PersonaTwin with healthcare data
(patient visits, diagnoses, treatments) while protecting patient privacy.
"""

import personatwin as pt
from datetime import datetime, timedelta
import random


def generate_sample_healthcare_data(n_patients=50):
    """Generate synthetic healthcare data for demonstration."""
    patients = []
    
    genders = ["Male", "Female"]
    ethnicities = ["White", "Black", "Hispanic", "Asian", "Other"]
    cities = ["Columbus", "Cincinnati", "Cleveland", "Toledo"]
    event_types = ["admission", "visit", "diagnosis", "treatment", "discharge", "follow_up"]
    outcomes = ["recovered", "improved", "stable", "ongoing", "readmitted"]
    conditions = ["diabetes", "hypertension", "asthma", "depression", "covid-19"]
    
    for i in range(n_patients):
        demographics = pt.Demographics(
            age=random.randint(25, 80),
            gender=random.choice(genders),
            ethnicity=random.choice(ethnicities),
            geography=random.choice(cities),
        )
        
        # Generate 2-10 healthcare events per patient
        events = []
        n_events = random.randint(2, 10)
        base_date = datetime.now() - timedelta(days=random.randint(0, 730))  # Last 2 years
        
        for j in range(n_events):
            event = pt.Event(
                event_id=f"H{i}_{j}",
                date=base_date + timedelta(days=j*15),
                event_type=random.choice(event_types),
                outcome=random.choice(outcomes),
                location=f"Hospital, {demographics.geography}",
                category="healthcare",
                severity=random.choice(["low", "medium", "high"]),
                details={"condition": random.choice(conditions)}
            )
            events.append(event)
        
        patient = pt.Person(
            person_id=f"PAT{i:04d}",
            demographics=demographics,
            events=events
        )
        patients.append(patient)
    
    return patients


def main():
    print("=" * 70)
    print("PersonaTwin Example: Healthcare Data")
    print("=" * 70)
    
    # Step 1: Generate sample data
    print("\n🏥 Generating sample healthcare data...")
    patients = generate_sample_healthcare_data(n_patients=50)
    print(f"Created {len(patients)} patients with healthcare events")
    
    # Step 2: Generate personas with high privacy
    print(f"\n{'='*70}")
    print("Generating Privacy-Protected Healthcare Personas")
    print(f"{'='*70}")
    
    result = pt.create_safe_personas(
        data=patients,
        privacy_level="high",
        domain="healthcare",
        target_risk=0.01  # 1% risk - HIPAA compliance
    )
    
    # Display results
    print(f"\n✅ Generated {len(result.personas)} personas")
    print(f"🔒 Population risk: {result.risk_metrics.population_average_risk:.3%}")
    print(f"📊 K-anonymity: {result.risk_metrics.k_anonymity}")
    print(f"🎯 Risk level: {result.risk_metrics.get_risk_level()}")
    print(f"💡 {result.message}")
    
    # HIPAA compliance check
    if result.risk_metrics.population_average_risk <= 0.01:
        print(f"\n✅ MEETS HIPAA-LEVEL PRIVACY REQUIREMENTS")
    
    # Export results
    pt.export_personas(result.personas, "examples/healthcare_personas.csv")
    pt.export_privacy_report(result, "examples/healthcare_privacy_report.html")
    
    print(f"\n📁 Exported to examples/healthcare_personas.csv")
    print(f"📁 Privacy report: examples/healthcare_privacy_report.html")
    
    # Step 3: Analyze utility preservation
    print(f"\n{'='*70}")
    print("Utility Preservation for Healthcare Research")
    print(f"{'='*70}")
    
    personas_df = pt.personas_to_dataframe(result.personas)
    events_df = pt.personas_to_event_dataframe(result.personas)
    
    print(f"\n📊 Age distribution:")
    print(personas_df['age_range'].value_counts())
    
    print(f"\n📊 Common event types:")
    print(events_df['event_type'].value_counts().head())
    
    print(f"\n📊 Outcomes distribution:")
    print(events_df['outcome'].value_counts())
    
    print(f"\n✅ Healthcare example complete!")
    print(f"Data can be shared for research while protecting patient privacy.")


if __name__ == "__main__":
    main()
