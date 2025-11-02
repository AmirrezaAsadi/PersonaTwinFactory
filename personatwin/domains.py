"""
Domain-specific configurations for PersonaTwin.

This module provides pre-configured event types, outcomes, and processing
rules for different domains. Users can use these or define their own.

Supported domains:
- Criminal Justice
- Healthcare
- Education
- Social Services
- Custom (user-defined)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from enum import Enum


class Domain(Enum):
    """Supported domains for people-events data."""
    CRIMINAL_JUSTICE = "criminal_justice"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SOCIAL_SERVICES = "social_services"
    EMPLOYMENT = "employment"
    CUSTOM = "custom"


@dataclass
class DomainConfig:
    """
    Configuration for a specific domain.
    
    Defines event types, outcomes, and processing rules specific to the domain.
    """
    domain: Domain
    event_types: List[str] = field(default_factory=list)
    outcomes: List[str] = field(default_factory=list)
    sensitive_fields: Set[str] = field(default_factory=set)
    preserve_fields: Set[str] = field(default_factory=set)
    temporal_precision: str = "month"  # "day", "week", "month", "quarter", "year"
    geographic_precision: str = "county"  # "address", "city", "county", "state", "country"
    
    def is_valid_event_type(self, event_type: str) -> bool:
        """Check if event type is valid for this domain."""
        if not self.event_types:
            return True  # No restrictions
        return event_type in self.event_types
    
    def is_valid_outcome(self, outcome: str) -> bool:
        """Check if outcome is valid for this domain."""
        if not self.outcomes:
            return True  # No restrictions
        return outcome in self.outcomes


# Criminal Justice Domain Configuration
CRIMINAL_JUSTICE_CONFIG = DomainConfig(
    domain=Domain.CRIMINAL_JUSTICE,
    event_types=[
        "arrest",
        "charge",
        "arraignment",
        "plea",
        "trial",
        "sentencing",
        "probation",
        "parole",
        "release",
        "violation",
        "appeal",
        "expungement",
        "bail_hearing",
        "pretrial_detention",
        "community_service",
    ],
    outcomes=[
        "guilty",
        "not_guilty",
        "dismissed",
        "plea_bargain",
        "convicted",
        "acquitted",
        "pending",
        "completed",
        "violated",
        "granted",
        "denied",
        "reduced",
        "enhanced",
    ],
    sensitive_fields={
        "case_number",
        "arrest_warrant",
        "judge_name",
        "prosecutor_name",
        "defense_attorney",
        "victim_name",
    },
    preserve_fields={
        "charge_severity",
        "sentence_length",
        "offense_category",
        "case_outcome",
    },
    temporal_precision="month",
    geographic_precision="county",
)


# Healthcare Domain Configuration
HEALTHCARE_CONFIG = DomainConfig(
    domain=Domain.HEALTHCARE,
    event_types=[
        "admission",
        "discharge",
        "visit",
        "diagnosis",
        "treatment",
        "prescription",
        "surgery",
        "test",
        "immunization",
        "emergency_visit",
        "telehealth",
        "referral",
        "follow_up",
    ],
    outcomes=[
        "recovered",
        "improved",
        "stable",
        "declined",
        "deceased",
        "transferred",
        "discharged",
        "readmitted",
        "completed",
        "ongoing",
        "cancelled",
    ],
    sensitive_fields={
        "patient_id",
        "mrn",
        "provider_name",
        "facility_name",
        "insurance_id",
        "diagnosis_code",
    },
    preserve_fields={
        "condition_type",
        "treatment_type",
        "outcome_status",
        "length_of_stay",
    },
    temporal_precision="week",
    geographic_precision="city",
)


# Education Domain Configuration
EDUCATION_CONFIG = DomainConfig(
    domain=Domain.EDUCATION,
    event_types=[
        "enrollment",
        "attendance",
        "assessment",
        "grade",
        "promotion",
        "graduation",
        "suspension",
        "expulsion",
        "transfer",
        "scholarship",
        "intervention",
        "parent_conference",
    ],
    outcomes=[
        "passed",
        "failed",
        "graduated",
        "promoted",
        "retained",
        "withdrawn",
        "completed",
        "in_progress",
        "excused",
        "unexcused",
        "awarded",
    ],
    sensitive_fields={
        "student_id",
        "teacher_name",
        "school_name",
        "guardian_name",
        "test_scores",
    },
    preserve_fields={
        "grade_level",
        "subject_area",
        "performance_level",
        "attendance_rate",
    },
    temporal_precision="month",
    geographic_precision="city",
)


# Social Services Domain Configuration
SOCIAL_SERVICES_CONFIG = DomainConfig(
    domain=Domain.SOCIAL_SERVICES,
    event_types=[
        "application",
        "eligibility_determination",
        "benefit_received",
        "case_opened",
        "case_closed",
        "home_visit",
        "assessment",
        "referral",
        "service_provided",
        "review",
        "appeal",
        "sanction",
    ],
    outcomes=[
        "approved",
        "denied",
        "pending",
        "completed",
        "ongoing",
        "closed",
        "successful",
        "unsuccessful",
        "compliant",
        "non_compliant",
        "appealed",
        "overturned",
    ],
    sensitive_fields={
        "case_number",
        "caseworker_name",
        "benefit_amount",
        "income",
        "household_members",
    },
    preserve_fields={
        "benefit_type",
        "service_category",
        "outcome_status",
        "duration",
    },
    temporal_precision="month",
    geographic_precision="county",
)


# Employment Domain Configuration
EMPLOYMENT_CONFIG = DomainConfig(
    domain=Domain.EMPLOYMENT,
    event_types=[
        "hire",
        "promotion",
        "demotion",
        "transfer",
        "performance_review",
        "training",
        "disciplinary_action",
        "leave",
        "return_from_leave",
        "resignation",
        "termination",
        "retirement",
    ],
    outcomes=[
        "successful",
        "unsuccessful",
        "completed",
        "ongoing",
        "approved",
        "denied",
        "voluntary",
        "involuntary",
        "promoted",
        "terminated",
    ],
    sensitive_fields={
        "employee_id",
        "ssn",
        "salary",
        "manager_name",
        "department",
    },
    preserve_fields={
        "job_category",
        "performance_rating",
        "tenure",
        "employment_status",
    },
    temporal_precision="month",
    geographic_precision="city",
)


# Registry of all configurations
DOMAIN_CONFIGS: Dict[Domain, DomainConfig] = {
    Domain.CRIMINAL_JUSTICE: CRIMINAL_JUSTICE_CONFIG,
    Domain.HEALTHCARE: HEALTHCARE_CONFIG,
    Domain.EDUCATION: EDUCATION_CONFIG,
    Domain.SOCIAL_SERVICES: SOCIAL_SERVICES_CONFIG,
    Domain.EMPLOYMENT: EMPLOYMENT_CONFIG,
}


def get_domain_config(domain: Domain) -> DomainConfig:
    """Get configuration for a specific domain."""
    return DOMAIN_CONFIGS.get(domain, DomainConfig(domain=Domain.CUSTOM))


def create_custom_config(
    event_types: List[str],
    outcomes: List[str],
    sensitive_fields: Set[str],
    preserve_fields: Set[str],
    temporal_precision: str = "month",
    geographic_precision: str = "county",
) -> DomainConfig:
    """
    Create a custom domain configuration.
    
    Args:
        event_types: List of valid event types for your domain
        outcomes: List of valid outcomes
        sensitive_fields: Fields that should be removed/anonymized
        preserve_fields: Fields that should be preserved for analysis
        temporal_precision: Level of temporal generalization
        geographic_precision: Level of geographic generalization
        
    Returns:
        Custom DomainConfig
    """
    return DomainConfig(
        domain=Domain.CUSTOM,
        event_types=event_types,
        outcomes=outcomes,
        sensitive_fields=sensitive_fields,
        preserve_fields=preserve_fields,
        temporal_precision=temporal_precision,
        geographic_precision=geographic_precision,
    )
