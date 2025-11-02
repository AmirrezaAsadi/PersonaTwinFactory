# PersonaTwin System Requirements
## Privacy-Preserving People-Events Data Sharing for Public Sector Transparency

### Executive Summary
PersonaTwin transforms sensitive people-events datasets (criminal justice, healthcare, social services) into shareable personas while preserving statistical utility for bias analysis and policy research. The system automatically measures population-level traceability risk and uses AI-driven adjustments to ensure safety.

---

## 1. CORE DATA MODEL

### 1.1 People-Events Structure
```python
# Input Data Structure
Person = {
    person_id: str,                    # Direct identifier (will be removed)
    demographics: {
        age: int,                      # PRESERVE for bias analysis
        gender: str,                   # PRESERVE for bias analysis  
        ethnicity: str,                # PRESERVE for bias analysis
        geography: str,                # PRESERVE (but may generalize)
        socioeconomic_indicators: {}   # PRESERVE for equity analysis
    },
    events: [Event1, Event2, Event3, ...]
}

Event = {
    event_id: str,                     # Direct identifier (will be removed)
    date: datetime,                    # NOISE (generalize to periods)
    event_type: str,                   # PRESERVE (arrest, sentencing, etc.)
    outcome: str,                      # PRESERVE (guilty, dismissed, etc.)
    details: {},                       # CONTEXT-DEPENDENT processing
    location: str,                     # GENERALIZE (specific address → county)
    associated_people: [person_ids]    # ANONYMIZE but preserve relationships
}
```

### 1.2 Output Structure
```python
# Generated Personas
Persona = {
    persona_id: str,                   # New synthetic identifier
    merged_from: int,                  # How many real people merged
    demographics: {
        age_range: str,                # "30-35" instead of exact age
        gender: str,                   # Preserved
        ethnicity: str,                # Preserved  
        geography: str,                # "Hamilton County" vs "123 Main St"
        confidence_level: float        # How much noise was added
    },
    event_patterns: {
        event_types: [list],           # All event types from merged people
        temporal_patterns: {},         # Time-based sequences (with noise)
        outcome_distributions: {},     # Statistical summaries
        recidivism_indicators: {},     # Pattern preservation
    },
    privacy_metadata: {
        traceability_score: float,     # Risk level for this persona
        noise_level: float,            # Amount of artificial noise added
        merge_count: int,              # Number of people merged
        generation_method: str         # Algorithm used
    }
}
```

---

## 2. PRIVACY PROTECTION REQUIREMENTS

### 2.1 Population-Level Traceability Measurement
```python
class PopulationTraceability:
    """
    Measure risk of re-identifying individuals across entire population
    """
    
    def calculate_population_risk(self, personas: List[Persona], original_data: List[Person]) -> RiskMetrics:
        """
        Requirements:
        - Calculate risk for EACH persona individually
        - Calculate OVERALL population risk 
        - Consider demographic uniqueness (rare combinations)
        - Consider event pattern uniqueness
        - Account for external data linkage risks
        """
        return RiskMetrics(
            individual_risks: Dict[persona_id, float],      # 0-1 risk per persona
            population_average_risk: float,                 # Overall average
            high_risk_personas: List[persona_id],           # Above threshold
            demographic_concentration_risk: float,          # Risk from rare demographics  
            event_pattern_concentration_risk: float,        # Risk from unique event sequences
            external_linkage_risk: float,                   # Risk from public records linkage
            recommendation: str                             # "SAFE", "INCREASE_MERGING", "INCREASE_NOISE"
        )
```

### 2.2 Risk Thresholds and Targets
```python
POPULATION_RISK_THRESHOLDS = {
    "SAFE_FOR_PUBLIC_RELEASE": 0.01,      # <1% average re-identification risk
    "SAFE_FOR_RESEARCH": 0.05,            # <5% average re-identification risk  
    "INTERNAL_USE_ONLY": 0.15,            # <15% average re-identification risk
    "UNSAFE": 0.30                        # >30% re-identification risk
}

INDIVIDUAL_RISK_THRESHOLDS = {
    "ACCEPTABLE": 0.10,                    # <10% individual risk
    "REVIEW_REQUIRED": 0.25,              # 10-25% individual risk
    "MUST_INCREASE_PROTECTION": 0.50      # >50% individual risk
}
```

### 2.3 Automatic Risk Mitigation
```python
class AutoPrivacyAdjustment:
    """
    Automatically increase protection when risk is too high
    """
    
    def adjust_privacy_level(self, current_risk: RiskMetrics, target_risk: float) -> PrivacyActions:
        """
        Requirements:
        - IF population_risk > target: increase merging AND/OR noise
        - IF individual high-risk personas exist: apply targeted protection
        - Use LLM to intelligently decide between merging vs noise
        - Preserve maximum utility while meeting risk targets
        """
        
        if current_risk.population_average_risk > target_risk:
            return self._escalate_protection(current_risk)
        
    def _escalate_protection(self, risk: RiskMetrics) -> PrivacyActions:
        """
        Escalation Strategy:
        1. FIRST: Increase merging of similar people 
        2. SECOND: Add temporal noise to events
        3. THIRD: Generalize demographics (age ranges, broader geography)
        4. LAST: Add synthetic noise events (via LLM)
        """
```

---

## 3. MERGING AND NOISE REQUIREMENTS

### 3.1 People Merging Strategy
```python
class PeopleMerging:
    """
    Merge similar people to reduce uniqueness
    """
    
    def merge_similar_people(self, people: List[Person], similarity_threshold: float) -> List[Persona]:
        """
        Requirements:
        - Group people by similar demographics (age ±X, same gender/ethnicity/geography)
        - Combine their events into unified patterns
        - Preserve important sequences (recidivism, escalation)
        - Maintain statistical validity of outcomes
        - Ensure minimum group sizes (k-anonymity)
        """
        
    def calculate_similarity(self, person1: Person, person2: Person) -> float:
        """
        Similarity Factors:
        - Demographics: age difference, gender match, ethnicity match, geography proximity
        - Event patterns: similar crime types, similar outcomes, similar timeframes
        - Risk factors: socioeconomic similarity
        """
        
    MERGING_CRITERIA = {
        "age_tolerance": 3,                # ±3 years
        "geography_level": "county",       # Same county required
        "gender_match": True,              # Must match
        "ethnicity_match": True,           # Must match  
        "minimum_group_size": 5,           # At least 5 people per merged persona
        "maximum_group_size": 50,          # No more than 50 people per persona
    }
```

### 3.2 Event Noise Generation
```python
class EventNoiseGeneration:
    """
    Add intelligent noise to events while preserving patterns
    """
    
    def add_temporal_noise(self, events: List[Event]) -> List[Event]:
        """
        Requirements:
        - Blur exact dates to time periods ("Q2 2023" vs "June 15, 2023")
        - Preserve temporal sequences (Event A before Event B)
        - Maintain seasonal patterns if relevant
        - Add configurable noise levels
        """
        
    def add_outcome_noise(self, events: List[Event]) -> List[Event]:
        """
        Requirements:
        - Slightly modify sentences within realistic ranges
        - Add uncertainty to binary outcomes (95% guilty → 90-100% guilty)
        - Preserve overall statistical distributions
        - Ensure legal realism (no impossible sentences)
        """
        
    def add_synthetic_events(self, person_profile: Dict, risk_level: float) -> List[Event]:
        """
        LLM-Generated Synthetic Events:
        - Generate realistic but fake events to add noise
        - Based on person's demographic profile and existing patterns  
        - Used only when other methods insufficient for privacy
        - Must be legally and contextually realistic
        """
```

---

## 4. LLM INTEGRATION REQUIREMENTS

### 4.1 AI-Driven Privacy Adjustment
```python
class LLMPrivacyAssistant:
    """
    Use LLM to make intelligent privacy decisions
    """
    
    def analyze_risk_and_recommend(self, 
                                  risk_metrics: RiskMetrics, 
                                  data_characteristics: Dict) -> PrivacyRecommendation:
        """
        LLM Prompt Context:
        - Current population risk levels
        - High-risk personas and their characteristics  
        - Data utility requirements (bias analysis, policy research)
        - Available privacy techniques (merging, noise, generalization)
        
        LLM Decision Making:
        - Which personas need more protection?
        - Should we merge more people or add more noise?
        - What's the optimal privacy-utility trade-off?
        - Generate synthetic events if needed
        """
        
    def generate_synthetic_events(self, person_context: Dict, noise_level: float) -> List[Event]:
        """
        Requirements:
        - Generate realistic but fictional events
        - Match demographic and geographic context
        - Ensure legal/procedural accuracy
        - Calibrate noise level to required privacy protection
        """
        
    PRIVACY_PROMPTS = {
        "risk_analysis": """
            Analyze this criminal justice dataset's re-identification risk:
            
            Population size: {n_people}
            Average risk: {avg_risk}
            High-risk personas: {high_risk_count}
            Target risk level: {target_risk}
            
            Recommend the best privacy protection strategy:
            1. Increase merging (combines more people per persona)
            2. Add temporal noise (blur dates and sequences)  
            3. Geographic generalization (county vs city)
            4. Synthetic event injection (add fake events)
            
            Consider: We need to preserve gender, ethnicity, and geography for bias analysis.
            """,
            
        "synthetic_events": """
            Generate a realistic criminal justice event for privacy protection:
            
            Person context: {demographics}
            Existing events: {event_history}
            Geographic area: {geography}
            Noise level needed: {noise_level}
            
            Generate 1-2 plausible events that fit this profile but add privacy protection.
            Ensure legal realism and maintain statistical validity.
            """
    }
```

### 4.2 Context-Aware Event Generation
```python
class SyntheticEventGenerator:
    """
    Generate realistic synthetic events using LLM knowledge
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = LLMInterface(model=llm_model)
        self.legal_constraints = LegalKnowledgeBase()
        self.geographic_context = GeographicDatabase()
        
    def generate_contextual_events(self, 
                                  person_demographics: Dict,
                                  existing_events: List[Event],
                                  geographic_area: str,
                                  noise_level: float) -> List[Event]:
        """
        Requirements:
        - Events must be realistic for demographic group
        - Events must be legally possible in jurisdiction
        - Events must maintain temporal logic (can't be sentenced before arrest)
        - Events should add privacy noise without distorting overall patterns
        """
```

---

## 5. BIAS ANALYSIS PRESERVATION

### 5.1 Statistical Validity Requirements
```python
class BiasAnalysisPreservation:
    """
    Ensure personas enable meaningful bias analysis
    """
    
    def validate_demographic_distributions(self, 
                                         personas: List[Persona], 
                                         original_data: List[Person]) -> ValidationReport:
        """
        Requirements:
        - Preserve racial/ethnic outcome disparities
        - Preserve gender-based sentencing patterns  
        - Preserve geographic disparities
        - Maintain age-related patterns
        - Preserve socioeconomic correlations
        """
        
    def validate_outcome_patterns(self, personas: List[Persona], original_data: List[Person]) -> ValidationReport:
        """
        Requirements:
        - Sentencing disparities preserved within statistical significance
        - Conviction rate patterns maintained
        - Recidivism patterns preserved
        - Appeal success rates maintained
        - Plea bargain patterns preserved
        """
        
    BIAS_ANALYSIS_REQUIREMENTS = {
        "preserve_disparities": True,           # Keep bias patterns for analysis
        "statistical_significance": 0.05,      # Maintain p<0.05 for known disparities
        "effect_size_preservation": 0.90,      # Preserve 90% of effect sizes
        "correlation_preservation": 0.85,      # Preserve 85% of correlations
    }
```

### 5.2 Research Use Case Support
```python
class ResearchUseValidation:
    """
    Validate that personas support specific research questions
    """
    
    SUPPORTED_RESEARCH_QUESTIONS = [
        "Are there racial disparities in sentencing for similar crimes?",
        "Do geographic differences affect conviction rates?", 
        "What factors predict recidivism?",
        "How do plea bargain rates vary by demographics?",
        "Are there gender differences in sentence length?",
        "Do public defenders achieve different outcomes than private attorneys?",
        "How do drug offense sentences vary by geography and demographics?"
    ]
    
    def validate_research_capability(self, personas: List[Persona], research_question: str) -> ResearchValidation:
        """
        Requirements:
        - Verify personas can answer specific research questions
        - Ensure sufficient statistical power
        - Confirm bias patterns are preserved
        - Validate temporal patterns if needed
        """
```

---

## 6. SYSTEM ARCHITECTURE REQUIREMENTS

### 6.1 Core Processing Pipeline
```python
class PersonaTwinPipeline:
    """
    End-to-end processing pipeline
    """
    
    def process_dataset(self, 
                       input_data: List[Person], 
                       target_risk_level: float,
                       research_requirements: List[str]) -> ProcessingResult:
        """
        Processing Steps:
        1. Data validation and cleaning
        2. Initial person-event parsing
        3. Demographic analysis and grouping
        4. Initial merging based on similarity
        5. Population risk calculation
        6. LLM-driven risk assessment 
        7. Iterative privacy adjustment
        8. Final validation and reporting
        """
        
        # Step 1: Parse and validate
        people, events = self.parse_input_data(input_data)
        
        # Step 2: Initial merging
        initial_personas = self.merge_similar_people(people)
        
        # Step 3: Risk assessment
        risk_metrics = self.calculate_population_risk(initial_personas, people)
        
        # Step 4: LLM-driven adjustment
        while risk_metrics.population_average_risk > target_risk_level:
            privacy_actions = self.llm_assistant.recommend_actions(risk_metrics)
            initial_personas = self.apply_privacy_actions(initial_personas, privacy_actions)
            risk_metrics = self.calculate_population_risk(initial_personas, people)
            
        # Step 5: Validation
        research_validation = self.validate_research_capability(initial_personas, research_requirements)
        
        return ProcessingResult(
            personas=initial_personas,
            risk_metrics=risk_metrics,
            research_validation=research_validation,
            processing_log=self.get_processing_log()
        )
```

### 6.2 API Requirements
```python
# Simple API
import personatwin as pt

# Load criminal justice data
data = pt.load_criminal_justice_data("court_records.csv")

# Generate personas with automatic risk management
result = pt.create_safe_personas(
    data=data,
    target_population_risk=0.01,  # 1% re-identification risk
    preserve_for_analysis=["sentencing_disparities", "recidivism_patterns"],
    llm_model="gpt-4"
)

# Check results
print(f"Population risk: {result.risk_metrics.population_average_risk:.3f}")
print(f"Research questions supported: {len(result.research_validation.supported_questions)}")
print(f"Safe for public release: {result.is_safe_for_public()}")

# Export for sharing
result.export_personas("safe_court_data.csv")
result.export_privacy_report("privacy_assessment.html")
```

---

## 7. PERFORMANCE AND SCALABILITY REQUIREMENTS

### 7.1 Data Scale Requirements
- **Small datasets**: 100-1,000 people (real-time processing)
- **Medium datasets**: 1,000-100,000 people (< 1 hour processing)
- **Large datasets**: 100,000+ people (batch processing, < 24 hours)

### 7.2 LLM Integration Performance
- **API rate limiting**: Handle OpenAI/Anthropic rate limits gracefully
- **Cost optimization**: Minimize LLM calls through intelligent batching
- **Fallback mechanisms**: Rule-based alternatives when LLM unavailable
- **Caching**: Cache LLM responses for similar contexts

### 7.3 Memory and Storage
- **Streaming processing**: Handle datasets larger than memory
- **Incremental processing**: Process new data without recomputing everything
- **Temporary storage**: Secure handling of intermediate results

---

## 8. VALIDATION AND TESTING REQUIREMENTS

### 8.1 Privacy Testing
```python
class PrivacyTesting:
    """
    Comprehensive privacy validation
    """
    
    def test_reidentification_resistance(self, personas: List[Persona], original_data: List[Person]):
        """
        Requirements:
        - Automated re-identification attacks
        - Linkage attacks with external datasets
        - Demographic inference attacks
        - Event pattern matching attacks
        """
        
    def test_statistical_utility(self, personas: List[Persona], original_data: List[Person]):
        """
        Requirements:
        - Preserve known research findings
        - Maintain statistical significance of disparities
        - Preserve correlation structures
        - Validate regression coefficients
        """
```

### 8.2 Real-World Validation
- **Academic partnership**: Validate with criminal justice researchers
- **Legal review**: Ensure compliance with FOIA and privacy laws
- **Audit capability**: External privacy audits of generated personas
- **Benchmarking**: Compare against existing anonymization tools

---

## 9. COMPLIANCE AND GOVERNANCE

### 9.1 Legal Compliance
- **FOIA compliance**: Support Freedom of Information Act requests
- **Privacy law compliance**: GDPR, CCPA, state privacy laws
- **Criminal justice regulations**: Comply with court data sharing rules
- **Research ethics**: IRB-compatible data sharing

### 9.2 Transparency and Auditability
- **Method documentation**: Full documentation of privacy techniques used
- **Reproducibility**: Ability to regenerate same personas from same inputs
- **Change tracking**: Log all privacy adjustments and decisions
- **External audits**: Support third-party privacy assessments

---

## 10. SUCCESS CRITERIA

### 10.1 Privacy Goals
- ✅ **Population re-identification risk < 1%** for public release
- ✅ **Individual re-identification risk < 10%** for any persona
- ✅ **Automated risk adjustment** maintains targets without manual intervention
- ✅ **External linkage resistance** against known public datasets

### 10.2 Utility Goals  
- ✅ **Preserve 90%+ of known bias patterns** for research validity
- ✅ **Support 80%+ of common research questions** in criminal justice
- ✅ **Maintain statistical significance** of existing findings
- ✅ **Enable new research** not possible with restricted data

### 10.3 Usability Goals
- ✅ **One-command processing** for standard use cases
- ✅ **Clear risk reporting** understandable by non-experts
- ✅ **Research validation** confirms data fitness for specific studies
- ✅ **Public sector adoption** by actual government agencies

---

This system would enable **genuine public sector transparency** while protecting individual privacy through sophisticated AI-driven risk management and intelligent noise generation.
