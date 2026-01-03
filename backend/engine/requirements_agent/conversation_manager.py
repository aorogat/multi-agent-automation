"""
Conversation flow management.
Single Responsibility: Determines what to ask next based on priorities.
"""
from typing import Any, Dict, List, Optional

from backend.engine.requirements_agent.interfaces import IConversationManager
from backend.engine.requirements_agent.spec_schema import SPEC_SCHEMA
from backend.engine.requirements_agent.field_validator import FieldValidator


class ConversationManager(IConversationManager):
    """
    Manages conversation flow and question prioritization.
    Follows Single Responsibility Principle.
    """
    
    def __init__(self, field_validator: FieldValidator):
        self._field_validator = field_validator
    
    def determine_next_field(
        self, spec: Dict[str, Any], missing_required: List[str]
    ) -> Optional[str]:
        """
        Determine which field to ask about next.
        Prioritizes required fields, then optional assumable fields.
        """
        # First, prioritize missing required fields
        if missing_required:
            prioritized = sorted(
                missing_required,
                key=lambda f: SPEC_SCHEMA.get(f, {}).get("conversation_priority", 999)
            )
            return prioritized[0]
        
        # If all required fields are filled, suggest optional fields that make sense
        assumable_fields = self.get_assumable_fields(spec)
        
        if assumable_fields:
            prioritized = sorted(
                assumable_fields,
                key=lambda f: SPEC_SCHEMA.get(f, {}).get("conversation_priority", 999)
            )
            return prioritized[0]
        
        return None
    
    def get_assumable_fields(self, spec: Dict[str, Any]) -> List[str]:
        """
        Get list of fields that can be assumed given current spec.
        """
        assumable_fields = []
        for field_name, meta in SPEC_SCHEMA.items():
            if not meta.get("required"):
                current_value = spec.get(field_name)
                # Check if field is empty and can be assumed
                if (self._field_validator.is_empty(current_value) and 
                    meta.get("can_assume", False)):
                    # Check if we have enough context to assume it
                    if self._can_assume_field(field_name, spec):
                        assumable_fields.append(field_name)
        
        return assumable_fields
    
    def _can_assume_field(self, field_name: str, spec: Dict[str, Any]) -> bool:
        """
        Check if we have enough context to make an assumption about a field.
        """
        # We can assume fields if we have agents defined
        if field_name in ["communication", "topology", "memory", "planning"]:
            return bool(spec.get("agents"))
        return False

