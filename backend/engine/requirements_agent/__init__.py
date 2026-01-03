"""
Requirements Agent Module.

Main exports for easy access to key components.
"""
from backend.engine.requirements_agent.agent import RequirementsAgent
from backend.engine.requirements_agent.spec_model import SpecificationModel
from backend.engine.requirements_agent.spec_schema import SPEC_SCHEMA

__all__ = [
    "RequirementsAgent",
    "SpecificationModel",
    "SPEC_SCHEMA",
]

