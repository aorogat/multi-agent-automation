"""
Field validation utilities.
Single Responsibility: Validates and cleans field values.
"""
from typing import Any, Dict

from backend.engine.requirements_agent.interfaces import IFieldValidator
from backend.engine.requirements_agent.spec_schema import SPEC_SCHEMA


class FieldValidator(IFieldValidator):
    """
    Validates and cleans field values.
    Follows Single Responsibility Principle.
    """
    
    def is_empty(self, value: Any) -> bool:
        """Check if a field value is considered empty."""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False
    
    def clean_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate updates, keeping only valid schema fields."""
        if not isinstance(updates, dict):
            return {}
        return {k: v for k, v in updates.items() if k in SPEC_SCHEMA}

