# How PersonaTwin Maintains Privacy

## Overview

PersonaTwin protects individual privacy while preserving statistical utility through a **multi-layered defense-in-depth approach**. This document explains exactly how each privacy mechanism works and why they work together.

## The Privacy Challenge

### The Problem

You have sensitive data about real people:

```python
# Real person in your database
Person(
    person_id="12345",
    demographics=Demographics(
        age=42,
        gender="Female",
        ethnicity="Asian",
        geography="Hamilton County, OH"
    ),
    events=[
        Event(date="2023-03-15", event_type="arrest", outcome="guilty"),
        Event(date="2023-06-20", event_type="sentencing", outcome="probation")
    ]
)
```

**Privacy risks:**
1. **Direct identification**: Someone recognizes this specific person
2. **Re-identification attacks**: Combining demographics + events uniquely identifies someone
3. **Attribute disclosure**: Learning sensitive information even without identifying the person
4. **Linkage attacks**: Connecting to external datasets (census, public records)

### The Goal

Generate "safe personas" that:
- ✅ Cannot be traced back to specific individuals
- ✅ Preserve population-level patterns for research
- ✅ Meet regulatory requirements (HIPAA, GDPR, etc.)
- ✅ Quantifiably safe (provable privacy guarantees)

---

## Privacy Mechanisms (The Five Pillars)

PersonaTwin uses **five complementary privacy mechanisms** that work together:

### 1. K-Anonymity (Group Privacy)

**What it does**: Ensures every person is indistinguishable from at least k-1 other people.

**How it works**: Merges similar people into single personas.

#### Example:

**Before (Individual Records):**
```
Person 1: Age=42, Female, Asian, Hamilton County → 2 arrests
Person 2: Age=44, Female, Asian, Hamilton County → 3 arrests  
Person 3: Age=41, Female, Asian, Hamilton County → 1 arrest
```

**After (k=3 anonymity):**
```
Persona A: Age=42±2, Female, Asian, Hamilton County → 2 arrests
  ↑ Merged from 3 people - cannot determine which one!
```

**Privacy guarantee**: An adversary cannot narrow down the identity to fewer than k individuals.

#### Code Implementation:

```python
from personatwin.merging import PeopleMerging

merger = PeopleMerging(min_group_size=5)  # k=5

# Merges similar people
personas = merger.merge_similar_people(people)

# Result: Every persona represents ≥5 people
# merged_from attribute tracks the k value
assert all(p.merged_from >= 5 for p in personas)
```

**Why k-anonymity alone isn't enough:**
- Vulnerable to homogeneity attacks (if all k people have same sensitive attribute)
- Vulnerable to background knowledge attacks
- Doesn't protect against attribute disclosure

**Solution**: Layer additional protections...

---

### 2. Differential Privacy (Mathematical Privacy)

**What it does**: Adds calibrated noise so that removing/adding one person doesn't significantly change the output.

**How it works**: Noise is added to:
- Event timestamps (temporal noise)
- Event outcomes (outcome noise)  
- Demographics (geographic generalization)

#### Temporal Noise Example:

**Original timeline:**
```
Arrest:     March 15, 2023
Sentencing: June 20, 2023  (97 days later)
```

**With differential privacy:**
```
Arrest:     ~March 2023 (±15 days noise)
Sentencing: ~June 2023 (±15 days noise)
Approximate time gap: ~3 months
```

**Privacy guarantee**: An adversary learning the persona data can't determine with certainty whether a specific person was in the original dataset.

#### Mathematical Foundation:

A mechanism M provides ε-differential privacy if for all datasets D₁ and D₂ differing by one record:

```
P(M(D₁) = output) ≤ e^ε × P(M(D₂) = output)
```

Where:
- ε (epsilon) = privacy budget (smaller = more private)
- ε = 0.1: Very strong privacy
- ε = 1.0: Moderate privacy
- ε = 3.0: Weaker privacy

#### Code Implementation:

```python
from personatwin.noise import EventNoiseGeneration

noise_gen = EventNoiseGeneration(privacy_level=PrivacyLevel.HIGH)

# Add temporal noise (Laplace distribution)
persona = noise_gen.add_temporal_noise(
    persona, 
    epsilon=1.0,  # Privacy budget
    sensitivity=30  # Days
)

# Add outcome noise
persona = noise_gen.add_outcome_noise(persona, flip_probability=0.05)

# Generalize locations
persona = noise_gen.generalize_locations(persona, level="county")
```

**Key insight**: Noise is **calibrated** based on:
- Privacy level setting (LOW/MEDIUM/HIGH/MAXIMUM)
- Risk assessment from other mechanisms
- Data sensitivity

---

### 3. Census-Enhanced External Linkage Risk Assessment

**What it does**: Detects rare demographic combinations that could be re-identified through external data sources.

**How it works**: Compares persona demographics against real US Census population distributions.

#### Example:

**Scenario**: 35-year-old Pacific Islander female in rural Wyoming

**Census analysis:**
```python
from personatwin.census import CensusEnhancedPrivacyCalculator

calculator = CensusEnhancedPrivacyCalculator()

# Check demographic rarity
rarity = calculator.calculate_demographic_rarity(
    demographics=persona.demographics,
    geography="Wyoming"
)

# Results:
# - Pacific Islander in Wyoming: 0.3% of population
# - Female aged 35-39: 3.2% of population  
# - Rural location: 15% of population
# Combined frequency: 0.3% × 3.2% × 15% = 0.0144% (1 in 6,944)
# 
# Rarity score: 0.92 (VERY HIGH RISK!)
```

**Automatic protection:**
```python
if rarity > 0.7:  # High risk threshold
    # Automatically increase protection:
    # 1. Broader geographic generalization ("Mountain West" instead of "Wyoming")
    # 2. Wider age range (30-40 instead of 35)
    # 3. Higher k-anonymity requirement
    # 4. More temporal noise
```

#### Why this matters:

**Without census enhancement:**
```
Assessment: "35-year-old female in rural area = moderate risk"
Protection: Standard noise + k=5
```

**With census enhancement:**
```
Assessment: "Pacific Islander female in rural Wyoming = RARE (1 in 6,944) = HIGH RISK"
Protection: Aggressive noise + k=10 + broader generalization
```

#### Code Implementation:

```python
from personatwin.privacy import PopulationTraceability

# Enable census-enhanced assessment (default)
risk_calculator = PopulationTraceability(
    privacy_level=PrivacyLevel.HIGH,
    use_census_data=True  # Uses real population distributions
)

# Calculate risks
risk_metrics = risk_calculator.calculate_population_risk(personas)

# Metrics include:
# - demographic_rarity_risk: How rare is this demographic combo?
# - census_enhanced_external_risk: Linkage risk using census data
# - rare_demographics_count: Number of high-risk personas

# Automatic recommendations
print(risk_metrics.recommendation)
# "WARNING: 15 personas have rare demographics. 
#  These individuals are at high re-identification risk from public census data."
```

---

### 4. Population-Level Traceability Metrics

**What it does**: Quantifies the risk that personas can be traced back to original individuals.

**How it works**: Calculates multiple risk dimensions and combines them.

#### Risk Components:

**A. Demographic Concentration Risk**

Measures how many personas share similar demographics:

```python
# Low concentration (diverse) = LOW RISK
Demographics: {
    "30-40, Female, White": 50 personas,
    "30-40, Female, Black": 45 personas,
    "30-40, Female, Asian": 48 personas,
    ...
}

# High concentration (homogeneous) = HIGH RISK  
Demographics: {
    "42, Female, Asian": 180 personas,  # Too specific!
    "43, Female, Asian": 5 personas,
    ...
}
```

**B. Event Pattern Concentration Risk**

Measures uniqueness of event sequences:

```python
# Common patterns = LOW RISK
Pattern: [arrest → trial → guilty → probation] = 250 personas

# Rare patterns = HIGH RISK
Pattern: [arrest → appeal → appeal → acquittal] = 2 personas ⚠️
```

**C. Individual Re-identification Risk**

For each persona, calculates probability of re-identification:

```python
# Formula (simplified):
risk = (
    0.25 × demographic_uniqueness +
    0.25 × event_pattern_uniqueness +
    0.25 × k_anonymity_inverse +
    0.25 × external_linkage_risk
)

# Example results:
Persona A: risk = 0.03 (3% chance of re-identification) ✅ SAFE
Persona B: risk = 0.28 (28% chance of re-identification) ⚠️ REVIEW
Persona C: risk = 0.65 (65% chance of re-identification) ❌ UNSAFE
```

#### Risk Thresholds:

```python
POPULATION_RISK_THRESHOLDS = {
    "SAFE_FOR_PUBLIC_RELEASE": 0.01,    # <1% average risk
    "SAFE_FOR_RESEARCH": 0.05,          # <5% average risk
    "INTERNAL_USE_ONLY": 0.15,          # <15% average risk
    "UNSAFE": 0.30,                      # >30% risk
}

INDIVIDUAL_RISK_THRESHOLDS = {
    "ACCEPTABLE": 0.10,                  # <10% individual risk
    "REVIEW_REQUIRED": 0.25,             # 10-25% needs review
    "MUST_INCREASE_PROTECTION": 0.50,    # >50% must fix
}
```

#### Code Implementation:

```python
from personatwin.privacy import PopulationTraceability

calculator = PopulationTraceability(privacy_level=PrivacyLevel.HIGH)
risk_metrics = calculator.calculate_population_risk(personas)

# Comprehensive risk report:
print(f"Population average risk: {risk_metrics.population_average_risk:.1%}")
print(f"High-risk personas: {len(risk_metrics.high_risk_personas)}")
print(f"K-anonymity: {risk_metrics.k_anonymity}")
print(f"Recommendation: {risk_metrics.recommendation}")

# Risk level classification
level = risk_metrics.get_risk_level()
# Returns: "SAFE_FOR_PUBLIC_RELEASE", "SAFE_FOR_RESEARCH", etc.
```

---

### 5. Automatic Iterative Privacy Adjustment

**What it does**: Automatically increases protection until target privacy level is reached.

**How it works**: Feedback loop that detects high risk and applies more protection.

#### The Adjustment Loop:

```
1. Generate initial personas
2. Calculate risk metrics
3. If risk > target:
   a. Increase k-anonymity (merge more people)
   b. Add more noise
   c. Broaden generalizations
   d. Recalculate risk
4. Repeat until risk ≤ target OR max iterations
```

#### Example Iteration:

**Iteration 1:**
```
Personas: 500
K-anonymity: 3
Temporal noise: ±7 days
Risk: 0.08 (8%) > Target: 0.05 (5%) ❌
Action: Need more protection
```

**Iteration 2:**
```
Personas: 450 (merged more)
K-anonymity: 5
Temporal noise: ±15 days
Risk: 0.06 (6%) > Target: 0.05 (5%) ❌
Action: Need more protection
```

**Iteration 3:**
```
Personas: 400 (merged even more)
K-anonymity: 7
Temporal noise: ±30 days
Risk: 0.04 (4%) ≤ Target: 0.05 (5%) ✅
Result: SAFE FOR RESEARCH
```

#### Code Implementation:

```python
from personatwin.privacy import AutoPrivacyAdjustment

adjuster = AutoPrivacyAdjustment(privacy_level=PrivacyLevel.HIGH)

# Automatic adjustment
adjusted_personas, final_risk = adjuster.adjust_until_safe(
    personas=initial_personas,
    target_risk=0.05,  # 5% target
    max_iterations=5
)

# System automatically:
# - Increases merging aggressiveness
# - Adds more noise
# - Broadens generalizations
# - Validates convergence

print(f"Final risk: {final_risk:.1%}")
print(f"Iterations needed: {adjuster.iterations}")
```

---

## How They Work Together: A Complete Example

Let's walk through a complete privacy protection scenario:

### Original Data

```python
# Real people in your database
people = [
    Person(
        person_id="001",
        demographics=Demographics(age=42, gender="Female", ethnicity="Asian", 
                                 geography="Hamilton County, OH"),
        events=[
            Event(date="2023-03-15", event_type="arrest", outcome="guilty"),
            Event(date="2023-06-20", event_type="sentencing", outcome="probation")
        ]
    ),
    Person(
        person_id="002",
        demographics=Demographics(age=44, gender="Female", ethnicity="Asian",
                                 geography="Hamilton County, OH"),
        events=[
            Event(date="2023-01-10", event_type="arrest", outcome="dismissed"),
            Event(date="2023-05-12", event_type="arrest", outcome="guilty")
        ]
    ),
    # ... 498 more people
]
```

### Step 1: K-Anonymity (Merging)

```python
# Merge similar people
merger = PeopleMerging(min_group_size=5)
personas = merger.merge_similar_people(people)

# Result: 500 people → 100 personas
# Each persona represents ≥5 people
```

**Privacy gain:**
- Can't identify individual #001 vs #002 (merged into same group)
- Demographic becomes "40-45, Female, Asian, Hamilton County"

### Step 2: Census Risk Assessment

```python
# Check for rare demographics
calculator = CensusEnhancedPrivacyCalculator()

for persona in personas:
    rarity = calculator.calculate_demographic_rarity(
        persona.demographics,
        "Hamilton County, OH"
    )
    
    if rarity > 0.7:  # Rare demographic
        # Flag for extra protection
        persona.needs_extra_protection = True
```

**Privacy gain:**
- Detected: "80-85 year old Pacific Islander in rural county" = RARE
- Automatically flagged for extra protection

### Step 3: Differential Privacy (Noise)

```python
# Add calibrated noise
noise_gen = EventNoiseGeneration(privacy_level=PrivacyLevel.HIGH)

for persona in personas:
    # Temporal noise
    persona = noise_gen.add_temporal_noise(persona, epsilon=1.0)
    
    # Outcome noise (small probability)
    persona = noise_gen.add_outcome_noise(persona, flip_probability=0.05)
    
    # Geographic generalization
    if persona.needs_extra_protection:
        persona = noise_gen.generalize_locations(persona, level="state")
    else:
        persona = noise_gen.generalize_locations(persona, level="county")
```

**Privacy gain:**
- Exact dates → fuzzy dates (±15 days)
- Precise locations → generalized regions
- Outcomes slightly randomized

### Step 4: Risk Calculation

```python
# Calculate comprehensive risks
risk_calculator = PopulationTraceability(
    privacy_level=PrivacyLevel.HIGH,
    use_census_data=True
)

risk_metrics = risk_calculator.calculate_population_risk(personas)

print(risk_metrics.to_dict())
```

**Output:**
```python
{
    "population_average_risk": 0.045,  # 4.5% average
    "k_anonymity": 5,
    "high_risk_personas": ["persona_042", "persona_087"],  # 2 need more protection
    "demographic_concentration_risk": 0.35,
    "event_pattern_concentration_risk": 0.28,
    "external_linkage_risk": 0.052,  # Census-enhanced
    "recommendation": "SAFE_FOR_RESEARCH | CENSUS: 2 personas have rare demographics"
}
```

### Step 5: Automatic Adjustment

```python
# Risk too high? Adjust automatically
if risk_metrics.population_average_risk > 0.05:
    adjuster = AutoPrivacyAdjustment(privacy_level=PrivacyLevel.HIGH)
    
    personas = adjuster.increase_protection(
        personas,
        focus_on=risk_metrics.high_risk_personas
    )
    
    # Recalculate
    risk_metrics = risk_calculator.calculate_population_risk(personas)
```

**Privacy gain:**
- High-risk personas get extra merging
- More noise added
- Broader generalizations
- Converges to safe level

### Final Result

```python
# Safe persona (cannot trace back to person 001 or 002)
Persona(
    persona_id="persona_017",
    merged_from=5,  # Represents 5 people
    demographics=Demographics(
        age_range="40-45",  # Not exact age
        gender="Female",
        ethnicity="Asian",
        geography="Hamilton County, OH"  # Or broader if needed
    ),
    events=[
        Event(
            date="~March 2023",  # Fuzzy date
            event_type="arrest",
            outcome="guilty",  # With 5% chance of noise
            location="Hamilton County"  # Generalized
        ),
        Event(
            date="~June 2023",
            event_type="sentencing",
            outcome="probation",
            location="Hamilton County"
        )
    ],
    privacy_metadata=PrivacyMetadata(
        k_anonymity=5,
        noise_level=0.15,
        individual_risk=0.04,  # 4% re-identification risk
        protection_applied=["merging", "temporal_noise", "location_generalization"]
    )
)
```

---

## Privacy Guarantees

### Quantifiable Guarantees

1. **K-Anonymity**: Every persona represents ≥k individuals
   - Guarantee: Cannot narrow identity to <k candidates
   - Configurable: k=3,5,10,etc.

2. **Differential Privacy**: ε-DP guarantee
   - Guarantee: Plausible deniability (could be in or out of dataset)
   - Configurable: ε=0.1 (strong) to ε=3.0 (weak)

3. **Re-identification Risk**: Measured probability
   - Individual risk: <10% per persona (for research use)
   - Population risk: <5% average (for research use)
   - Measured using multiple risk factors

4. **External Linkage**: Census-validated
   - Uses real population distributions
   - Detects rare demographics automatically
   - Adjusts protection accordingly

### Regulatory Compliance

**HIPAA Safe Harbor Method:**
- ✅ Removes 18 direct identifiers
- ✅ Geographic generalization (≥20,000 population)
- ✅ Date generalization (year only or fuzzy)
- ✅ Age generalization (90+ grouped)

**GDPR Article 89:**
- ✅ Pseudonymization (no direct identifiers)
- ✅ Technical safeguards (k-anonymity, DP)
- ✅ Minimization (only necessary data)
- ✅ Purpose limitation (documented use case)

**NIST Privacy Framework:**
- ✅ Risk assessment (quantified metrics)
- ✅ Iterative improvement (automatic adjustment)
- ✅ Transparency (detailed reporting)
- ✅ Accountability (audit trail)

---

## Attack Resistance

### 1. Singling Out Attack

**Attack**: Adversary tries to isolate a specific individual.

**Defense**: K-anonymity ensures ≥k indistinguishable candidates.

```python
# Attacker knows: "42-year-old Asian female in Hamilton County"
# Finds: 5+ personas with those attributes
# Cannot determine which one is the target
```

### 2. Linkage Attack

**Attack**: Link to external dataset (census, voter records).

**Defense**: Census-enhanced risk assessment + geographic generalization.

```python
# Attacker tries to match demographics to census blocks
# Defense: 
# - Rare demographics flagged and protected
# - Geographic areas generalized to ≥20,000 population
# - Age ranges instead of exact ages
```

### 3. Inference Attack

**Attack**: Infer sensitive attributes from non-sensitive ones.

**Defense**: Noise injection + outcome randomization.

```python
# Attacker knows pattern: "All arrests in July → all guilty verdicts"
# Defense:
# - Dates have ±15 day noise (could be June or August)
# - Outcomes have 5% flip probability
# - Pattern correlation reduced
```

### 4. Composition Attack

**Attack**: Combine multiple releases to narrow down identity.

**Defense**: Differential privacy with privacy budget tracking.

```python
# Multiple releases tracked with ε budget
total_epsilon = 0
max_epsilon = 3.0

for release in releases:
    total_epsilon += release.epsilon
    if total_epsilon > max_epsilon:
        raise PrivacyBudgetExceeded()
```

### 5. Background Knowledge Attack

**Attack**: Use prior knowledge to narrow down candidates.

**Defense**: High k-anonymity + noise + census-aware protection.

```python
# Attacker knows: "My neighbor was arrested in March"
# Defense:
# - k=10 means 10+ neighbors match the profile
# - Dates have noise (could be February-April)
# - Cannot definitively identify the specific neighbor
```

---

## Usage Examples

### Basic Usage (Default Protection)

```python
import personatwin as pt

# Load sensitive data
people = pt.load_criminal_justice_data("court_records.csv")

# Generate safe personas (default: MEDIUM privacy)
result = pt.create_safe_personas(
    data=people,
    privacy_level="medium",
    domain="criminal_justice"
)

# Check safety
print(f"Risk: {result.risk_metrics.population_average_risk:.1%}")
print(f"K-anonymity: {result.risk_metrics.k_anonymity}")
print(f"Safe? {result.is_safe_for_research()}")
```

### High Privacy (Public Release)

```python
# Maximum protection for public data sharing
result = pt.create_safe_personas(
    data=sensitive_medical_records,
    privacy_level="high",
    domain="healthcare",
    target_risk=0.01,  # 1% risk (safe for public)
    use_census_data=True  # Enable census enhancement
)

# Export with privacy report
pt.export_personas(result.personas, "public_data.csv")
pt.export_privacy_report(result, "privacy_audit.html")
```

### Custom Privacy Requirements

```python
from personatwin import ProcessingConfig, PrivacyLevel

# Fine-grained control
config = ProcessingConfig(
    privacy_level=PrivacyLevel.MAXIMUM,
    target_population_risk=0.005,  # 0.5% risk
    min_k_anonymity=10,  # Minimum k=10
    use_census_data=True,
    max_iterations=10  # More adjustment rounds
)

pipeline = pt.PersonaTwinPipeline(config)
result = pipeline.process_dataset(people, target_risk=0.005)
```

---

## Verification and Auditing

### Privacy Report

```python
result = pt.create_safe_personas(data, privacy_level="high")

# Generate comprehensive report
report = result.risk_metrics.to_dict()

print(f"""
PRIVACY AUDIT REPORT
====================

Population Metrics:
- Average re-identification risk: {report['population_average_risk']:.1%}
- K-anonymity: {report['k_anonymity']}
- High-risk personas: {len(report['high_risk_personas'])}

Risk Components:
- Demographic concentration: {report['demographic_concentration_risk']:.3f}
- Event pattern concentration: {report['event_pattern_concentration_risk']:.3f}
- External linkage risk: {report['external_linkage_risk']:.3f}

Classification: {report['recommendation']}

Individual Risks:
- Min: {min(report['individual_risks'].values()):.1%}
- Max: {max(report['individual_risks'].values()):.1%}
- Median: {median(report['individual_risks'].values()):.1%}
""")
```

### Validation Tests

```python
# Verify k-anonymity
assert all(p.merged_from >= 5 for p in result.personas), "K-anonymity violated!"

# Verify risk thresholds
assert result.risk_metrics.population_average_risk <= 0.05, "Risk too high!"

# Verify no high-risk outliers
high_risk_count = len(result.risk_metrics.high_risk_personas)
assert high_risk_count == 0, f"Found {high_risk_count} high-risk personas!"

# Verify census enhancement applied
assert "CENSUS" in result.risk_metrics.recommendation, "Census not used!"
```

---

## Summary: Defense in Depth

PersonaTwin maintains privacy through **five complementary layers**:

1. **K-Anonymity**: Group indistinguishability (≥k candidates)
2. **Differential Privacy**: Mathematical plausible deniability
3. **Census-Enhanced Assessment**: Detects rare demographics
4. **Risk Quantification**: Measures actual re-identification probability
5. **Automatic Adjustment**: Converges to target safety level

**Key principle**: Each layer catches what others might miss.

### Privacy Spectrum

```
LOW PRIVACY          MEDIUM PRIVACY        HIGH PRIVACY          MAXIMUM PRIVACY
────────────────────────────────────────────────────────────────────────────────
k=3                  k=5                   k=7                   k=10
ε=2.0                ε=1.0                 ε=0.5                 ε=0.1
±7 days noise        ±15 days noise        ±30 days noise        ±60 days noise
County-level         County-level          State-level           Region-level
Risk: <15%           Risk: <5%             Risk: <1%             Risk: <0.1%
Internal use         Research use          Public release        Maximum protection
```

### The Bottom Line

**PersonaTwin transforms sensitive data into safe personas through:**

✅ **Proven techniques**: K-anonymity, differential privacy, risk assessment
✅ **Real-world data**: Census-based demographic analysis
✅ **Quantifiable guarantees**: Measured re-identification risk
✅ **Automatic protection**: Self-adjusting until safe
✅ **Regulatory compliance**: HIPAA, GDPR, NIST standards
✅ **Attack resistance**: Defense against known privacy attacks
✅ **Transparency**: Detailed audit reports and metrics

**You can confidently share the resulting personas for research, knowing that individual privacy is mathematically protected.**
