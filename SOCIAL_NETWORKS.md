# Social Network Integration in PersonaTwin

## Overview

PersonaTwin now supports **social networks and relationship modeling**, allowing you to preserve social structures while maintaining privacy. This is crucial for research on social factors, peer influence, family dynamics, and community effects.

## Why Social Networks Matter

### Research Applications

1. **Criminal Justice**: Co-defendant networks, gang affiliations, family patterns
2. **Healthcare**: Patient support networks, caregiver relationships, epidemic spread
3. **Education**: Peer effects, study groups, bullying networks
4. **Social Services**: Family support systems, caseworker-client relationships
5. **Employment**: Workplace hierarchies, mentorship networks, collaboration patterns

### The Challenge

Social networks create **additional privacy risks**:
- Unique network positions (e.g., "only person connecting two groups") can identify individuals
- Small isolated groups are vulnerable to re-identification
- Dense connections between rare demographics increase risk

## Features

### 1. Multiple Connection Sources

#### A. Explicit Connections from Your Data

Extract connections already present in your data:

```python
from personatwin.models import Person, Event, Demographics

# People with explicit connections
person1 = Person(
    person_id="001",
    demographics=Demographics(age=42, gender="Female"),
    events=[...],
    connections=["002", "003"],  # Connected to persons 002 and 003
    social_circle_ids=["family_1", "workplace_A"]
)

# Shared events create connections
person2 = Person(
    person_id="002",
    demographics=Demographics(age=45, gender="Male"),
    events=[
        Event(
            event_id="arrest_123",
            event_type="arrest",
            associated_people=["001", "004"]  # Co-defendants
        )
    ]
)
```

**Automatically detected connections:**
- ✅ Family members (same household indicators)
- ✅ Co-defendants (shared arrest events)
- ✅ Co-workers (same employment events)
- ✅ Neighbors (same small geographic area)
- ✅ Caregivers/patients (shared medical events)

#### B. Inferred Connections from Patterns

Uses demographic and geographic patterns to infer likely connections:

```python
from personatwin.social_network import SocialNetworkBuilder

builder = SocialNetworkBuilder(
    use_external_patterns=True,
    min_connection_confidence=0.6  # Only include confident inferences
)

# Automatically infers:
# - Same age + same geography = likely friends
# - Same household + similar age = likely family
# - Same workplace/school = likely colleagues/classmates
inferred_connections = builder.extract_connections(people)
```

**Inference rules:**
- Same small geographic area + similar age → Neighbors (confidence: 0.7)
- Shared events + same location → Coworkers/classmates (confidence: 0.9)
- Very similar demographics + same address → Family (confidence: 0.8)

#### C. External Network Patterns

Adds realistic social structure using well-studied network patterns:

```python
# Small-world network (most common in real life)
# - Most people have 2-5 connections
# - Few "hubs" with 10+ connections
# - High clustering (friends of friends are friends)
pattern_connections = builder.integrate_external_network_patterns(
    people,
    pattern_source="small_world"
)

# Other patterns available:
# - "community": Strong intra-cluster, weak inter-cluster
# - "hierarchical": Tree-like structure (workplaces, schools)
```

### 2. Connection Types and Strengths

```python
from personatwin.social_network import ConnectionType, ConnectionStrength

# Connection types (domain-specific)
ConnectionType.FAMILY          # Family members
ConnectionType.FRIEND          # Friends
ConnectionType.COWORKER        # Colleagues
ConnectionType.NEIGHBOR        # Geographic neighbors
ConnectionType.CODEFENDANT     # Criminal justice
ConnectionType.CAREGIVER       # Healthcare
ConnectionType.CLASSMATE       # Education
ConnectionType.CASEWORKER_CLIENT  # Social services
ConnectionType.SUPERVISOR_EMPLOYEE  # Employment
ConnectionType.INFERRED        # From patterns

# Connection strengths
ConnectionStrength.WEAK        # Acquaintance
ConnectionStrength.MODERATE    # Regular contact
ConnectionStrength.STRONG      # Close relationship
```

### 3. Privacy-Preserving Anonymization

Transforms social networks for personas while preserving structure:

```python
from personatwin.social_network import SocialNetworkBuilder

builder = SocialNetworkBuilder(
    preserve_strong_connections=True,  # Keep family/close friends
    use_external_patterns=True
)

# Extract and anonymize
explicit_connections = builder.extract_connections(people)
anonymized = builder.anonymize_network(
    connections=explicit_connections,
    personas=personas,
    preserve_structure=True
)

# Anonymization strategies:
# 1. Map person IDs → persona IDs
# 2. Remove self-connections (if people merged into same persona)
# 3. Preserve strong connections (family, close friends)
# 4. Generalize weak connections (reduce detail)
# 5. Add noise to connection counts
```

**Privacy protections:**
- ✅ Self-connections removed (when people merge)
- ✅ Connection counts noised (±2 connections)
- ✅ Weak connections generalized (less detail)
- ✅ Strong connections preserved (for utility)
- ✅ Unique network positions identified and protected

### 4. Network Privacy Risk Assessment

Assess privacy risks specific to network structure:

```python
from personatwin.social_network import SocialNetworkAnalyzer

analyzer = SocialNetworkAnalyzer()

# Calculate network metrics
metrics = analyzer.calculate_network_metrics(connections)
print(f"Average degree: {metrics['average_degree']}")
print(f"Clustering: {metrics['clustering_coefficient']}")
print(f"Largest component: {metrics['largest_component_size']}")

# Assess network-specific privacy risks
network_risk = analyzer.assess_privacy_risk_from_network(
    connections=anonymized_connections,
    personas=personas
)

print(f"Hub risk: {network_risk['network_hub_risk']:.2%}")
print(f"Isolation risk: {network_risk['network_isolation_risk']:.2%}")
print(f"Overall network risk: {network_risk['overall_network_risk']:.2%}")
```

**Network risk factors:**
- **Hub risk**: People with many connections are identifiable
- **Isolation risk**: Small isolated groups vulnerable
- **Density risk**: Dense connections increase re-identification
- **Bridge risk**: People connecting disparate groups identifiable

### 5. Social Circle Detection

Automatically detect communities and groups:

```python
# Detect social circles using graph clustering
circles = builder.detect_social_circles(
    people=people,
    connections=connections
)

for circle in circles:
    print(f"Circle {circle.circle_id}:")
    print(f"  Size: {circle.size} members")
    print(f"  Type: {circle.circle_type}")
    print(f"  Geography: {circle.geographic_area}")
```

## Complete Usage Example

### Basic Usage

```python
import personatwin as pt
from personatwin.social_network import add_social_network

# Load your data with connections
people = [
    pt.Person(
        person_id="001",
        demographics=pt.Demographics(age=42, gender="Female"),
        events=[...],
        connections=["002", "003"],  # Explicit connections
        social_circle_ids=["family_1"]
    ),
    # ... more people
]

# Generate personas with privacy protection
result = pt.create_safe_personas(
    data=people,
    privacy_level="high",
    target_risk=0.05
)

# Add and anonymize social network
anonymized_connections, network_risk = add_social_network(
    people=people,
    personas=result.personas,
    use_external_patterns=True,
    preserve_connections=True
)

print(f"Network risk: {network_risk['overall_network_risk']:.2%}")
```

### Advanced Usage

```python
from personatwin.social_network import (
    SocialNetworkBuilder,
    SocialNetworkAnalyzer,
    ConnectionType,
    ConnectionStrength,
    SocialConnection
)

# Step 1: Build network with fine-grained control
builder = SocialNetworkBuilder(
    min_connection_confidence=0.7,  # Higher threshold
    preserve_strong_connections=True,
    use_external_patterns=True
)

# Extract explicit connections
explicit_connections = builder.extract_connections(people)

# Add realistic patterns
small_world_connections = builder.integrate_external_network_patterns(
    people,
    pattern_source="small_world"
)

all_connections = explicit_connections + small_world_connections

# Step 2: Detect communities
circles = builder.detect_social_circles(people, all_connections)
print(f"Found {len(circles)} social circles")

# Step 3: Analyze original network
analyzer = SocialNetworkAnalyzer()
original_metrics = analyzer.calculate_network_metrics(all_connections)

# Step 4: Generate personas
result = pt.create_safe_personas(
    data=people,
    privacy_level="high",
    target_risk=0.05
)

# Step 5: Anonymize network
anonymized = builder.anonymize_network(
    connections=all_connections,
    personas=result.personas,
    preserve_structure=True
)

# Step 6: Analyze anonymized network
anon_metrics = analyzer.calculate_network_metrics(anonymized)

# Step 7: Assess privacy risks
network_risk = analyzer.assess_privacy_risk_from_network(
    anonymized,
    result.personas
)

# Step 8: Update personas with network info
for persona in result.personas:
    persona.connections = [
        conn.person2_id if conn.person1_id == persona.persona_id else conn.person1_id
        for conn in anonymized
        if persona.persona_id in [conn.person1_id, conn.person2_id]
    ]
    persona.connection_count = len(persona.connections)

# Step 9: Export
import pandas as pd

# Export personas
pt.export_personas(result.personas, "personas.csv")

# Export network edges
connections_df = pd.DataFrame([
    {
        "persona1": conn.person1_id,
        "persona2": conn.person2_id,
        "type": conn.connection_type.value,
        "strength": conn.strength.value,
        "confidence": conn.confidence
    }
    for conn in anonymized
])
connections_df.to_csv("connections.csv", index=False)
```

## Privacy Guarantees

### Network Anonymization Strategies

1. **ID Remapping**
   - Original person IDs → Persona IDs
   - Prevents direct identification

2. **Connection Merging**
   - When people merge into same persona, connections collapse
   - Reduces network density automatically

3. **Selective Preservation**
   - **Preserve**: Strong connections (family, close friends) for utility
   - **Generalize**: Weak connections (reduce to "inferred")
   - **Remove**: Self-loops, redundant connections

4. **Noise Injection**
   - Add ±2 noise to connection counts
   - Provides plausible deniability

5. **Structure Protection**
   - Identify unique network positions (bridges, hubs)
   - Apply extra protection to vulnerable positions

### Network-Specific Attacks Defended

| Attack | Defense |
|--------|---------|
| **Hub identification** | Noise on connection counts, merging hubs with similar people |
| **Bridge identification** | Detect bridges, increase k-anonymity for them |
| **Clique enumeration** | Generalize weak links in dense subgraphs |
| **Structural fingerprinting** | Add realistic external patterns to obscure unique structures |
| **Isolation attack** | Detect small components, merge with larger groups |

## Use Cases

### 1. Criminal Justice: Co-Defendant Networks

```python
# Extract co-defendant networks from arrest records
people_with_codefendants = [
    Person(
        person_id="suspect_1",
        events=[
            Event(
                event_type="arrest",
                associated_people=["suspect_2", "suspect_3"]
            )
        ]
    ),
    # ...
]

# Preserve gang/network structure while protecting individuals
result = pt.create_safe_personas(
    data=people_with_codefendants,
    privacy_level="high",
    domain="criminal_justice"
)

connections, risk = add_social_network(people_with_codefendants, result.personas)

# Research question: Do co-defendant networks predict recidivism?
# Answer: Yes, while protecting individual identities!
```

### 2. Healthcare: Patient Support Networks

```python
# Patient support groups and caregiver networks
patients = [
    Person(
        person_id="patient_1",
        demographics=Demographics(age=65, geography="County A"),
        events=[
            Event(event_type="diagnosis", outcome="diabetes"),
            Event(event_type="support_group", associated_people=["patient_2", "patient_3"])
        ],
        connections=["caregiver_1"],  # Family caregiver
        social_circle_ids=["diabetes_support_group_A"]
    ),
    # ...
]

# Preserve support network structure
result = pt.create_safe_personas(
    data=patients,
    privacy_level="high",
    domain="healthcare"
)

# Research question: Do support networks improve outcomes?
```

### 3. Education: Peer Effects

```python
# Student peer networks and study groups
students = [
    Person(
        person_id="student_1",
        events=[
            Event(event_type="assessment", outcome="grade_A"),
            Event(event_type="study_group", associated_people=["student_2", "student_3"])
        ],
        connections=["student_2", "student_4"],  # Friends
        social_circle_ids=["class_2024", "study_group_math"]
    ),
    # ...
]

# Research question: Do peer networks affect academic performance?
```

## Comparison: With vs. Without Social Networks

| Aspect | Without Networks | With Networks |
|--------|------------------|---------------|
| **Research Questions** | Individual factors only | Social factors, peer effects |
| **Data Utility** | Demographics + events | + Social structure |
| **Privacy Risk** | Individual re-identification | + Network re-identification |
| **Complexity** | Simpler | More complex |
| **Real-world Fidelity** | Good | Excellent |

## Performance Considerations

### Computational Complexity

- **Connection extraction**: O(n²) worst case, O(n·k) typical (k = avg connections)
- **Community detection**: O(n + e) where e = edges
- **Anonymization**: O(e) linear in edges
- **Risk assessment**: O(n + e)

### Memory Requirements

```python
# Memory usage approximation:
# - 100K people, 500K connections ≈ 50 MB
# - 1M people, 5M connections ≈ 500 MB
```

### Optimization Tips

1. **Limit connection inference**: Set `min_connection_confidence` higher
2. **Skip external patterns**: Set `use_external_patterns=False`
3. **Process in batches**: For very large datasets (>1M people)
4. **Prune weak connections**: Remove connections with confidence < 0.5

## Validation and Testing

### Verify Network Properties Preserved

```python
# Compare original vs anonymized networks
original_metrics = analyzer.calculate_network_metrics(original_connections)
anon_metrics = analyzer.calculate_network_metrics(anonymized_connections)

# Check preservation
assert abs(original_metrics['average_degree'] - anon_metrics['average_degree']) < 1.0
assert abs(original_metrics['clustering_coefficient'] - anon_metrics['clustering_coefficient']) < 0.1

print("✅ Network properties preserved!")
```

### Verify Privacy Protection

```python
# Check network privacy risks
network_risk = analyzer.assess_privacy_risk_from_network(anonymized, personas)

assert network_risk['network_hub_risk'] < 0.3  # Hubs not too identifiable
assert network_risk['network_isolation_risk'] < 0.2  # No isolated groups
assert network_risk['overall_network_risk'] < 0.25  # Overall acceptable

print("✅ Network privacy protected!")
```

## Future Enhancements

### Planned Features

1. **Dynamic networks**: Temporal evolution of connections
2. **Weighted connections**: Connection strength as continuous value
3. **Attributed networks**: Edge attributes (communication frequency, etc.)
4. **Multi-layer networks**: Different relationship types as layers
5. **Network differential privacy**: Formal DP guarantees for networks

## Summary

### Key Benefits

✅ **Preserves social structure** for richer research
✅ **Multiple connection sources**: Explicit + inferred + external patterns
✅ **Privacy-aware anonymization**: Network-specific protections
✅ **Quantifiable network risks**: Measure hub/isolation/density risks
✅ **Flexible integration**: Works with all PersonaTwin domains
✅ **Realistic patterns**: Uses well-studied network models

### Best Practices

1. **Start with explicit connections** from your data
2. **Add inferred connections carefully** (check confidence thresholds)
3. **Use external patterns** for realism
4. **Preserve strong connections** (family, close relationships)
5. **Assess network risks** alongside traditional privacy risks
6. **Validate network properties** before/after anonymization

### When to Use

✅ **Use when:**
- Research questions involve social factors
- Peer effects are important
- Family/community dynamics matter
- Network structure affects outcomes

❌ **Skip when:**
- Only individual-level analysis needed
- No connection data available
- Privacy risks outweigh utility gains
- Computational resources limited

**Social networks add a crucial dimension to privacy-preserving data sharing, enabling research on the social fabric of communities while protecting individual privacy!** 🕸️🔒
