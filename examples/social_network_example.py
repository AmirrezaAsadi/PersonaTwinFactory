"""
Example: Social Networks in PersonaTwin

Demonstrates how to:
1. Include explicit social connections from your data
2. Infer connections from patterns
3. Use external network structures
4. Preserve privacy while maintaining network properties
"""

import personatwin as pt
from personatwin.social_network import (
    SocialNetworkBuilder,
    SocialNetworkAnalyzer,
    add_social_network,
    ConnectionType,
    ConnectionStrength
)
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
random.seed(42)


def create_sample_data_with_connections():
    """Create sample criminal justice data with social connections."""
    people = []
    
    # Create family groups
    families = []
    for family_id in range(10):
        family_size = random.randint(2, 4)
        family = []
        
        for member_id in range(family_size):
            person_id = f"person_{len(people)}"
            
            person = pt.Person(
                person_id=person_id,
                demographics=pt.Demographics(
                    age=random.randint(18, 65),
                    gender=random.choice(["Male", "Female"]),
                    ethnicity=random.choice(["White", "Black", "Hispanic", "Asian"]),
                    geography=f"County_{family_id % 5}"  # Families in same county
                ),
                events=[],
                connections=[],  # Will populate later
                social_circle_ids=[f"family_{family_id}"]
            )
            
            # Add some events
            num_events = random.randint(1, 3)
            for _ in range(num_events):
                event = pt.Event(
                    event_id=f"event_{person_id}_{_}",
                    date=datetime.now() - timedelta(days=random.randint(0, 365)),
                    event_type=random.choice(["arrest", "trial", "sentencing", "probation_check"]),
                    outcome=random.choice(["guilty", "not_guilty", "dismissed", "plea_bargain"]),
                    location=f"Court_{family_id % 3}"
                )
                person.events.append(event)
            
            family.append(person)
            people.append(person)
        
        families.append(family)
    
    # Add family connections
    for family in families:
        for i, person1 in enumerate(family):
            for person2 in family[i+1:]:
                person1.connections.append(person2.person_id)
                person2.connections.append(person1.person_id)
    
    # Add co-defendant connections (shared events)
    # Randomly create groups who share events
    for _ in range(5):
        group_size = random.randint(2, 4)
        group = random.sample(people, min(group_size, len(people)))
        
        # Add shared event
        shared_event_date = datetime.now() - timedelta(days=random.randint(0, 365))
        shared_location = f"Court_{random.randint(0, 2)}"
        
        for person in group:
            event = pt.Event(
                event_id=f"shared_event_{_}_{person.person_id}",
                date=shared_event_date,
                event_type="arrest",
                outcome="guilty",
                location=shared_location,
                associated_people=[p.person_id for p in group if p != person]
            )
            person.events.append(event)
            
            # Add connections
            for other in group:
                if other != person and other.person_id not in person.connections:
                    person.connections.append(other.person_id)
    
    print(f"Created {len(people)} people in {len(families)} families")
    print(f"Total explicit connections: {sum(len(p.connections) for p in people) // 2}")
    
    return people


def main():
    print("=" * 80)
    print("PersonaTwin Social Network Example")
    print("=" * 80)
    print()
    
    # Step 1: Create sample data with social connections
    print("Step 1: Creating sample data with family and co-defendant connections...")
    people = create_sample_data_with_connections()
    print()
    
    # Step 2: Extract connections from data
    print("Step 2: Building social network from explicit connections...")
    builder = SocialNetworkBuilder(
        preserve_strong_connections=True,
        use_external_patterns=True
    )
    
    # Extract explicit connections
    explicit_connections = builder.extract_connections(people)
    print(f"  Extracted {len(explicit_connections)} explicit connections")
    
    # Show connection types
    connection_types = {}
    for conn in explicit_connections:
        conn_type = conn.connection_type.value
        connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
    
    print("  Connection type breakdown:")
    for conn_type, count in connection_types.items():
        print(f"    {conn_type}: {count}")
    print()
    
    # Step 3: Add realistic network patterns
    print("Step 3: Adding realistic small-world network pattern...")
    pattern_connections = builder.integrate_external_network_patterns(
        people,
        pattern_source="small_world"
    )
    print(f"  Added {len(pattern_connections)} inferred connections")
    print()
    
    all_connections = explicit_connections + pattern_connections
    
    # Step 4: Analyze network properties
    print("Step 4: Analyzing network properties...")
    analyzer = SocialNetworkAnalyzer()
    metrics = analyzer.calculate_network_metrics(all_connections)
    
    print(f"  Network Statistics:")
    print(f"    Nodes (people): {metrics['num_nodes']}")
    print(f"    Edges (connections): {metrics['num_edges']}")
    print(f"    Average degree: {metrics['average_degree']:.2f}")
    print(f"    Network density: {metrics['density']:.4f}")
    print(f"    Clustering coefficient: {metrics['clustering_coefficient']:.4f}")
    print(f"    Largest component: {metrics['largest_component_size']} people")
    print(f"    Number of components: {metrics['num_components']}")
    print()
    
    # Step 5: Detect social circles
    print("Step 5: Detecting social circles (communities)...")
    circles = builder.detect_social_circles(people, all_connections)
    print(f"  Found {len(circles)} social circles")
    print(f"  Circle sizes: {[circle.size for circle in circles[:10]]}")
    print()
    
    # Step 6: Generate privacy-protected personas
    print("Step 6: Generating privacy-protected personas...")
    result = pt.create_safe_personas(
        data=people,
        privacy_level="high",
        domain="criminal_justice",
        target_risk=0.05,
        use_census_data=True
    )
    
    print(f"  Generated {len(result.personas)} personas from {len(people)} people")
    print(f"  Average k-anonymity: {result.risk_metrics.k_anonymity}")
    print(f"  Population risk: {result.risk_metrics.population_average_risk:.2%}")
    print()
    
    # Step 7: Anonymize social network for personas
    print("Step 7: Anonymizing social network for personas...")
    
    # Add merged_person_ids to personas for mapping
    person_to_persona_map = {}
    for persona in result.personas:
        # In real implementation, this would be tracked during merging
        # For demo, we'll create a simplified mapping
        sample_size = persona.merged_from
        if sample_size <= len(people):
            sampled_people = random.sample(people, sample_size)
            persona.merged_person_ids = [p.person_id for p in sampled_people]
            for person_id in persona.merged_person_ids:
                person_to_persona_map[person_id] = persona.persona_id
    
    # Anonymize network
    anonymized_connections = builder.anonymize_network(
        all_connections,
        result.personas,
        preserve_structure=True
    )
    
    print(f"  Original connections: {len(all_connections)}")
    print(f"  Anonymized connections: {len(anonymized_connections)}")
    print(f"  Reduction: {(1 - len(anonymized_connections)/len(all_connections))*100:.1f}%")
    print()
    
    # Step 8: Analyze anonymized network
    print("Step 8: Analyzing anonymized network...")
    anon_metrics = analyzer.calculate_network_metrics(anonymized_connections)
    
    print(f"  Anonymized Network Statistics:")
    print(f"    Nodes (personas): {anon_metrics['num_nodes']}")
    print(f"    Edges (connections): {anon_metrics['num_edges']}")
    print(f"    Average degree: {anon_metrics['average_degree']:.2f}")
    print(f"    Network density: {anon_metrics['density']:.4f}")
    print(f"    Clustering coefficient: {anon_metrics['clustering_coefficient']:.4f}")
    print()
    
    # Step 9: Assess privacy risks from network
    print("Step 9: Assessing privacy risks from network structure...")
    network_risk = analyzer.assess_privacy_risk_from_network(
        anonymized_connections,
        result.personas
    )
    
    print(f"  Network Privacy Risks:")
    print(f"    Hub risk (identifiable hubs): {network_risk['network_hub_risk']:.2%}")
    print(f"    Isolation risk (small groups): {network_risk['network_isolation_risk']:.2%}")
    print(f"    Density risk: {network_risk['network_density_risk']:.2%}")
    print(f"    Overall network risk: {network_risk['overall_network_risk']:.2%}")
    print()
    
    # Step 10: Add connection info to personas
    print("Step 10: Updating personas with network information...")
    persona_connections = {}
    for conn in anonymized_connections:
        if conn.person1_id not in persona_connections:
            persona_connections[conn.person1_id] = []
        if conn.person2_id not in persona_connections:
            persona_connections[conn.person2_id] = []
        
        persona_connections[conn.person1_id].append(conn.person2_id)
        persona_connections[conn.person2_id].append(conn.person1_id)
    
    for persona in result.personas:
        persona.connections = persona_connections.get(persona.persona_id, [])
        persona.connection_count = len(persona.connections)
    
    # Show sample persona with connections
    if result.personas:
        sample = result.personas[0]
        print(f"  Sample Persona: {sample.persona_id}")
        print(f"    Merged from: {sample.merged_from} people")
        print(f"    Demographics: {sample.demographics.age_range}, "
              f"{sample.demographics.gender}, {sample.demographics.geography}")
        print(f"    Connections: {sample.connection_count} other personas")
        if sample.connections:
            print(f"    Connected to: {sample.connections[:5]}...")
        print()
    
    # Step 11: Export with network data
    print("Step 11: Exporting personas with social network...")
    
    # Export personas
    pt.export_personas(result.personas, "personas_with_network.csv")
    
    # Export network connections separately
    import pandas as pd
    connections_df = pd.DataFrame([
        {
            "persona1": conn.person1_id,
            "persona2": conn.person2_id,
            "type": conn.connection_type.value,
            "strength": conn.strength.value,
            "confidence": conn.confidence
        }
        for conn in anonymized_connections
    ])
    connections_df.to_csv("persona_connections.csv", index=False)
    
    print("  Exported:")
    print("    - personas_with_network.csv (persona data)")
    print("    - persona_connections.csv (network edges)")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY: Social Network Integration")
    print("=" * 80)
    print()
    print("Key Features:")
    print("✅ Extracted explicit connections from data (family, co-defendants)")
    print("✅ Inferred connections from patterns (neighbors, colleagues)")
    print("✅ Added realistic network structure (small-world pattern)")
    print("✅ Preserved privacy while maintaining network properties")
    print("✅ Assessed network-specific privacy risks")
    print()
    print("Privacy Protection:")
    print(f"  • K-anonymity: {result.risk_metrics.k_anonymity}")
    print(f"  • Population risk: {result.risk_metrics.population_average_risk:.2%}")
    print(f"  • Network risk: {network_risk['overall_network_risk']:.2%}")
    print(f"  • Connection reduction: {(1 - len(anonymized_connections)/len(all_connections))*100:.1f}%")
    print()
    print("Network preserved the following properties:")
    print(f"  • Average connections per person: {anon_metrics['average_degree']:.1f}")
    print(f"  • Community structure: {anon_metrics['clustering_coefficient']:.2f}")
    print(f"  • Connected groups: {anon_metrics['num_components']}")
    print()
    print("You can now share:")
    print("  1. personas_with_network.csv - Safe persona data")
    print("  2. persona_connections.csv - Anonymized social network")
    print()
    print("For research on social factors without compromising privacy! 🎯")


if __name__ == "__main__":
    main()
