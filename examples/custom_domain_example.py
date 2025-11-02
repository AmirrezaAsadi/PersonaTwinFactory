"""
Example: Custom Domain Configuration

This example shows how to use PersonaTwin with a custom domain
that's not pre-configured (e.g., retail customer behavior).
"""

import personatwin as pt
from datetime import datetime, timedelta
import random


def generate_retail_data(n_customers=75):
    """Generate synthetic retail customer data."""
    customers = []
    
    genders = ["Male", "Female", "Other"]
    states = ["California", "Texas", "New York", "Florida"]
    event_types = ["purchase", "return", "review", "inquiry", "complaint", "reward_earned"]
    outcomes = ["completed", "pending", "refunded", "resolved", "escalated"]
    
    for i in range(n_customers):
        demographics = pt.Demographics(
            age=random.randint(18, 75),
            gender=random.choice(genders),
            geography=random.choice(states),
            socioeconomic_indicators={
                "income_bracket": random.choice(["low", "medium", "high"]),
                "loyalty_tier": random.choice(["bronze", "silver", "gold"])
            }
        )
        
        # Generate 1-15 retail events per customer
        events = []
        n_events = random.randint(1, 15)
        base_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        for j in range(n_events):
            event = pt.Event(
                event_id=f"R{i}_{j}",
                date=base_date + timedelta(days=j*7),
                event_type=random.choice(event_types),
                outcome=random.choice(outcomes),
                location=f"Store, {demographics.geography}",
                category="retail",
                details={
                    "amount": random.randint(10, 500),
                    "product_category": random.choice(["electronics", "clothing", "home", "food"])
                }
            )
            events.append(event)
        
        customer = pt.Person(
            person_id=f"CUST{i:04d}",
            demographics=demographics,
            events=events
        )
        customers.append(customer)
    
    return customers


def main():
    print("=" * 70)
    print("PersonaTwin Example: Custom Domain (Retail)")
    print("=" * 70)
    
    # Step 1: Define custom domain configuration
    print("\n🔧 Defining custom domain configuration...")
    
    retail_config = pt.create_custom_config(
        event_types=[
            "purchase", "return", "review", "inquiry", 
            "complaint", "reward_earned", "subscription"
        ],
        outcomes=[
            "completed", "pending", "refunded", "resolved", 
            "escalated", "cancelled"
        ],
        sensitive_fields={
            "customer_id", "email", "phone", "credit_card",
            "exact_purchase_amount", "specific_products"
        },
        preserve_fields={
            "product_category", "price_range", "loyalty_tier",
            "purchase_frequency", "satisfaction_rating"
        },
        temporal_precision="week",  # Weekly granularity
        geographic_precision="state"  # State-level only
    )
    
    print("✅ Custom retail domain configured")
    print(f"   Event types: {len(retail_config.event_types)}")
    print(f"   Outcomes: {len(retail_config.outcomes)}")
    print(f"   Temporal precision: {retail_config.temporal_precision}")
    print(f"   Geographic precision: {retail_config.geographic_precision}")
    
    # Step 2: Generate sample retail data
    print("\n🛒 Generating sample retail customer data...")
    customers = generate_retail_data(n_customers=75)
    print(f"Created {len(customers)} customers with transaction events")
    
    # Step 3: Generate personas
    print(f"\n{'='*70}")
    print("Generating Privacy-Protected Customer Personas")
    print(f"{'='*70}")
    
    result = pt.create_safe_personas(
        data=customers,
        privacy_level="medium",
        domain="custom",
        domain_config=retail_config,
        target_risk=0.05  # 5% risk for analytics
    )
    
    # Display results
    print(f"\n✅ Generated {len(result.personas)} customer personas")
    print(f"🔒 Population risk: {result.risk_metrics.population_average_risk:.3%}")
    print(f"📊 K-anonymity: {result.risk_metrics.k_anonymity}")
    print(f"🎯 Risk level: {result.risk_metrics.get_risk_level()}")
    print(f"🔄 Processing iterations: {result.iterations}")
    
    # Check if safe for analytics
    if result.is_safe_for_research():
        print(f"\n✅ SAFE FOR CUSTOMER ANALYTICS")
    
    # Export results
    pt.export_personas(result.personas, "examples/retail_personas.csv")
    pt.export_privacy_report(result, "examples/retail_privacy_report.html")
    
    print(f"\n📁 Exported to examples/retail_personas.csv")
    print(f"📁 Privacy report: examples/retail_privacy_report.html")
    
    # Step 4: Analyze preserved patterns
    print(f"\n{'='*70}")
    print("Utility Preservation for Customer Analytics")
    print(f"{'='*70}")
    
    personas_df = pt.personas_to_dataframe(result.personas)
    events_df = pt.personas_to_event_dataframe(result.personas)
    
    print(f"\n📊 Customer demographics (preserved):")
    print(f"   Gender distribution: {personas_df['gender'].value_counts().to_dict()}")
    print(f"   Geographic distribution: {personas_df['geography'].value_counts().to_dict()}")
    
    print(f"\n📊 Transaction patterns (preserved):")
    print(f"   Event types: {events_df['event_type'].value_counts().to_dict()}")
    
    print(f"\n📊 Average events per persona: {events_df.groupby('persona_id').size().mean():.1f}")
    
    print(f"\n✅ Custom domain example complete!")
    print(f"Demonstrates PersonaTwin's flexibility for ANY people-events domain.")
    print(f"\n💡 You can use this pattern for:")
    print(f"   - E-commerce behavior")
    print(f"   - Financial transactions")
    print(f"   - Social media interactions")
    print(f"   - App usage patterns")
    print(f"   - Any custom domain you define!")


if __name__ == "__main__":
    main()
