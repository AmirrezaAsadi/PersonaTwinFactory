"""
Simple, user-friendly API for PersonaTwin.

This module provides easy-to-use functions for generating
privacy-protected personas without dealing with complex configuration.
"""

from typing import List, Optional, Dict, Any, Union
import pandas as pd

from personatwin.models import Person, Persona, Demographics, Event
from personatwin.pipeline import PersonaTwinPipeline, ProcessingConfig, ProcessingResult
from personatwin.privacy import PrivacyLevel
from personatwin.domains import Domain, DomainConfig, get_domain_config


def create_safe_personas(
    data: Union[List[Person], pd.DataFrame, List[Dict]],
    privacy_level: Union[str, PrivacyLevel] = "medium",
    domain: Union[str, Domain] = "custom",
    domain_config: Optional[DomainConfig] = None,
    target_risk: float = 0.05,
    enable_llm: bool = False,
    llm_api_key: Optional[str] = None,
) -> ProcessingResult:
    """
    Generate privacy-protected personas from people-events data.
    
    This is the main entry point for PersonaTwin. It takes your sensitive
    data and generates safe personas that preserve statistical utility while
    protecting privacy.
    
    Args:
        data: Input data as list of Person objects, DataFrame, or list of dicts
        privacy_level: "low", "medium", "high", or "maximum"
        domain: Domain type ("criminal_justice", "healthcare", "education", etc.)
        domain_config: Optional custom domain configuration
        target_risk: Target population re-identification risk (default 5%)
        enable_llm: Use LLM for intelligent privacy decisions
        llm_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        
    Returns:
        ProcessingResult with personas and risk metrics
        
    Example:
        >>> import personatwin as pt
        >>> import pandas as pd
        >>> 
        >>> # Load your sensitive data
        >>> df = pd.read_csv("sensitive_court_records.csv")
        >>> 
        >>> # Generate safe personas
        >>> result = pt.create_safe_personas(
        ...     data=df,
        ...     privacy_level="high",
        ...     domain="criminal_justice",
        ...     target_risk=0.01  # 1% risk for public release
        ... )
        >>> 
        >>> # Check results
        >>> print(f"Risk level: {result.risk_metrics.get_risk_level()}")
        >>> print(f"Safe for public: {result.is_safe_for_public()}")
        >>> 
        >>> # Export personas
        >>> personas_df = personas_to_dataframe(result.personas)
        >>> personas_df.to_csv("safe_personas.csv", index=False)
    """
    # Convert privacy level
    if isinstance(privacy_level, str):
        privacy_level = PrivacyLevel(privacy_level.lower())
    
    # Convert domain
    if isinstance(domain, str):
        domain = Domain(domain.lower())
    
    # Convert data to Person objects
    people = _convert_to_people(data)
    
    # Get domain config
    if domain_config is None:
        domain_config = get_domain_config(domain)
    
    # Create config
    config = ProcessingConfig(
        privacy_level=privacy_level,
        target_population_risk=target_risk,
        domain=domain,
        domain_config=domain_config,
        enable_llm=enable_llm,
    )
    
    if enable_llm and llm_api_key:
        from personatwin.llm_integration import LLMConfig
        config.llm_config = LLMConfig(api_key=llm_api_key)
    
    # Run pipeline
    pipeline = PersonaTwinPipeline(config)
    result = pipeline.process_dataset(people, target_risk)
    
    return result


def _convert_to_people(data: Union[List[Person], pd.DataFrame, List[Dict]]) -> List[Person]:
    """Convert various input formats to list of Person objects."""
    if isinstance(data, list):
        if len(data) == 0:
            return []
        
        if isinstance(data[0], Person):
            return data
        elif isinstance(data[0], dict):
            return [Person.from_dict(d) for d in data]
    
    elif isinstance(data, pd.DataFrame):
        return _dataframe_to_people(data)
    
    raise ValueError(f"Unsupported data type: {type(data)}")


def _dataframe_to_people(df: pd.DataFrame) -> List[Person]:
    """
    Convert DataFrame to list of Person objects.
    
    Expected DataFrame structure:
    - person_id: unique identifier
    - age, gender, ethnicity, geography: demographics
    - event_* columns: event information
    
    Or grouped format with multiple rows per person.
    """
    people = []
    
    # Check if this is a person-level or event-level DataFrame
    if 'event_id' in df.columns or 'event_type' in df.columns:
        # Event-level data: group by person
        if 'person_id' not in df.columns:
            raise ValueError("DataFrame must have 'person_id' column")
        
        for person_id, group in df.groupby('person_id'):
            # Extract demographics from first row
            first_row = group.iloc[0]
            demographics = Demographics(
                age=first_row.get('age'),
                gender=first_row.get('gender'),
                ethnicity=first_row.get('ethnicity'),
                geography=first_row.get('geography'),
            )
            
            # Extract events
            events = []
            for _, row in group.iterrows():
                if 'event_type' in row and row['event_type']:
                    event = Event(
                        event_id=row.get('event_id', ''),
                        date=pd.to_datetime(row.get('date', pd.Timestamp.now())),
                        event_type=str(row['event_type']),
                        outcome=row.get('outcome'),
                        location=row.get('location'),
                        details=row.get('details', {}),
                    )
                    events.append(event)
            
            person = Person(
                person_id=str(person_id),
                demographics=demographics,
                events=events
            )
            people.append(person)
    
    else:
        # Person-level data: one row per person
        for _, row in df.iterrows():
            demographics = Demographics(
                age=row.get('age'),
                gender=row.get('gender'),
                ethnicity=row.get('ethnicity'),
                geography=row.get('geography'),
            )
            
            person = Person(
                person_id=str(row['person_id']) if 'person_id' in row else str(row.name),
                demographics=demographics,
                events=[]
            )
            people.append(person)
    
    return people


def personas_to_dataframe(personas: List[Persona]) -> pd.DataFrame:
    """
    Convert personas to pandas DataFrame for easy analysis and export.
    
    Args:
        personas: List of Persona objects
        
    Returns:
        DataFrame with persona information
    """
    rows = []
    
    for persona in personas:
        base_row = {
            'persona_id': persona.persona_id,
            'merged_from': persona.merged_from,
            'age': persona.demographics.age,
            'age_range': persona.demographics.age_range,
            'gender': persona.demographics.gender,
            'ethnicity': persona.demographics.ethnicity,
            'geography': persona.demographics.geography,
            'confidence_level': persona.demographics.confidence_level,
            'traceability_score': persona.privacy_metadata.traceability_score,
            'noise_level': persona.privacy_metadata.noise_level,
            'generation_method': persona.privacy_metadata.generation_method,
            'event_count': len(persona.events),
            'event_types': ', '.join(persona.event_patterns.event_types),
        }
        rows.append(base_row)
    
    return pd.DataFrame(rows)


def personas_to_event_dataframe(personas: List[Persona]) -> pd.DataFrame:
    """
    Convert personas to event-level DataFrame.
    
    Each row is an event, with persona information included.
    
    Args:
        personas: List of Persona objects
        
    Returns:
        DataFrame with event-level data
    """
    rows = []
    
    for persona in personas:
        for event in persona.events:
            row = {
                'persona_id': persona.persona_id,
                'merged_from': persona.merged_from,
                'age_range': persona.demographics.age_range,
                'gender': persona.demographics.gender,
                'ethnicity': persona.demographics.ethnicity,
                'geography': persona.demographics.geography,
                'event_id': event.event_id,
                'event_date': event.date,
                'event_type': event.event_type,
                'outcome': event.outcome,
                'location': event.location,
                'category': event.category,
                'severity': event.severity,
            }
            rows.append(row)
    
    return pd.DataFrame(rows)


def load_criminal_justice_data(filepath: str) -> List[Person]:
    """
    Load criminal justice data from CSV file.
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        List of Person objects
    """
    df = pd.read_csv(filepath)
    return _dataframe_to_people(df)


def load_healthcare_data(filepath: str) -> List[Person]:
    """
    Load healthcare data from CSV file.
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        List of Person objects
    """
    df = pd.read_csv(filepath)
    return _dataframe_to_people(df)


def export_personas(personas: List[Persona], filepath: str, format: str = "csv") -> None:
    """
    Export personas to file.
    
    Args:
        personas: List of Persona objects
        filepath: Output file path
        format: "csv" or "json"
    """
    if format == "csv":
        df = personas_to_dataframe(personas)
        df.to_csv(filepath, index=False)
    elif format == "json":
        import json
        data = [p.to_dict() for p in personas]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    else:
        raise ValueError(f"Unsupported format: {format}")


def export_privacy_report(result: ProcessingResult, filepath: str) -> None:
    """
    Export privacy assessment report to HTML file.
    
    Args:
        result: ProcessingResult from create_safe_personas
        filepath: Output HTML file path
    """
    metrics = result.risk_metrics
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PersonaTwin Privacy Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; }}
            .metric {{ margin: 20px 0; padding: 15px; background-color: #f5f5f5; }}
            .risk-level {{ font-size: 24px; font-weight: bold; }}
            .safe {{ color: green; }}
            .warning {{ color: orange; }}
            .danger {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>PersonaTwin Privacy Assessment Report</h1>
        </div>
        
        <div class="metric">
            <h2>Overall Risk Level</h2>
            <p class="risk-level {_get_risk_class(metrics.get_risk_level())}">
                {metrics.get_risk_level()}
            </p>
            <p>Population Average Risk: {metrics.population_average_risk:.3%}</p>
        </div>
        
        <div class="metric">
            <h2>Privacy Metrics</h2>
            <ul>
                <li>K-Anonymity: {metrics.k_anonymity}</li>
                <li>High-Risk Personas: {len(metrics.high_risk_personas)}</li>
                <li>Demographic Concentration Risk: {metrics.demographic_concentration_risk:.3f}</li>
                <li>Event Pattern Risk: {metrics.event_pattern_concentration_risk:.3f}</li>
                <li>External Linkage Risk: {metrics.external_linkage_risk:.3f}</li>
            </ul>
        </div>
        
        <div class="metric">
            <h2>Recommendation</h2>
            <p>{metrics.recommendation}</p>
        </div>
        
        <div class="metric">
            <h2>Processing Information</h2>
            <ul>
                <li>Personas Generated: {len(result.personas)}</li>
                <li>Processing Iterations: {result.iterations}</li>
                <li>Status: {result.message}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(filepath, 'w') as f:
        f.write(html)


def _get_risk_class(risk_level: str) -> str:
    """Get CSS class for risk level."""
    if risk_level == "SAFE_FOR_PUBLIC_RELEASE":
        return "safe"
    elif risk_level == "SAFE_FOR_RESEARCH":
        return "safe"
    elif risk_level == "INTERNAL_USE_ONLY":
        return "warning"
    else:
        return "danger"
