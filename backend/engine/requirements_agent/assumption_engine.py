"""
Assumption engine that uses strategy pattern to make smart assumptions.
Single Responsibility: Orchestrates assumption strategies.
Open/Closed: Easy to add new assumption strategies without modifying this class.
"""
from typing import Any, Dict, List

from backend.engine.requirements_agent.interfaces import IAssumptionStrategy
from backend.engine.requirements_agent.field_validator import FieldValidator


class AssumptionEngine:
    """
    Engine for making smart assumptions about missing fields.
    Uses Strategy Pattern - easy to extend with new assumption strategies.
    Follows Open/Closed Principle.
    """
    
    def __init__(
        self,
        strategies: List[IAssumptionStrategy],
        field_validator: FieldValidator
    ):
        self._strategies = strategies
        self._field_validator = field_validator
    
    def make_assumptions(
        self, 
        spec: Dict[str, Any], 
        assumable_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Make reasonable assumptions for fields that can be assumed.
        Returns updates to apply.
        """
        updates = {}
        
        # Don't make assumptions if user hasn't provided basic info
        if not spec.get("agents"):
            return updates
        
        # Try each strategy for each assumable field
        for field_name in assumable_fields:
            current_value = spec.get(field_name)
            
            # Skip if field already has a value
            if not self._field_validator.is_empty(current_value):
                continue
            
            # Try to find a strategy that can assume this field
            for strategy in self._strategies:
                if strategy.can_assume(field_name, spec):
                    assumed_value = strategy.assume(field_name, spec)
                    if assumed_value is not None:
                        updates[field_name] = assumed_value
                        break  # Use first matching strategy
        
        return updates

