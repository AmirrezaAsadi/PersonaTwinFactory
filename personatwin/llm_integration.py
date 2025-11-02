"""
LLM integration for intelligent privacy decisions and synthetic data generation.

This module uses Large Language Models to:
1. Analyze privacy risks and recommend actions
2. Generate realistic synthetic events for noise
3. Make intelligent privacy-utility trade-off decisions
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os

from personatwin.models import Event, Demographics, Person
from personatwin.privacy import RiskMetrics, PrivacyActions
from personatwin.domains import DomainConfig


try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class LLMConfig:
    """Configuration for LLM integration."""
    provider: str = "openai"  # "openai" or "anthropic"
    model: str = "gpt-4"  # or "claude-3-opus-20240229"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500
    enabled: bool = True


class LLMPrivacyAssistant:
    """
    Use LLM to make intelligent privacy decisions.
    
    Provides AI-driven recommendations for:
    - Privacy protection strategies
    - Synthetic event generation
    - Risk assessment and mitigation
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._default_config()
        self.client = self._initialize_client()
    
    def _default_config(self) -> LLMConfig:
        """Create default LLM configuration."""
        return LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            enabled=OPENAI_AVAILABLE or ANTHROPIC_AVAILABLE,
        )
    
    def _initialize_client(self) -> Optional[Any]:
        """Initialize the LLM client."""
        if not self.config.enabled:
            return None
        
        if self.config.provider == "openai" and OPENAI_AVAILABLE:
            if self.config.api_key:
                openai.api_key = self.config.api_key
            return openai
        elif self.config.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            if self.config.api_key:
                return anthropic.Anthropic(api_key=self.config.api_key)
        
        return None
    
    def analyze_risk_and_recommend(
        self,
        risk_metrics: RiskMetrics,
        data_characteristics: Dict[str, Any],
        domain_config: Optional[DomainConfig] = None
    ) -> PrivacyActions:
        """
        Analyze privacy risks and recommend actions using LLM.
        
        Args:
            risk_metrics: Current risk assessment
            data_characteristics: Information about the dataset
            domain_config: Domain-specific configuration
            
        Returns:
            Recommended privacy actions
        """
        if not self.client:
            # Fallback to rule-based recommendation
            return self._rule_based_recommendation(risk_metrics)
        
        try:
            prompt = self._create_risk_analysis_prompt(
                risk_metrics,
                data_characteristics,
                domain_config
            )
            
            response = self._call_llm(prompt)
            return self._parse_recommendation(response)
        
        except Exception as e:
            print(f"LLM call failed: {e}. Using rule-based fallback.")
            return self._rule_based_recommendation(risk_metrics)
    
    def _create_risk_analysis_prompt(
        self,
        risk_metrics: RiskMetrics,
        data_characteristics: Dict[str, Any],
        domain_config: Optional[DomainConfig]
    ) -> str:
        """Create prompt for risk analysis."""
        domain_name = domain_config.domain.value if domain_config else "unknown"
        
        prompt = f"""Analyze this people-events dataset's re-identification risk and recommend privacy protection strategies.

Dataset Domain: {domain_name}
Population size: {data_characteristics.get('n_people', 'unknown')}
Average risk: {risk_metrics.population_average_risk:.3f}
Risk level: {risk_metrics.get_risk_level()}
High-risk personas: {len(risk_metrics.high_risk_personas)}
K-anonymity: {risk_metrics.k_anonymity}
Demographic concentration risk: {risk_metrics.demographic_concentration_risk:.3f}
Event pattern concentration risk: {risk_metrics.event_pattern_concentration_risk:.3f}

Available Privacy Protection Strategies:
1. Increase merging (combine more people per persona)
   - Pros: Reduces uniqueness, improves k-anonymity
   - Cons: May reduce granularity of analysis

2. Add temporal noise (blur dates and sequences)
   - Pros: Preserves event types, reduces linkage risk
   - Cons: May affect temporal analysis

3. Geographic generalization (county vs city vs address)
   - Pros: Reduces location-based linkage
   - Cons: Limits geographic analysis

4. Synthetic event injection (add fake events)
   - Pros: Strong privacy protection
   - Cons: May distort patterns

Consider: We need to preserve key demographic and outcome patterns for {domain_name} analysis.

Provide a JSON response with:
{{
  "increase_merging": true/false,
  "recommended_merge_size": number,
  "increase_temporal_noise": true/false,
  "generalize_demographics": true/false,
  "add_synthetic_events": true/false,
  "reasoning": "explanation of recommendations"
}}"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        if self.config.provider == "openai" and OPENAI_AVAILABLE:
            response = self.client.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a privacy expert specializing in data anonymization and k-anonymity."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            return response.choices[0].message.content
        
        elif self.config.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
            )
            return response.content[0].text
        
        raise ValueError("No LLM provider available")
    
    def _parse_recommendation(self, response: str) -> PrivacyActions:
        """Parse LLM response into PrivacyActions."""
        import json
        
        try:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                return PrivacyActions(
                    increase_merging=data.get("increase_merging", False),
                    recommended_merge_size=data.get("recommended_merge_size", 5),
                    increase_temporal_noise=data.get("increase_temporal_noise", False),
                    generalize_demographics=data.get("generalize_demographics", False),
                    add_synthetic_events=data.get("add_synthetic_events", False),
                )
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
        
        # Fallback to rule-based
        return PrivacyActions()
    
    def _rule_based_recommendation(self, risk_metrics: RiskMetrics) -> PrivacyActions:
        """Fallback rule-based recommendation when LLM is unavailable."""
        actions = PrivacyActions()
        
        # If k-anonymity is low, increase merging
        if risk_metrics.k_anonymity < 5:
            actions.increase_merging = True
            actions.recommended_merge_size = 10
        
        # If demographic concentration is high, generalize
        if risk_metrics.demographic_concentration_risk > 0.5:
            actions.generalize_demographics = True
        
        # If event patterns are risky, add noise
        if risk_metrics.event_pattern_concentration_risk > 0.5:
            actions.increase_temporal_noise = True
        
        return actions


class SyntheticEventGenerator:
    """
    Generate realistic synthetic events using LLM knowledge.
    
    Used for adding privacy-protecting noise that maintains
    domain realism and statistical validity.
    """
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        domain_config: Optional[DomainConfig] = None
    ):
        self.llm_config = llm_config or LLMConfig()
        self.domain_config = domain_config
        self.assistant = LLMPrivacyAssistant(llm_config)
    
    def generate_contextual_events(
        self,
        person_demographics: Demographics,
        existing_events: List[Event],
        geographic_area: str,
        noise_level: float
    ) -> List[Event]:
        """
        Generate realistic synthetic events based on context.
        
        Args:
            person_demographics: Demographics of the person
            existing_events: Their existing events
            geographic_area: Geographic context
            noise_level: Amount of noise to add (0-1)
            
        Returns:
            List of synthetic events
        """
        if not self.assistant.client:
            # If LLM not available, return empty list
            return []
        
        if noise_level < 0.5:
            # Low noise level, don't add synthetic events
            return []
        
        try:
            prompt = self._create_synthetic_event_prompt(
                person_demographics,
                existing_events,
                geographic_area,
                noise_level
            )
            
            response = self.assistant._call_llm(prompt)
            return self._parse_synthetic_events(response)
        
        except Exception as e:
            print(f"Failed to generate synthetic events: {e}")
            return []
    
    def _create_synthetic_event_prompt(
        self,
        demographics: Demographics,
        events: List[Event],
        geography: str,
        noise_level: float
    ) -> str:
        """Create prompt for synthetic event generation."""
        domain_name = self.domain_config.domain.value if self.domain_config else "general"
        valid_event_types = self.domain_config.event_types if self.domain_config else []
        
        event_summary = ", ".join([e.event_type for e in events[:5]]) if events else "none"
        
        prompt = f"""Generate 1-2 realistic synthetic events for privacy protection in a {domain_name} dataset.

Person Context:
- Age: {demographics.age or demographics.age_range or 'unknown'}
- Gender: {demographics.gender or 'unknown'}
- Ethnicity: {demographics.ethnicity or 'unknown'}
- Geography: {geography}

Existing Events (sample): {event_summary}

Valid Event Types for {domain_name}: {', '.join(valid_event_types[:10]) if valid_event_types else 'any'}

Noise Level: {noise_level:.2f} (higher = more synthetic events needed)

Requirements:
- Generate events that fit this person's profile
- Events must be realistic for the {domain_name} domain
- Events should add privacy protection without distorting overall patterns
- Maintain domain-specific rules and constraints

Provide a JSON array of events:
[
  {{
    "event_type": "type",
    "outcome": "outcome",
    "date_offset_days": number (days from now, can be negative),
    "location": "{geography}",
    "details": {{"key": "value"}}
  }}
]"""
        
        return prompt
    
    def _parse_synthetic_events(self, response: str) -> List[Event]:
        """Parse LLM response into Event objects."""
        import json
        from datetime import datetime, timedelta
        import uuid
        
        try:
            # Extract JSON array
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                events = []
                for event_data in data:
                    date_offset = event_data.get("date_offset_days", 0)
                    event_date = datetime.now() + timedelta(days=date_offset)
                    
                    event = Event(
                        event_id=str(uuid.uuid4()),
                        date=event_date,
                        event_type=event_data.get("event_type", "unknown"),
                        outcome=event_data.get("outcome"),
                        details=event_data.get("details", {}),
                        location=event_data.get("location"),
                        category=self.domain_config.domain.value if self.domain_config else None,
                    )
                    events.append(event)
                
                return events
        
        except Exception as e:
            print(f"Failed to parse synthetic events: {e}")
        
        return []
