"""
PersonaTwinFactory: A Python framework for Digital Persona Twin development and data transparency.

This package provides tools for creating, managing, and ensuring transparency of digital persona twins.
"""

__version__ = "0.1.0"

from .persona_twin import PersonaTwin
from .data_models import PersonaAttributes, PersonaBehavior
from .transparency import TransparencyLogger, AuditLog

__all__ = [
    "PersonaTwin",
    "PersonaAttributes",
    "PersonaBehavior",
    "TransparencyLogger",
    "AuditLog",
]
