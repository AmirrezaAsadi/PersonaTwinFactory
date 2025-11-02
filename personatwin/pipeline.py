"""
Main processing pipeline for PersonaTwin.

This module implements the end-to-end pipeline for generating
privacy-protected personas from sensitive people-events data.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

from personatwin.models import Person, Persona
from personatwin.privacy import (
    PrivacyLevel,
    RiskMetrics,
    PopulationTraceability,
    AutoPrivacyAdjustment,
)
from personatwin.merging import PeopleMerging
from personatwin.noise import EventNoiseGeneration
from personatwin.domains import DomainConfig, Domain, get_domain_config
from personatwin.llm_integration import LLMPrivacyAssistant, SyntheticEventGenerator, LLMConfig


logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for the processing pipeline."""
    privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM
    target_population_risk: float = 0.05  # 5% risk threshold
    domain: Domain = Domain.CUSTOM
    domain_config: Optional[DomainConfig] = None
    enable_llm: bool = False
    llm_config: Optional[LLMConfig] = None
    max_iterations: int = 5  # Maximum privacy adjustment iterations
    min_k_anonymity: int = 5


@dataclass
class ProcessingResult:
    """Result of the processing pipeline."""
    personas: List[Persona]
    risk_metrics: RiskMetrics
    iterations: int
    success: bool
    message: str
    
    def is_safe_for_public(self) -> bool:
        """Check if data is safe for public release."""
        return self.risk_metrics.get_risk_level() == "SAFE_FOR_PUBLIC_RELEASE"
    
    def is_safe_for_research(self) -> bool:
        """Check if data is safe for research use."""
        level = self.risk_metrics.get_risk_level()
        return level in ["SAFE_FOR_PUBLIC_RELEASE", "SAFE_FOR_RESEARCH"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_count": len(self.personas),
            "risk_metrics": self.risk_metrics.to_dict(),
            "iterations": self.iterations,
            "success": self.success,
            "message": self.message,
            "safe_for_public": self.is_safe_for_public(),
            "safe_for_research": self.is_safe_for_research(),
        }


class PersonaTwinPipeline:
    """
    End-to-end processing pipeline for generating privacy-protected personas.
    
    Steps:
    1. Data validation and cleaning
    2. Initial person merging
    3. Privacy risk calculation
    4. Iterative privacy adjustment
    5. Final validation
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
        # Get domain configuration
        if self.config.domain_config:
            self.domain_config = self.config.domain_config
        else:
            self.domain_config = get_domain_config(self.config.domain)
        
        # Initialize components
        self.merger = PeopleMerging(
            privacy_level=self.config.privacy_level,
            min_group_size=self.config.min_k_anonymity
        )
        self.noise_generator = EventNoiseGeneration(
            privacy_level=self.config.privacy_level
        )
        self.risk_calculator = PopulationTraceability(
            privacy_level=self.config.privacy_level
        )
        self.privacy_adjuster = AutoPrivacyAdjustment(
            privacy_level=self.config.privacy_level
        )
        
        # Optional LLM assistant
        if self.config.enable_llm and self.config.llm_config:
            self.llm_assistant = LLMPrivacyAssistant(self.config.llm_config)
            self.synthetic_generator = SyntheticEventGenerator(
                self.config.llm_config,
                self.domain_config
            )
        else:
            self.llm_assistant = None
            self.synthetic_generator = None
    
    def process_dataset(
        self,
        input_data: List[Person],
        target_risk_level: Optional[float] = None
    ) -> ProcessingResult:
        """
        Process dataset to generate privacy-protected personas.
        
        Args:
            input_data: List of original people with events
            target_risk_level: Target population risk (uses config if not provided)
            
        Returns:
            ProcessingResult with personas and metrics
        """
        if not input_data:
            return ProcessingResult(
                personas=[],
                risk_metrics=RiskMetrics(),
                iterations=0,
                success=False,
                message="No input data provided"
            )
        
        target_risk = target_risk_level or self.config.target_population_risk
        
        logger.info(f"Processing {len(input_data)} people...")
        logger.info(f"Domain: {self.domain_config.domain.value}")
        logger.info(f"Privacy level: {self.config.privacy_level.value}")
        logger.info(f"Target risk: {target_risk}")
        
        # Step 1: Validate data
        validated_data = self._validate_input(input_data)
        
        # Step 2: Initial merging
        personas = self.merger.merge_similar_people(validated_data)
        logger.info(f"Initial merge: {len(personas)} personas from {len(validated_data)} people")
        
        # Step 3: Add initial noise
        personas = self._add_noise_to_personas(personas)
        
        # Step 4: Calculate risk
        risk_metrics = self.risk_calculator.calculate_population_risk(personas, validated_data)
        logger.info(f"Initial risk: {risk_metrics.population_average_risk:.3f}")
        
        # Step 5: Iterative privacy adjustment
        iteration = 0
        while (risk_metrics.population_average_risk > target_risk and 
               iteration < self.config.max_iterations):
            iteration += 1
            logger.info(f"Iteration {iteration}: Adjusting privacy...")
            
            # Get recommended actions
            actions = self.privacy_adjuster.adjust_privacy_level(
                risk_metrics,
                target_risk
            )
            
            # Apply actions
            personas = self._apply_privacy_actions(personas, actions, validated_data)
            
            # Recalculate risk
            risk_metrics = self.risk_calculator.calculate_population_risk(personas, validated_data)
            logger.info(f"Risk after iteration {iteration}: {risk_metrics.population_average_risk:.3f}")
            
            # Check if we reached target
            if risk_metrics.population_average_risk <= target_risk:
                break
        
        # Determine success
        success = risk_metrics.population_average_risk <= target_risk
        if success:
            message = f"Successfully generated {len(personas)} personas with {risk_metrics.get_risk_level()} risk level"
        else:
            message = f"Generated {len(personas)} personas but target risk not achieved. Current: {risk_metrics.population_average_risk:.3f}, Target: {target_risk}"
        
        return ProcessingResult(
            personas=personas,
            risk_metrics=risk_metrics,
            iterations=iteration,
            success=success,
            message=message
        )
    
    def _validate_input(self, data: List[Person]) -> List[Person]:
        """Validate and clean input data."""
        validated = []
        
        for person in data:
            # Basic validation
            if not person.person_id:
                logger.warning(f"Skipping person with no ID")
                continue
            
            # Validate event types against domain config
            if self.domain_config.event_types:
                valid_events = [
                    e for e in person.events
                    if self.domain_config.is_valid_event_type(e.event_type)
                ]
                if len(valid_events) < len(person.events):
                    logger.warning(
                        f"Person {person.person_id}: filtered {len(person.events) - len(valid_events)} invalid events"
                    )
                person.events = valid_events
            
            validated.append(person)
        
        return validated
    
    def _add_noise_to_personas(self, personas: List[Persona]) -> List[Persona]:
        """Add privacy-protecting noise to personas."""
        noised_personas = []
        
        for persona in personas:
            # Add noise to events
            noised_events = self.noise_generator.add_noise_to_events(
                persona.events,
                valid_outcomes=self.domain_config.outcomes if self.domain_config.outcomes else None
            )
            
            # Generalize temporal precision
            noised_events = self.noise_generator.generalize_temporal_precision(
                noised_events,
                precision=self.domain_config.temporal_precision
            )
            
            # Update persona
            persona.events = noised_events
            persona.privacy_metadata.noise_level += 0.2  # Increment noise level
            
            noised_personas.append(persona)
        
        return noised_personas
    
    def _apply_privacy_actions(
        self,
        personas: List[Persona],
        actions,
        original_data: List[Person]
    ) -> List[Persona]:
        """Apply recommended privacy actions."""
        if actions.increase_merging:
            # Re-merge with stricter criteria
            logger.info(f"Increasing merge size to {actions.recommended_merge_size}")
            # Convert personas back to people for re-merging
            people = self._personas_to_people(personas)
            self.merger.min_group_size = actions.recommended_merge_size
            personas = self.merger.merge_similar_people(people)
        
        if actions.increase_temporal_noise:
            logger.info("Adding more temporal noise")
            personas = self._add_noise_to_personas(personas)
        
        if actions.generalize_demographics:
            logger.info("Generalizing demographics")
            personas = self._generalize_demographics(personas)
        
        if actions.add_synthetic_events and self.synthetic_generator:
            logger.info("Adding synthetic events")
            personas = self._add_synthetic_events(personas)
        
        return personas
    
    def _personas_to_people(self, personas: List[Persona]) -> List[Person]:
        """Convert personas back to people for re-processing."""
        people = []
        for persona in personas:
            # Create a representative person from the persona
            person = Person(
                person_id=persona.persona_id,
                demographics=persona.demographics,
                events=persona.events
            )
            people.append(person)
        return people
    
    def _generalize_demographics(self, personas: List[Persona]) -> List[Persona]:
        """Apply additional demographic generalization."""
        for persona in personas:
            demo = persona.demographics
            
            # Generalize age to range if not already
            if demo.age and not demo.age_range:
                demo.age_range = demo.generalize_age(bin_size=10)
                demo.age = None  # Remove exact age
            
            # Generalize geography
            if demo.geography and "," in demo.geography:
                parts = demo.geography.split(",")
                if len(parts) > 1:
                    demo.geography = parts[-2].strip()  # Keep only county/state
            
            # Reduce confidence
            demo.confidence_level *= 0.8
        
        return personas
    
    def _add_synthetic_events(self, personas: List[Persona]) -> List[Persona]:
        """Add synthetic events using LLM."""
        if not self.synthetic_generator:
            return personas
        
        for persona in personas:
            # Generate synthetic events
            synthetic_events = self.synthetic_generator.generate_contextual_events(
                person_demographics=persona.demographics,
                existing_events=persona.events,
                geographic_area=persona.demographics.geography or "Unknown",
                noise_level=persona.privacy_metadata.noise_level
            )
            
            # Add to persona
            if synthetic_events:
                persona.events.extend(synthetic_events)
                persona.privacy_metadata.noise_level += 0.3
        
        return personas
