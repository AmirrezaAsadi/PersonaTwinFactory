"""
Privacy protection and risk assessment for PersonaTwin.

This module implements:
- Risk calculation and metrics
- Privacy level definitions
- Population-level traceability measurement
- Automatic risk mitigation strategies
- Census-enhanced privacy assessment using public data
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import numpy as np
from collections import Counter
import logging

# Try to import census module
try:
    from .census import CensusEnhancedPrivacyCalculator, create_census_enhanced_calculator
    CENSUS_AVAILABLE = True
except ImportError:
    CENSUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy protection levels."""
    LOW = "low"  # Minimal protection, higher utility
    MEDIUM = "medium"  # Balanced protection
    HIGH = "high"  # Strong protection, lower utility
    MAXIMUM = "maximum"  # Maximum protection, minimal utility


# Risk thresholds based on requirements
POPULATION_RISK_THRESHOLDS = {
    "SAFE_FOR_PUBLIC_RELEASE": 0.01,  # <1% average re-identification risk
    "SAFE_FOR_RESEARCH": 0.05,  # <5% average re-identification risk
    "INTERNAL_USE_ONLY": 0.15,  # <15% average re-identification risk
    "UNSAFE": 0.30,  # >30% re-identification risk
}

INDIVIDUAL_RISK_THRESHOLDS = {
    "ACCEPTABLE": 0.10,  # <10% individual risk
    "REVIEW_REQUIRED": 0.25,  # 10-25% individual risk
    "MUST_INCREASE_PROTECTION": 0.50,  # >50% individual risk
}


@dataclass
class RiskMetrics:
    """
    Comprehensive risk assessment for generated personas.
    
    Measures both individual and population-level re-identification risks.
    """
    individual_risks: Dict[str, float] = field(default_factory=dict)  # persona_id -> risk
    population_average_risk: float = 0.0
    high_risk_personas: List[str] = field(default_factory=list)
    demographic_concentration_risk: float = 0.0
    event_pattern_concentration_risk: float = 0.0
    external_linkage_risk: float = 0.0
    recommendation: str = "UNKNOWN"
    k_anonymity: int = 0  # Minimum group size
    
    def get_risk_level(self) -> str:
        """Determine overall risk level based on population average."""
        if self.population_average_risk <= POPULATION_RISK_THRESHOLDS["SAFE_FOR_PUBLIC_RELEASE"]:
            return "SAFE_FOR_PUBLIC_RELEASE"
        elif self.population_average_risk <= POPULATION_RISK_THRESHOLDS["SAFE_FOR_RESEARCH"]:
            return "SAFE_FOR_RESEARCH"
        elif self.population_average_risk <= POPULATION_RISK_THRESHOLDS["INTERNAL_USE_ONLY"]:
            return "INTERNAL_USE_ONLY"
        else:
            return "UNSAFE"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "population_average_risk": self.population_average_risk,
            "risk_level": self.get_risk_level(),
            "high_risk_count": len(self.high_risk_personas),
            "demographic_concentration_risk": self.demographic_concentration_risk,
            "event_pattern_concentration_risk": self.event_pattern_concentration_risk,
            "external_linkage_risk": self.external_linkage_risk,
            "recommendation": self.recommendation,
            "k_anonymity": self.k_anonymity,
        }


class PopulationTraceability:
    """
    Measure risk of re-identifying individuals across entire population.
    
    Implements sophisticated privacy risk assessment based on:
    - Demographic uniqueness
    - Event pattern uniqueness
    - K-anonymity
    - External linkage risks
    
    Can optionally use census data for enhanced privacy assessment.
    """
    
    def __init__(
        self, 
        privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM,
        use_census_data: bool = True
    ):
        self.privacy_level = privacy_level
        self.risk_weights = self._get_risk_weights()
        self.use_census_data = use_census_data
        self.census_calculator = None
        
        # Initialize census calculator if available and enabled
        if use_census_data and CENSUS_AVAILABLE:
            try:
                self.census_calculator = create_census_enhanced_calculator()
                logger.info("Census-enhanced privacy assessment enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize census calculator: {e}")
                self.census_calculator = None
        elif use_census_data and not CENSUS_AVAILABLE:
            logger.warning("Census module not available. Using basic privacy assessment.")
    
    def _get_risk_weights(self) -> Dict[str, float]:
        """Get risk component weights based on privacy level."""
        if self.privacy_level == PrivacyLevel.LOW:
            return {
                "demographic": 0.3,
                "event_pattern": 0.3,
                "k_anonymity": 0.2,
                "external_linkage": 0.2,
            }
        elif self.privacy_level == PrivacyLevel.MEDIUM:
            return {
                "demographic": 0.25,
                "event_pattern": 0.25,
                "k_anonymity": 0.25,
                "external_linkage": 0.25,
            }
        elif self.privacy_level == PrivacyLevel.HIGH:
            return {
                "demographic": 0.2,
                "event_pattern": 0.2,
                "k_anonymity": 0.3,
                "external_linkage": 0.3,
            }
        else:  # MAXIMUM
            return {
                "demographic": 0.15,
                "event_pattern": 0.15,
                "k_anonymity": 0.35,
                "external_linkage": 0.35,
            }
    
    def calculate_population_risk(
        self, 
        personas: List['Persona'],  # type: ignore
        original_data: Optional[List['Person']] = None  # type: ignore
    ) -> RiskMetrics:
        """
        Calculate comprehensive privacy risk metrics for generated personas.
        
        Args:
            personas: List of generated personas
            original_data: Optional original data for comparison
            
        Returns:
            RiskMetrics with detailed risk assessment
        """
        if not personas:
            return RiskMetrics(recommendation="NO_DATA")
        
        # Calculate individual risks
        individual_risks = {}
        for persona in personas:
            risk = self._calculate_individual_risk(persona, personas)
            individual_risks[persona.persona_id] = risk
        
        # Calculate population metrics
        population_avg_risk = np.mean(list(individual_risks.values()))
        
        # Find high-risk personas
        high_risk_threshold = INDIVIDUAL_RISK_THRESHOLDS["REVIEW_REQUIRED"]
        high_risk_personas = [
            pid for pid, risk in individual_risks.items()
            if risk > high_risk_threshold
        ]
        
        # Calculate component risks
        demographic_risk = self._calculate_demographic_concentration(personas)
        event_pattern_risk = self._calculate_event_pattern_concentration(personas)
        external_risk = self._estimate_external_linkage_risk(personas)
        
        # Calculate k-anonymity
        k_anonymity = self._calculate_k_anonymity(personas)
        
        # Enhance with census data if available
        census_enhanced_metrics = {}
        if self.census_calculator:
            try:
                census_enhanced_metrics = self.census_calculator.enhance_risk_metrics(
                    personas, None  # Will create basic metrics internally
                )
                # Update external risk with census-enhanced version if available
                if "census_enhanced_external_risk" in census_enhanced_metrics:
                    external_risk = census_enhanced_metrics["census_enhanced_external_risk"]
                    logger.info("Using census-enhanced external linkage risk")
            except Exception as e:
                logger.warning(f"Census enhancement failed: {e}")
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            float(population_avg_risk), high_risk_personas, k_anonymity
        )
        
        # Add census recommendation if available
        if self.census_calculator and census_enhanced_metrics:
            try:
                census_rec = self.census_calculator.get_recommendation_with_census(
                    personas, None, float(population_avg_risk)
                )
                recommendation = f"{recommendation} | CENSUS: {census_rec}"
            except Exception as e:
                logger.warning(f"Census recommendation failed: {e}")
        
        return RiskMetrics(
            individual_risks=individual_risks,
            population_average_risk=float(population_avg_risk),
            high_risk_personas=high_risk_personas,
            demographic_concentration_risk=demographic_risk,
            event_pattern_concentration_risk=event_pattern_risk,
            external_linkage_risk=external_risk,
            recommendation=recommendation,
            k_anonymity=k_anonymity,
        )
    
    def _calculate_individual_risk(
        self, 
        persona: 'Persona',  # type: ignore
        all_personas: List['Persona']  # type: ignore
    ) -> float:
        """Calculate re-identification risk for a single persona."""
        # Demographic uniqueness
        demo_risk = self._calculate_demographic_uniqueness(persona, all_personas)
        
        # Event pattern uniqueness
        event_risk = self._calculate_event_pattern_uniqueness(persona, all_personas)
        
        # K-anonymity risk (inverse of merge count)
        k_risk = 1.0 / max(persona.merged_from, 1)
        
        # External linkage risk (based on geographic specificity)
        external_risk = self._calculate_persona_external_risk(persona)
        
        # Weighted combination
        weights = self.risk_weights
        total_risk = (
            weights["demographic"] * demo_risk +
            weights["event_pattern"] * event_risk +
            weights["k_anonymity"] * k_risk +
            weights["external_linkage"] * external_risk
        )
        
        return min(total_risk, 1.0)
    
    def _calculate_demographic_uniqueness(
        self,
        persona: 'Persona',  # type: ignore
        all_personas: List['Persona']  # type: ignore
    ) -> float:
        """Calculate how unique a persona's demographics are."""
        demo = persona.demographics
        
        # Count similar personas
        similar_count = sum(
            1 for p in all_personas
            if (p.demographics.gender == demo.gender and
                p.demographics.ethnicity == demo.ethnicity and
                self._age_similar(p.demographics, demo))
        )
        
        # Risk inversely proportional to similar count
        return 1.0 / max(similar_count, 1)
    
    def _age_similar(self, demo1, demo2, tolerance: int = 5) -> bool:
        """Check if two demographics have similar ages."""
        if demo1.age is not None and demo2.age is not None:
            return abs(demo1.age - demo2.age) <= tolerance
        return True  # If ages unknown, consider similar
    
    def _calculate_event_pattern_uniqueness(
        self,
        persona: 'Persona',  # type: ignore
        all_personas: List['Persona']  # type: ignore
    ) -> float:
        """Calculate how unique a persona's event patterns are."""
        event_types = set(persona.event_patterns.event_types)
        
        if not event_types:
            return 0.0
        
        # Count personas with similar event patterns
        similar_count = sum(
            1 for p in all_personas
            if len(set(p.event_patterns.event_types) & event_types) >= len(event_types) * 0.5
        )
        
        return 1.0 / max(similar_count, 1)
    
    def _calculate_persona_external_risk(self, persona: 'Persona') -> float:  # type: ignore
        """Estimate risk of linking to external data sources."""
        risk = 0.0
        
        # Geographic specificity increases risk
        geo = persona.demographics.geography
        if geo:
            if "address" in geo.lower() or "street" in geo.lower():
                risk += 0.5
            elif "city" in geo.lower():
                risk += 0.3
            elif "county" in geo.lower():
                risk += 0.1
        
        # Age specificity
        if persona.demographics.age is not None:
            risk += 0.2
        elif persona.demographics.age_range:
            risk += 0.1
        
        return min(risk, 1.0)
    
    def _calculate_demographic_concentration(self, personas: List['Persona']) -> float:  # type: ignore
        """Calculate overall demographic concentration risk."""
        if not personas:
            return 0.0
        
        # Analyze gender distribution
        genders = [p.demographics.gender for p in personas if p.demographics.gender]
        gender_counts = Counter(genders)
        
        # Analyze ethnicity distribution
        ethnicities = [p.demographics.ethnicity for p in personas if p.demographics.ethnicity]
        ethnicity_counts = Counter(ethnicities)
        
        # Calculate concentration (Herfindahl index)
        def herfindahl(counts):
            total = sum(counts.values())
            if total == 0:
                return 0.0
            return sum((count / total) ** 2 for count in counts.values())
        
        gender_concentration = herfindahl(gender_counts)
        ethnicity_concentration = herfindahl(ethnicity_counts)
        
        # Higher concentration = higher risk of rare combinations
        return (gender_concentration + ethnicity_concentration) / 2
    
    def _calculate_event_pattern_concentration(self, personas: List['Persona']) -> float:  # type: ignore
        """Calculate event pattern concentration risk."""
        if not personas:
            return 0.0
        
        # Count unique event patterns
        pattern_counts = Counter()
        for persona in personas:
            pattern = tuple(sorted(persona.event_patterns.event_types))
            pattern_counts[pattern] += 1
        
        # Calculate concentration
        total = len(personas)
        concentration = sum((count / total) ** 2 for count in pattern_counts.values())
        
        return concentration
    
    def _estimate_external_linkage_risk(self, personas: List['Persona']) -> float:  # type: ignore
        """Estimate risk of linking to external datasets."""
        if not personas:
            return 0.0
        
        # Average external risk across all personas
        risks = [self._calculate_persona_external_risk(p) for p in personas]
        return float(np.mean(risks))
    
    def _calculate_k_anonymity(self, personas: List['Persona']) -> int:  # type: ignore
        """Calculate minimum group size (k-anonymity)."""
        if not personas:
            return 0
        
        # K-anonymity is the minimum merge count
        return min(p.merged_from for p in personas)
    
    def _generate_recommendation(
        self,
        population_risk: float,
        high_risk_personas: List[str],
        k_anonymity: int
    ) -> str:
        """Generate privacy recommendation based on risk assessment."""
        if population_risk <= POPULATION_RISK_THRESHOLDS["SAFE_FOR_PUBLIC_RELEASE"]:
            return "SAFE - Data meets public release standards"
        elif population_risk <= POPULATION_RISK_THRESHOLDS["SAFE_FOR_RESEARCH"]:
            return "SAFE_FOR_RESEARCH - Suitable for research use"
        elif k_anonymity < 5:
            return "INCREASE_MERGING - Group size too small, merge more people"
        elif len(high_risk_personas) > 0:
            return "INCREASE_NOISE - Apply more noise to high-risk personas"
        else:
            return "INCREASE_PROTECTION - Both merging and noise needed"


@dataclass
class PrivacyActions:
    """Actions to take for privacy protection."""
    increase_merging: bool = False
    increase_temporal_noise: bool = False
    generalize_demographics: bool = False
    add_synthetic_events: bool = False
    target_personas: List[str] = field(default_factory=list)
    recommended_merge_size: int = 5


class AutoPrivacyAdjustment:
    """
    Automatically adjust privacy protection when risk is too high.
    
    Implements escalating privacy protection strategies:
    1. Increase merging of similar people
    2. Add temporal noise to events
    3. Generalize demographics
    4. Add synthetic noise events
    """
    
    def __init__(self, privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM):
        self.privacy_level = privacy_level
        self.traceability = PopulationTraceability(privacy_level)
    
    def adjust_privacy_level(
        self,
        current_risk: RiskMetrics,
        target_risk: float
    ) -> PrivacyActions:
        """
        Determine privacy actions needed to meet target risk.
        
        Args:
            current_risk: Current risk metrics
            target_risk: Target population risk level
            
        Returns:
            PrivacyActions specifying what adjustments to make
        """
        if current_risk.population_average_risk <= target_risk:
            return PrivacyActions()  # No action needed
        
        return self._escalate_protection(current_risk, target_risk)
    
    def _escalate_protection(
        self,
        risk: RiskMetrics,
        target_risk: float
    ) -> PrivacyActions:
        """
        Escalate privacy protection using multiple strategies.
        
        Strategy order:
        1. Increase merging (k-anonymity)
        2. Add temporal noise
        3. Generalize demographics
        4. Add synthetic events
        """
        actions = PrivacyActions()
        
        risk_gap = risk.population_average_risk - target_risk
        
        # Strategy 1: Increase merging if k-anonymity is low
        if risk.k_anonymity < 5 or risk_gap > 0.1:
            actions.increase_merging = True
            actions.recommended_merge_size = max(5, risk.k_anonymity * 2)
        
        # Strategy 2: Add temporal noise for event patterns
        if risk.event_pattern_concentration_risk > 0.5:
            actions.increase_temporal_noise = True
        
        # Strategy 3: Generalize demographics for unique demographics
        if risk.demographic_concentration_risk > 0.5:
            actions.generalize_demographics = True
        
        # Strategy 4: Add synthetic events as last resort
        if risk_gap > 0.2:
            actions.add_synthetic_events = True
        
        # Target high-risk personas specifically
        actions.target_personas = risk.high_risk_personas
        
        return actions
