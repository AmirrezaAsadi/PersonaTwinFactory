# External Datasets Integration for PersonaTwin

## Executive Summary

**Question**: Should PersonaTwin use external datasets to add synthetic social connections based on demographic patterns?

**Answer**: **YES! This protects against connection pattern re-identification.**

---

## The Problem: Connection Pattern Re-identification

**Scenario**: People can be identified by their connections' attributes

```python
# Example: Criminal justice data
Person A: Connected to "father with criminal record"
Person B: Connected to "father with criminal record"  
Person C: Connected to "spouse who is a teacher"

# Risk: Person C is unique!
# Adversary searches: "Who is connected to a teacher?"
# Only Person C matches → IDENTIFIED
```

## The Solution: Add Synthetic Connections with Similar Attributes

Add fake connections that match demographic patterns from external datasets:

```python
# Original data:
Person C: Connected to "spouse who is a teacher" (UNIQUE!)

# Add synthetic connections from demographic patterns:
Person X: Connected to "spouse who is a teacher" (SYNTHETIC)
Person Y: Connected to "spouse who is a teacher" (SYNTHETIC)
Person Z: Connected to "spouse who is a teacher" (SYNTHETIC)

# Result: Now k=4 for this connection pattern
# Person C no longer unique!
```

### How It Works

```python
# Step 1: Extract real connection patterns
Real connections:
- Person A → father (age 60, criminal record)
- Person B → father (age 65, criminal record)
- Person C → spouse (age 40, teacher)

# Step 2: Find rare connection patterns
Rare pattern: "Connected to teacher" (only Person C)

# Step 3: Use external dataset to add synthetic connections
External demographic dataset provides:
- Typical connection patterns by demographics
- "People age 35-45 often connected to teachers"

# Step 4: Add synthetic connections matching rare patterns
Add synthetic connections:
- Persona X → spouse (age 38, teacher) [SYNTHETIC]
- Persona Y → spouse (age 42, teacher) [SYNTHETIC]

# Result: Connection pattern k-anonymity achieved!
```

---

## Why This Is Different from Network Structure

### Network Structure (Already Implemented)

```python
# Current system adds connections for graph structure:
Person A: 5 connections (random people)
Person B: 3 connections (random people)

# Goal: Make network look realistic
```

### Connection Attributes (NEW - This Feature)

```python
# NEW: Add connections based on WHAT the connected people are:
Person A: Connected to "father with criminal record"
Person B: Connected to "father with criminal record"

# Goal: Make connection PATTERNS less identifying
```

---

## What External Datasets Are Needed?

### Demographic Connection Pattern Datasets

To add synthetic connections intelligently, we need datasets that show:
- **Who connects to whom** based on demographics
- **Connection patterns** by age, occupation, relationship type

### Option 1: US Census Social Characteristics Data

**Source**: US Census Bureau (already integrated!)

**Provides**:
- Household composition patterns
- Family relationship statistics
- Age distributions within households

**Use**: Generate synthetic family connections matching real demographics

### Option 2: NVIDIA Nemotron (Limited Use)

[NVIDIA Nemotron-CC](https://arxiv.org/abs/2406.11704) contains synthetic personas with:
- Demographics (age, occupation, etc.)
- Can be analyzed for connection patterns

**Use**: Extract demographic patterns (e.g., "40-year-olds often connected to teachers")

**Note**: Use only for pattern extraction, not direct persona addition

### Option 3: Sociological Research Data

**Source**: Academic studies on social connections

**Provides**:
- Homophily patterns (similar people connect)
- Relationship type distributions
- Demographic connection probabilities

**Use**: Build realistic connection pattern templates

---

## Data Sources for Connection Patterns

### Already Available

#### 1. **US Census Social Characteristics** ⭐⭐⭐
- **Source**: US Census Bureau API (already integrated)
- **Data**: Household relationships, family composition
- **Use**: Generate realistic family connection patterns

#### 2. **Census Demographic Distributions** ⭐⭐
- **Source**: PersonaTwin's existing census integration
- **Data**: Age, occupation, geographic distributions
- **Use**: Match synthetic connections to realistic demographics

### External Sources (Optional)

#### 3. **Sociological Pattern Templates**
- **Source**: Academic literature on social networks
- **Data**: Homophily patterns, connection probabilities
- **Use**: Build realistic connection templates

#### 4. **Domain-Specific Patterns**
- **Criminal Justice**: Co-defendant relationship patterns
- **Healthcare**: Caregiver relationship statistics
- **Education**: Student-teacher connection patterns

---

## Architectural Integration

### Option 1: Connection Pattern Analyzer (Recommended) ⭐

```python
# personatwin/connection_patterns.py (NEW MODULE)

from typing import List, Dict, Tuple
from collections import defaultdict
from personatwin.models import Person, Persona
from personatwin.social_network import SocialConnection

class ConnectionPatternAnalyzer:
    """
    Analyzes connection patterns to find rare/unique combinations
    that could lead to re-identification.
    """
    
    def find_rare_connection_patterns(
        self,
        personas: List[Persona],
        connections: List[SocialConnection],
        threshold: int = 5
    ) -> List[Dict]:
        """
        Find connection patterns with k < threshold.
        
        Returns patterns like:
        - "Connected to person age 60-65 with criminal record"
        - "Connected to teacher age 35-45"
        """
        patterns = defaultdict(list)
        
        for conn in connections:
            # Get connected persona's attributes
            connected_persona = self._get_persona(conn.person2_id, personas)
            
            # Create pattern signature
            pattern = self._create_pattern_signature(
                connection_type=conn.connection_type,
                connected_demographics=connected_persona.demographics,
                connected_events=connected_persona.events
            )
            
            patterns[pattern].append(conn.person1_id)
        
        # Find rare patterns
        rare_patterns = []
        for pattern, persona_ids in patterns.items():
            if len(set(persona_ids)) < threshold:
                rare_patterns.append({
                    'pattern': pattern,
                    'count': len(set(persona_ids)),
                    'personas': list(set(persona_ids))
                })
        
        return rare_patterns
    
    def _create_pattern_signature(
        self,
        connection_type: str,
        connected_demographics: Demographics,
        connected_events: List
    ) -> str:
        """
        Create a pattern signature from connection attributes.
        
        Example: "FAMILY_Male_60-65_CriminalRecord"
        """
        age_bucket = f"{(connected_demographics.age // 5) * 5}-{((connected_demographics.age // 5) * 5) + 5}"
        
        has_criminal_record = any('criminal' in str(e.category).lower() for e in connected_events)
        
        signature = f"{connection_type}_{connected_demographics.gender}_{age_bucket}"
        if has_criminal_record:
            signature += "_CriminalRecord"
        
        return signature


class SyntheticConnectionGenerator:
    """
    Generates synthetic connections to increase k-anonymity
    for rare connection patterns.
    """
    
    def __init__(self, census_data_provider=None):
        self.census = census_data_provider
    
    def generate_synthetic_connections(
        self,
        rare_patterns: List[Dict],
        personas: List[Persona],
        target_k: int = 10
    ) -> List[SocialConnection]:
        """
        Generate synthetic connections matching rare patterns
        to increase k-anonymity.
        """
        synthetic_connections = []
        
        for pattern_info in rare_patterns:
            pattern = pattern_info['pattern']
            current_k = pattern_info['count']
            needed = target_k - current_k
            
            if needed <= 0:
                continue
            
            # Generate synthetic connections matching this pattern
            for _ in range(needed):
                # Select a random persona that doesn't have this pattern
                source_persona = self._select_persona_without_pattern(
                    personas, pattern, pattern_info['personas']
                )
                
                # Create synthetic connected persona matching pattern
                target_attributes = self._parse_pattern(pattern)
                
                # Find or create target persona with matching attributes
                target_persona = self._find_matching_persona(
                    personas, target_attributes
                )
                
                # Create synthetic connection
                synthetic_conn = SocialConnection(
                    person1_id=source_persona.persona_id,
                    person2_id=target_persona.persona_id,
                    connection_type=target_attributes['connection_type'],
                    strength="WEAK",
                    context="Synthetic (privacy protection)",
                    confidence=0.5
                )
                
                synthetic_connections.append(synthetic_conn)
        
        return synthetic_connections
    """
    Abstract interface for synthetic persona providers.
    
    Provides synthetic people to augment real data and
    increase anonymity through demographic diversity.
    """
    
    @abstractmethod
    def get_synthetic_personas(
        self,
        count: int,
        zipcodes: Optional[List[str]] = None,
        demographic_distribution: Optional[Dict] = None
    ) -> List[Person]:
        """
        Generate or retrieve synthetic personas.
        
        Args:
            count: Number of synthetic personas to generate
            zipcodes: Filter to specific zipcodes (optional)
            demographic_distribution: Match demographics to this distribution
        
        Returns:
            List of synthetic Person objects
        """
        pass


class NemotronProvider(SyntheticPersonaProvider):
    """Provider for NVIDIA Nemotron synthetic personas."""
    
    def __init__(self, cache_dir: str = "~/.personatwin/nemotron_cache"):
        self.cache_dir = cache_dir
        self.dataset_url = "https://huggingface.co/datasets/nvidia/Nemotron-CC"
        self._personas = None  # Lazy load
    
    def get_synthetic_personas(
        self,
        count: int,
        zipcodes: Optional[List[str]] = None,
        demographic_distribution: Optional[Dict] = None
    ) -> List[Person]:
        """
        Get synthetic personas from Nemotron dataset.
        
        Filters and samples from the 20,000+ Nemotron personas
        to match requested criteria.
        """
        # Load dataset if not cached
        if self._personas is None:
            self._personas = self._load_or_download_nemotron()
        
        # Filter by zipcode if requested
        if zipcodes:
            filtered = [p for p in self._personas 
                       if p.demographics.geography in zipcodes]
        else:
            filtered = self._personas
        
        # Match demographic distribution if provided
        if demographic_distribution:
            filtered = self._match_demographics(filtered, demographic_distribution)
        
        # Sample requested count
        import random
        selected = random.sample(filtered, min(count, len(filtered)))
        
        # Mark as synthetic
        for person in selected:
            person.is_synthetic = True  # Add flag
        
        return selected
    
    def _load_or_download_nemotron(self) -> List[Person]:
        """Download and parse Nemotron dataset."""
        # Check cache first
        cache_path = f"{self.cache_dir}/nemotron_personas.pkl"
        if os.path.exists(cache_path):
            return pickle.load(open(cache_path, 'rb'))
        
        # Download from HuggingFace
        dataset = self._download_from_huggingface()
        
        # Convert to Person objects
        personas = []
        for row in dataset:
            person = Person(
                person_id=f"synthetic_{row['id']}",
                demographics=Demographics(
                    age=row['age'],
                    gender=row['gender'],
                    ethnicity=row['ethnicity'],
                    geography=row['zipcode']
                ),
                events=[],  # No events for synthetic personas
                is_synthetic=True
            )
            personas.append(person)
        
        # Cache for future use
        os.makedirs(self.cache_dir, exist_ok=True)
        pickle.dump(personas, open(cache_path, 'wb'))
        
        return personas


class CensusSyntheticProvider(SyntheticPersonaProvider):
    """Generate synthetic personas from Census distributions."""
    
    def __init__(self):
        from personatwin.census import CensusDataProvider
        self.census = CensusDataProvider()
    
    def get_synthetic_personas(
        self,
        count: int,
        zipcodes: Optional[List[str]] = None,
        demographic_distribution: Optional[Dict] = None
    ) -> List[Person]:
        """
        Generate synthetic personas from Census data.
        
        Samples demographics based on real Census distributions
        for the specified geography.
        """
        personas = []
        
        for i in range(count):
            # Sample demographics from Census distribution
            demographics = self._sample_from_census(zipcodes)
            
            person = Person(
                person_id=f"census_synthetic_{i}",
                demographics=demographics,
                events=[],
                is_synthetic=True
            )
            personas.append(person)
        
        return personas
```

### Option 2: Augmentation Helper Functions

```python
# personatwin/augmentation.py (NEW MODULE)

def augment_with_synthetic(
    real_people: List[Person],
    synthetic_provider: SyntheticPersonaProvider,
    strategy: str = "match_distribution",
    synthetic_ratio: float = 2.0
) -> List[Person]:
    """
    Augment real people with synthetic personas for increased privacy.
    
    Args:
        real_people: Original people from your dataset
        synthetic_provider: Provider for synthetic personas
        strategy: How to select synthetics ("match_distribution", "fill_gaps", "boost_rare")
        synthetic_ratio: Ratio of synthetic to real (2.0 = 2x synthetic)
    
    Returns:
        Combined list of real + synthetic people
    """
    synthetic_count = int(len(real_people) * synthetic_ratio)
    
    if strategy == "match_distribution":
        # Add synthetics matching real demographic distribution
        distribution = _calculate_demographic_distribution(real_people)
        synthetic_people = synthetic_provider.get_synthetic_personas(
            count=synthetic_count,
            demographic_distribution=distribution
        )
    
    elif strategy == "fill_gaps":
        # Add synthetics for missing geographic areas
        existing_zips = _get_unique_zipcodes(real_people)
        all_zips = _get_all_zipcodes_in_region(existing_zips)
        missing_zips = set(all_zips) - set(existing_zips)
        
        synthetic_people = synthetic_provider.get_synthetic_personas(
            count=synthetic_count,
            zipcodes=list(missing_zips)
        )
    
    elif strategy == "boost_rare":
        # Find rare demographic groups and add synthetics
        rare_groups = _find_rare_demographics(real_people, threshold=5)
        synthetic_people = []
        
        for group in rare_groups:
            # Add synthetics matching this rare group
            group_synthetics = synthetic_provider.get_synthetic_personas(
                count=20,  # Boost to k=20
                demographic_distribution=group
            )
            synthetic_people.extend(group_synthetics)
    
    # Combine real and synthetic
    combined = real_people + synthetic_people
    
    logger.info(f"Augmented {len(real_people)} real with {len(synthetic_people)} synthetic")
    return combined


def _calculate_demographic_distribution(people: List[Person]) -> Dict:
    """Calculate demographic distribution from real people."""
    distribution = {
        'age': defaultdict(int),
        'gender': defaultdict(int),
        'ethnicity': defaultdict(int),
        'geography': defaultdict(int)
    }
    
    for person in people:
        distribution['age'][person.demographics.age] += 1
        distribution['gender'][person.demographics.gender] += 1
        # ... etc
    
    # Convert counts to probabilities
    total = len(people)
    for category in distribution:
        for key in distribution[category]:
            distribution[category][key] /= total
    
    return distribution
```

### Option 3: API Integration (User-Friendly)

```python
# personatwin/api.py (UPDATE)

def create_safe_personas(
    data: Union[List[Person], pd.DataFrame, List[Dict]],
    privacy_level: Union[str, PrivacyLevel] = "medium",
    domain: Union[str, Domain] = "custom",
    target_risk: float = 0.05,
    
    # NEW: Synthetic persona augmentation
    augment_with_synthetic: bool = False,
    synthetic_source: Optional[str] = "nemotron",  # "nemotron" or "census"
    synthetic_ratio: float = 2.0,  # Ratio of synthetic to real
    synthetic_strategy: str = "match_distribution",  # or "fill_gaps", "boost_rare"
    
    # Existing options
    enable_llm: bool = False,
    llm_api_key: Optional[str] = None,
    use_census_data: bool = True,
) -> ProcessingResult:
    """
    Generate privacy-protected personas.
    
    Args:
        ... (existing args) ...
        
        augment_with_synthetic: Add synthetic personas to increase privacy
        synthetic_source: Source of synthetics ("nemotron", "census")
        synthetic_ratio: Ratio of synthetic to real people (2.0 = 2x synthetic)
        synthetic_strategy: How to select synthetics:
            - "match_distribution": Match real demographic distribution
            - "fill_gaps": Fill missing geographic areas
            - "boost_rare": Add synthetics to rare demographic groups
    
    Example:
        >>> # Basic usage: 2x synthetic personas
        >>> result = pt.create_safe_personas(
        ...     data=people,  # 100 real people
        ...     privacy_level="high",
        ...     augment_with_synthetic=True,  # Add 200 synthetic
        ...     synthetic_source="nemotron"
        ... )
        >>> # Result: 300 personas (100 real + 200 synthetic)
        
        >>> # Advanced: Boost rare demographics
        >>> result = pt.create_safe_personas(
        ...     data=people,
        ...     privacy_level="high",
        ...     augment_with_synthetic=True,
        ...     synthetic_strategy="boost_rare"  # Target rare groups
        ... )
    """
    # Convert data to Person objects
    people = _convert_to_people(data)
    
    # Augment with synthetic if requested
    if augment_with_synthetic:
        from personatwin.external_data import NemotronProvider, CensusSyntheticProvider
        from personatwin.augmentation import augment_with_synthetic as augment
        
        # Get provider
        if synthetic_source == "nemotron":
            provider = NemotronProvider()
        elif synthetic_source == "census":
            provider = CensusSyntheticProvider()
        else:
            raise ValueError(f"Unknown synthetic source: {synthetic_source}")
        
        # Augment
        people = augment(
            real_people=people,
            synthetic_provider=provider,
            strategy=synthetic_strategy,
            synthetic_ratio=synthetic_ratio
        )
        
        logger.info(f"Augmented with synthetic personas. Total: {len(people)}")
    
    # ... rest of existing processing ...
    
    # Run pipeline
    config = ProcessingConfig(
        privacy_level=privacy_level,
        target_population_risk=target_risk,
        domain=domain,
        domain_config=domain_config,
        enable_llm=enable_llm,
        use_census_data=use_census_data,
    )
    
    pipeline = PersonaTwinPipeline(config)
    result = pipeline.process(people)
    
    # Add metadata about synthetic augmentation
    if augment_with_synthetic:
        result.metadata['synthetic_augmentation'] = {
            'source': synthetic_source,
            'ratio': synthetic_ratio,
            'strategy': synthetic_strategy,
            'synthetic_count': sum(1 for p in people if p.is_synthetic)
        }
    
    return result
```

---

## Privacy Considerations

### Critical Requirements

When integrating external datasets, **privacy MUST be maintained**:

#### 1. **Template-Only Usage**

```python
# ✅ SAFE: Extract structural patterns
template = {
    "degree_distribution": [0.1, 0.3, 0.4, 0.15, 0.05],  # Aggregate statistics
    "avg_clustering": 0.42,
    "community_sizes": [50, 75, 100, 125]
}

# ❌ UNSAFE: Copy actual identities or attributes
person_data = {
    "user_123": {"name": "John", "age": 35, "friends": ["user_456", ...]},
    # NO! This violates privacy of original dataset
}
```

#### 2. **No Direct Copying**

```python
# ❌ WRONG: Copy connections from external dataset
for edge in external_dataset.edges:
    copy_connection(edge.source, edge.target)

# ✅ CORRECT: Use pattern to generate new connections
pattern = analyze_external_dataset(external_dataset)
generate_connections_matching_pattern(your_people, pattern)
```

#### 3. **Differential Privacy for Templates**

```python
def extract_template_with_privacy(external_graph, epsilon=1.0):
    """
    Extract network template with differential privacy.
    
    Adds noise to ensure template doesn't leak info about
    individuals in the external dataset.
    """
    # Calculate statistics
    true_avg_degree = calculate_avg_degree(external_graph)
    
    # Add Laplacian noise
    noise = numpy.random.laplace(0, 1/epsilon)
    private_avg_degree = true_avg_degree + noise
    
    return NetworkTemplate(avg_degree=private_avg_degree, ...)
```

### Privacy Impact Assessment

**Question**: Does using external datasets increase privacy risk?

**Answer**: **It depends on implementation**:

| Implementation | Privacy Risk | Explanation |
|---------------|-------------|-------------|
| Template-only (aggregate stats) | ✅ **No increase** | Only uses structural patterns, no personal data |
| With demographic matching | ⚠️ **Slight increase** | May create more realistic (thus more vulnerable) networks |
| Direct copying | ❌ **Major increase** | Violates privacy of both datasets |

**Recommended approach**: Template-only with differential privacy guarantees.

---

## Implementation Phases

### Phase 1: Infrastructure (Week 1)

1. Create `personatwin/external_data.py` module
2. Define `ExternalDatasetProvider` interface
3. Implement `NetworkTemplate` data structure
4. Add caching mechanism

### Phase 2: SNAP Integration (Week 2)

1. Implement `SNAPDataProvider`
2. Add download and caching logic
3. Create template extraction methods
4. Add privacy-preserving statistics

### Phase 3: API Integration (Week 3)

1. Update `create_safe_personas()` API
2. Add configuration options
3. Integrate with `SocialNetworkBuilder`
4. Add validation and error handling

### Phase 4: Testing & Documentation (Week 4)

1. Unit tests for providers
2. Integration tests with real datasets
3. Privacy impact assessment
4. User documentation and examples

---

## Example Usage (Proposed)

### Basic Usage

```python
import personatwin as pt

# Without external datasets (current)
result = pt.create_safe_personas(
    data=people,
    privacy_level="high"
)

# With external datasets (proposed)
result = pt.create_safe_personas(
    data=people,
    privacy_level="high",
    use_external_network=True,
    external_network_dataset="facebook_combined"
)
```

### Advanced Usage

```python
from personatwin.external_data import SNAPDataProvider

# Custom provider configuration
snap = SNAPDataProvider(
    cache_dir="./my_cache",
    privacy_budget=1.0  # Epsilon for differential privacy
)

result = pt.create_safe_personas(
    data=people,
    privacy_level="high",
    use_external_network=True,
    external_network_provider=snap
)

# Check what template was used
print(f"Network template: {result.network_metadata.template_source}")
print(f"Template avg degree: {result.network_metadata.avg_degree}")
```



---

## Benefits vs. Costs

### Benefits ✅

1. **Significantly increased k-anonymity**: 2-5x more people in each demographic group
2. **Reduced concentration risk**: Rare demographics become common
3. **Geographic coverage**: Fill gaps in zipcode coverage
4. **Plausible deniability**: Real people blend with synthetic ones
5. **No real privacy risk**: Synthetic personas have no privacy concerns
6. **Reproducible**: Same synthetic dataset → consistent results
7. **Flexible**: Can target specific demographics or areas

### Costs ⚠️

1. **Modest complexity**: New module for synthetic provider interface
2. **Storage**: Cache synthetic datasets (~50-100MB for Nemotron)
3. **Download time**: One-time download of Nemotron dataset
4. **Utility dilution**: Adding synthetics may slightly reduce statistical precision
5. **Tracking requirement**: Need to mark which personas are synthetic

---

## Recommendation

### Should We Integrate Connection Pattern Protection?

**YES! This is critical for preventing connection-based re-identification.** ✅

#### Priority 1: Connection Pattern Analyzer (High Value) ⭐⭐⭐
- Detects rare connection patterns (k < threshold)
- Identifies: "Connected to [demographic] with [attribute]"
- **Critical for privacy**

#### Priority 2: Synthetic Connection Generator (High Value) ⭐⭐⭐
- Adds synthetic connections to boost k-anonymity
- Uses Census data for realistic demographics
- Preserves network structure while adding noise

#### Priority 3: Census-Based Demographics (Medium Value) ⭐⭐
- Already integrated!
- Provides realistic demographic distributions
- Can generate connection patterns

---

## Conclusion

**Connection pattern protection SHOULD be integrated** because:

1. **Closes privacy gap**: Current system handles network structure but not connection attributes
2. **Real threat**: People CAN be identified by "connected to teacher" or similar patterns
3. **Uses existing data**: Census integration provides needed demographics
4. **Complements existing**: Works with current network anonymization
5. **Targeted approach**: Only adds synthetic connections where needed (rare patterns)

The integration should be:
- ✅ **Automatic** (detect rare patterns automatically)
- ✅ **Configurable** (set k-anonymity threshold for connections)
- ✅ **Transparent** (mark synthetic connections)
- ✅ **Opt-in** (can disable if not using social networks)

---

## Implementation Plan

### Step 1: Create `personatwin/connection_patterns.py` module ✅ DESIGNED
- Implement `ConnectionPatternAnalyzer` class
- Implement `SyntheticConnectionGenerator` class
- Integrate with existing `social_network.py`

### Step 2: Update API (`personatwin/api.py`) 
```python
factory.create_persona(
    use_social_network=True,
    protect_connection_patterns=True,  # NEW
    connection_pattern_k=10            # NEW: k-anonymity threshold
)
```

### Step 3: Update Documentation
- Update README with connection pattern privacy explanation
- Add example showing connection pattern protection
- Document how to configure thresholds

### Step 4: Testing
- Test with rare connection patterns (e.g., "connected to CEO")
- Verify k-anonymity improvement
- Measure impact on network structure

---

## Next Steps

If approved, implement in this order:

1. **Week 1**: Create infrastructure
   - `personatwin/external_data.py`: Provider interface
   - `personatwin/augmentation.py`: Augmentation helpers
   - Add `is_synthetic` flag to Person model

2. **Week 2**: Implement Nemotron provider
   - Download and parse Nemotron dataset
   - Implement filtering and sampling
   - Add caching mechanism

3. **Week 3**: Census-based synthetic generation
   - Use existing CensusDataProvider
   - Generate synthetics from Census distributions
   - Smart demographic matching

4. **Week 4**: API integration and testing
   - Update `create_safe_personas()` API
   - Add `augment_with_synthetic` parameter
   - Write examples and documentation

**Estimated effort**: 3-4 weeks for complete implementation with testing.

---

## Example Usage Summary

```python
import personatwin as pt
import pandas as pd

# Load your data
df = pd.read_csv("data.csv")
real_people = pt.load_data(df, domain="criminal_justice")

# Option 1: No augmentation (current behavior)
result = pt.create_safe_personas(
    data=real_people,
    privacy_level="high"
)
# Result: ~100 personas, moderate privacy

# Option 2: Augment with Nemotron (2x synthetic)
result = pt.create_safe_personas(
    data=real_people,
    privacy_level="high",
    augment_with_synthetic=True,
    synthetic_source="nemotron",
    synthetic_ratio=2.0
)
# Result: ~300 personas (100 real + 200 synthetic), HIGH privacy

# Option 3: Boost rare demographics only
result = pt.create_safe_personas(
    data=real_people,
    privacy_level="high",
    augment_with_synthetic=True,
    synthetic_strategy="boost_rare"
)
# Result: Rare groups now have k≥20, significantly safer

# Check results
print(f"Total personas: {len(result.personas)}")
print(f"Synthetic count: {result.metadata['synthetic_count']}")
print(f"Privacy improved: {result.risk_metrics.population_average_risk:.1%}")
```

**This approach is perfect for your use case!** 🎯
