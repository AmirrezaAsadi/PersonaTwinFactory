"""
Example: Census-Enhanced Privacy Assessment

This example demonstrates how PersonaTwin uses publicly available census data
to improve privacy risk assessment without requiring you to provide any data.

The system automatically:
1. Downloads census data from public sources (US Census Bureau API)
2. Caches data locally for future use
3. Uses fallback synthetic data if API is unavailable
4. Calculates demographic rarity based on real population data
5. Provides census-informed privacy recommendations
"""

import personatwin as pt
from datetime import datetime, timedelta
import random

print("=" * 70)
print("Census-Enhanced Privacy Assessment Example")
print("=" * 70)

# Create sample criminal justice data
print("\n1. Creating sample data with diverse demographics...")

people = []
for i in range(100):
    # Create diverse demographic combinations
    person = pt.Person(
        person_id=f"person_{i}",
        demographics=pt.Demographics(
            age=random.randint(18, 75),
            gender=random.choice(["Male", "Female"]),
            ethnicity=random.choice(["White", "Black", "Hispanic", "Asian"]),
            geography=random.choice([
                "Hamilton County, OH",
                "Los Angeles County, CA",
                "Cook County, IL",
            ])
        )
    )
    
    # Add some events
    for j in range(random.randint(1, 5)):
        person.events.append(pt.Event(
            event_id=f"event_{i}_{j}",
            event_type="arrest",
            date=datetime.now() - timedelta(days=random.randint(0, 1000)),
            outcome=random.choice(["charge_filed", "warning", "dismissed"]),
            location="City Court",
        ))
    
    people.append(person)

print(f"Created {len(people)} people with events")

# Generate personas WITH census-enhanced privacy (default)
print("\n2. Generating personas WITH census-enhanced privacy...")
print("   (Using public census data for better risk assessment)")

result_with_census = pt.create_safe_personas(
    data=people,
    privacy_level="high",
    domain="criminal_justice",
    target_risk=0.01,
    use_census_data=True  # Enable census-enhanced privacy
)

print(f"\nResults with census enhancement:")
print(f"  - Generated {len(result_with_census.personas)} personas")
print(f"  - Population risk: {result_with_census.risk_metrics.population_average_risk:.4f}")
print(f"  - Risk level: {result_with_census.risk_metrics.get_risk_level()}")
print(f"  - Safe for public: {result_with_census.is_safe_for_public()}")
print(f"  - Iterations: {result_with_census.iterations}")

# Check for census-specific warnings
if "CENSUS:" in result_with_census.risk_metrics.recommendation:
    census_part = result_with_census.risk_metrics.recommendation.split("CENSUS:")[1]
    print(f"\n  Census insights: {census_part.strip()}")

# Generate personas WITHOUT census enhancement (basic heuristics only)
print("\n3. Generating personas WITHOUT census enhancement...")
print("   (Using only basic heuristics)")

result_without_census = pt.create_safe_personas(
    data=people,
    privacy_level="high",
    domain="criminal_justice",
    target_risk=0.01,
    use_census_data=False  # Disable census enhancement
)

print(f"\nResults without census enhancement:")
print(f"  - Generated {len(result_without_census.personas)} personas")
print(f"  - Population risk: {result_without_census.risk_metrics.population_average_risk:.4f}")
print(f"  - Risk level: {result_without_census.risk_metrics.get_risk_level()}")
print(f"  - Safe for public: {result_without_census.is_safe_for_public()}")
print(f"  - Iterations: {result_without_census.iterations}")

# Compare results
print("\n4. Comparison:")
print("=" * 70)
print(f"{'Metric':<40} {'With Census':<15} {'Without Census':<15}")
print("-" * 70)
print(f"{'Population Risk':<40} {result_with_census.risk_metrics.population_average_risk:<15.4f} {result_without_census.risk_metrics.population_average_risk:<15.4f}")
print(f"{'High Risk Personas':<40} {len(result_with_census.risk_metrics.high_risk_personas):<15} {len(result_without_census.risk_metrics.high_risk_personas):<15}")
print(f"{'K-anonymity':<40} {result_with_census.risk_metrics.k_anonymity:<15} {result_without_census.risk_metrics.k_anonymity:<15}")
print(f"{'External Linkage Risk':<40} {result_with_census.risk_metrics.external_linkage_risk:<15.4f} {result_without_census.risk_metrics.external_linkage_risk:<15.4f}")
print(f"{'Iterations Required':<40} {result_with_census.iterations:<15} {result_without_census.iterations:<15}")

# Detailed census analysis
print("\n5. Census Data Source:")
print("=" * 70)
print("""
PersonaTwin uses the following public data sources:

1. US Census Bureau API (primary)
   - Free, no authentication required
   - Provides real demographic distributions
   - Updated regularly

2. Cached Local Data (secondary)
   - Saves API calls and improves performance
   - Stored in ~/.personatwin/census_cache

3. Bundled Synthetic Data (fallback)
   - US national averages
   - Used when API is unavailable
   - Conservative estimates for safety

Benefits of census-enhanced privacy:
- Detects truly rare demographic combinations
- More accurate external linkage risk
- Better protection for vulnerable populations
- Realistic privacy guarantees
""")

# Export results
print("\n6. Exporting results...")
df = pt.personas_to_dataframe(result_with_census.personas)
print(f"\nExported {len(df)} personas with {df['event_count'].sum():.0f} total events")
print("\nSample personas:")
print(df[['persona_id', 'merged_from', 'age_range', 'gender', 'geography', 'event_count']].head())

print("\n" + "=" * 70)
print("Census-enhanced privacy assessment complete!")
print("=" * 70)

print("\nKey Takeaways:")
print("1. Census data is fetched automatically from public sources")
print("2. No manual data collection or API keys required")
print("3. Census enhancement provides more accurate privacy assessment")
print("4. System works offline with bundled fallback data")
print("5. All census data is cached locally for performance")
