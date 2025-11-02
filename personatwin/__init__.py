"""
PersonaTwin: Privacy-Preserving Persona Generation

A Python package for transforming sensitive people-events datasets into shareable
personas while preserving statistical utility and ensuring privacy.

Domain-agnostic system supporting:
- Criminal Justice
- Healthcare
- Education
- Social Services
- Employment
- Custom domains
"""

from personatwin.models import Person, Event, Persona, Demographics, EventPatterns, PrivacyMetadata
from personatwin.privacy import PrivacyLevel, RiskMetrics, PopulationTraceability
from personatwin.domains import Domain, DomainConfig, get_domain_config, create_custom_config

# Optional census module
try:
    from personatwin.census import CensusEnhancedPrivacyCalculator, CensusDataProvider, CensusData
    _CENSUS_AVAILABLE = True
except ImportError:
    _CENSUS_AVAILABLE = False
from personatwin.domains import (
    CRIMINAL_JUSTICE_CONFIG,
    HEALTHCARE_CONFIG,
    EDUCATION_CONFIG,
    SOCIAL_SERVICES_CONFIG,
    EMPLOYMENT_CONFIG,
)
from personatwin.merging import PeopleMerging
from personatwin.noise import EventNoiseGeneration, NoiseConfig
from personatwin.pipeline import PersonaTwinPipeline, ProcessingConfig, ProcessingResult
from personatwin.api import (
    create_safe_personas,
    personas_to_dataframe,
    personas_to_event_dataframe,
    load_criminal_justice_data,
    load_healthcare_data,
    export_personas,
    export_privacy_report,
)

__version__ = "0.1.0"
__author__ = "Amirreza Asadi"

__all__ = [
    # Core models
    "Person",
    "Event",
    "Persona",
    "Demographics",
    "EventPatterns",
    "PrivacyMetadata",
    # Privacy
    "PrivacyLevel",
    "RiskMetrics",
    "PopulationTraceability",
    # Domains
    "Domain",
    "DomainConfig",
    "get_domain_config",
    "create_custom_config",
    "CRIMINAL_JUSTICE_CONFIG",
    "HEALTHCARE_CONFIG",
    "EDUCATION_CONFIG",
    "SOCIAL_SERVICES_CONFIG",
    "EMPLOYMENT_CONFIG",
    # Processing
    "PeopleMerging",
    "EventNoiseGeneration",
    "NoiseConfig",
    "PersonaTwinPipeline",
    "ProcessingConfig",
    "ProcessingResult",
    # API
    "create_safe_personas",
    "personas_to_dataframe",
    "personas_to_event_dataframe",
    "load_criminal_justice_data",
    "load_healthcare_data",
    "export_personas",
    "export_privacy_report",
]
