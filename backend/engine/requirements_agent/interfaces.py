"""
Interfaces and abstract classes for requirements agent components.
Follows Dependency Inversion Principle - depend on abstractions, not concretions.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IAssumptionStrategy(ABC):
    """
    Strategy interface for making assumptions about specific fields.
    Follows Strategy Pattern for Open/Closed Principle.
    """
    
    @abstractmethod
    def can_assume(self, field_name: str, spec: Dict[str, Any]) -> bool:
        """Check if this strategy can make an assumption for the given field."""
        pass
    
    @abstractmethod
    def assume(self, field_name: str, spec: Dict[str, Any]) -> Optional[Any]:
        """
        Make an assumption for the given field.
        Returns the assumed value, or None if no assumption can be made.
        """
        pass


class IConversationManager(ABC):
    """Interface for managing conversation flow and question prioritization."""
    
    @abstractmethod
    def determine_next_field(
        self, spec: Dict[str, Any], missing_required: List[str]
    ) -> Optional[str]:
        """Determine which field to ask about next."""
        pass
    
    @abstractmethod
    def get_assumable_fields(
        self, spec: Dict[str, Any]
    ) -> List[str]:
        """Get list of fields that can be assumed given current spec."""
        pass


class IPromptBuilder(ABC):
    """Interface for building prompts for LLM."""
    
    @abstractmethod
    def build_prompt(
        self,
        user_message: str,
        spec_dict: Dict[str, Any],
        history: List[Dict[str, str]],
        missing_required: List[str],
        next_field: Optional[str],
    ) -> str:
        """Build a prompt for the LLM."""
        pass


class ISchemaFormatter(ABC):
    """Interface for formatting schema information for LLM consumption."""
    
    @abstractmethod
    def format_field(self, name: str, meta: Dict[str, Any]) -> str:
        """Format a single field description."""
        pass
    
    @abstractmethod
    def format_schema(self) -> str:
        """Format the entire schema."""
        pass


class IFieldValidator(ABC):
    """Interface for validating field values."""
    
    @abstractmethod
    def is_empty(self, value: Any) -> bool:
        """Check if a field value is considered empty."""
        pass
    
    @abstractmethod
    def clean_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate updates, keeping only valid schema fields."""
        pass

