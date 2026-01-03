"""
Requirements Agent - Main orchestrator.
Follows SOLID principles:
- Single Responsibility: Orchestrates the requirements collection process
- Dependency Inversion: Depends on abstractions (interfaces)
- Open/Closed: Easy to extend with new strategies without modifying this class
"""
from typing import Any, Dict, List, Optional

from backend.engine.requirements_agent.spec_model import SpecificationModel
from backend.engine.requirements_agent.conversation_manager import ConversationManager
from backend.engine.requirements_agent.assumption_engine import AssumptionEngine
from backend.engine.requirements_agent.assumption_strategies import (
    CommunicationAssumptionStrategy,
    TopologyAssumptionStrategy,
    MemoryAssumptionStrategy,
    PlanningAssumptionStrategy,
)
from backend.engine.requirements_agent.prompt_builder import PromptBuilder
from backend.engine.requirements_agent.schema_formatter import SchemaFormatter
from backend.engine.requirements_agent.field_validator import FieldValidator
from backend.llm.llm_manager import LLM
from backend.utils.logger import debug


class RequirementsAgent:
    """
    Requirements collection agent that orchestrates the conversation.
    
    Follows SOLID principles:
    - Single Responsibility: Orchestrates the requirements collection process
    - Dependency Inversion: Uses dependency injection for all components
    - Open/Closed: Easy to extend with new strategies without modifying this class
    """
    
    def __init__(
        self,
        conversation_manager: Optional[ConversationManager] = None,
        assumption_engine: Optional[AssumptionEngine] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        field_validator: Optional[FieldValidator] = None,
    ):
        """
        Initialize with dependency injection.
        If components are not provided, creates default instances.
        This allows for easy testing and extension.
        """
        # Initialize dependencies with defaults if not provided (for backward compatibility)
        self._field_validator = field_validator or FieldValidator()
        self._conversation_manager = conversation_manager or ConversationManager(self._field_validator)
        
        # Initialize assumption engine with default strategies
        if assumption_engine is None:
            strategies = [
                CommunicationAssumptionStrategy(),
                TopologyAssumptionStrategy(),
                MemoryAssumptionStrategy(),
                PlanningAssumptionStrategy(),
            ]
            self._assumption_engine = AssumptionEngine(strategies, self._field_validator)
        else:
            self._assumption_engine = assumption_engine
        
        # Initialize prompt builder
        if prompt_builder is None:
            schema_formatter = SchemaFormatter()
            self._prompt_builder = PromptBuilder(schema_formatter)
        else:
            self._prompt_builder = prompt_builder

    # =====================================================================
    # PUBLIC ENTRY POINT
    # =====================================================================
    def run(
        self,
        user_message: str,
        current_spec: Any,
        history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user messages.
        Orchestrates the requirements collection process.
        """
        debug("RequirementsAgent.run() called")
        debug(f"User message: {user_message}")

        # Normalize spec -> model
        spec_model = self._build_spec_model(current_spec)
        spec_dict = spec_model.to_dict()
        missing_required = spec_model.missing_required_fields()

        debug(f"Current spec:\n{spec_dict}")
        debug(f"Missing required fields: {missing_required}")

        # Determine what to ask/suggest next
        next_field = self._conversation_manager.determine_next_field(
            spec_dict, missing_required
        )
        
        # Get assumable fields
        assumable_fields = self._conversation_manager.get_assumable_fields(spec_dict)
        
        # Make smart assumptions if appropriate
        assumed_updates = self._assumption_engine.make_assumptions(
            spec_dict, assumable_fields
        )
        if assumed_updates:
            debug(f"Making assumptions: {assumed_updates}")
            spec_model.update(assumed_updates)
            spec_dict = spec_model.to_dict()

        # Build conversation-focused prompt
        prompt = self._prompt_builder.build_prompt(
            user_message, spec_dict, history, missing_required, next_field
        )
        debug(f"RequirementsAgent prompt:\n{prompt}")

        # Call LLM
        llm_output = LLM.generate_json(prompt)
        debug(f"Raw LLM JSON output: {llm_output}")

        # Handle case where JSON parsing failed and raw_output is returned
        if "raw_output" in llm_output:
            # Try to parse the raw output as JSON
            import json
            import re
            try:
                raw_text = llm_output["raw_output"]
                # Remove markdown fences if present
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                    raw_text = re.sub(r"```\s*$", "", raw_text, flags=re.MULTILINE)
                    raw_text = raw_text.strip()
                # Try to extract JSON from the raw text
                llm_output = json.loads(raw_text)
                debug(f"Successfully parsed raw_output: {llm_output}")
            except Exception as e:
                debug(f"Failed to parse raw_output: {e}, raw_text: {llm_output.get('raw_output', '')[:200]}")
                # Fallback: return empty updates
                llm_output = {}

        updated_fields = llm_output.get("updated_fields", {}) or {}
        reply = llm_output.get("reply")
        follow_up = llm_output.get("follow_up_question")

        # Merge assumed updates with LLM updates
        if assumed_updates:
            updated_fields = {**assumed_updates, **updated_fields}

        # Fallback logic
        if not reply and follow_up:
            reply = follow_up
        if not reply:
            reply = "I'm here to help! What would you like to tell me about your system?"

        # Check if we still need more info
        spec_model.update(updated_fields)
        still_missing = spec_model.missing_required_fields()
        needs_more = bool(follow_up or updated_fields or still_missing)

        cleaned_updates = self._field_validator.clean_updates(updated_fields)
        debug(f"Cleaned updated_fields: {cleaned_updates}")
        debug(f"Reply to user: {reply}")
        debug(f"Needs_more: {needs_more}")

        return {
            "reply": reply,
            "updated_fields": cleaned_updates,
            "needs_more": needs_more,
        }

    # =====================================================================
    # INTERNAL HELPERS
    # =====================================================================

    def _build_spec_model(self, current_spec: Any) -> SpecificationModel:
        """Build a SpecificationModel from various input types."""
        model = SpecificationModel()
        if isinstance(current_spec, SpecificationModel):
            model.update(current_spec.to_dict())
        elif isinstance(current_spec, dict):
            model.update(current_spec)
        return model
