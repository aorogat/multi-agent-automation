"""
Prompt builder for LLM interactions.
Single Responsibility: Constructs prompts for the LLM.
"""
import json
from typing import Any, Dict, List, Optional

from backend.engine.requirements_agent.interfaces import IPromptBuilder, ISchemaFormatter
from backend.engine.requirements_agent.spec_schema import SPEC_SCHEMA


class PromptBuilder(IPromptBuilder):
    """
    Builds prompts for LLM interactions.
    Follows Single Responsibility Principle.
    Uses Dependency Injection for schema formatter.
    """
    
    def __init__(self, schema_formatter: ISchemaFormatter):
        self._schema_formatter = schema_formatter
    
    def build_prompt(
        self,
        user_message: str,
        spec_dict: Dict[str, Any],
        history: List[Dict[str, str]],
        missing_required: List[str],
        next_field: Optional[str],
    ) -> str:
        """Build a conversation-focused prompt for the LLM."""
        # Build history snippet
        history_text = self._build_history_text(history)
        
        schema_text = self._schema_formatter.format_schema()
        
        # Build context about what to focus on
        focus_text = self._build_focus_text(missing_required, next_field)

        return f"""
You are a friendly assistant helping someone build a multi-agent system. Your job is to:
1. Understand what they want in plain language
2. Ask ONE clear question at a time (no technical jargon)
3. Make reasonable assumptions when appropriate (especially for optional fields marked as assumable)
4. Extract information and update the specification
5. Be conversational and helpful

IMPORTANT RULES:
- Use plain language - NO technical terms like "topology", "pub/sub", "semantic search", etc.
- Instead say: "how should they be connected?", "how should they talk?", "should they remember things?"
- Ask ONE question at a time
- If a field is marked as "can_assume", you can make a reasonable assumption and mention it to the user
- Always be friendly and conversational
- If the user wants to change something, let them know they can modify it anytime

===================================================
SCHEMA (what information to collect):
===================================================
{schema_text}

===================================================
CURRENT SPECIFICATION:
===================================================
{json.dumps(spec_dict, indent=2)}

{focus_text}
===================================================
CONVERSATION HISTORY:
===================================================
{history_text}

===================================================
USER'S MESSAGE:
===================================================
{user_message}

===================================================
YOUR RESPONSE:
===================================================
You must respond with ONLY valid JSON in this format:
{{
  "updated_fields": {{
    // Only include fields that you extracted from the user's message
    // Use the exact field names from the schema
    // For structured fields (list/dict), provide complete valid JSON structures
    // Example: {{"task": "Customer service system"}}
    // Example: {{"agents": [{{"type": "Agent", "count": 5, "role": "Handles requests"}}]}}
  }},
  "reply": "Your friendly, conversational reply to the user. Use plain language, no jargon. If you made assumptions, mention them. If you updated fields, acknowledge it. Then ask ONE follow-up question if needed.",
  "follow_up_question": "ONE clear question in plain language to gather the next piece of information. Only include if you need more info. If the spec is complete or user is done, leave this empty."
}}

Remember:
- Extract information from the user's message into updated_fields
- Reply in a friendly, conversational way
- Ask ONE question at a time
- Use plain language - explain things simply
- If you made assumptions, tell the user what you assumed
""".strip()
    
    def _build_history_text(self, history: List[Dict[str, str]]) -> str:
        """Build conversation history text."""
        if history:
            history_text = "Recent conversation:\n"
            for msg in history[-8:]:  # Last 8 messages for context
                role = "User" if msg["role"] == "user" else "You"
                history_text += f"{role}: {msg['content']}\n"
            return history_text
        else:
            return "This is the start of the conversation.\n"
    
    def _build_focus_text(
        self, 
        missing_required: List[str], 
        next_field: Optional[str]
    ) -> str:
        """Build focus text for the prompt."""
        focus_text = ""
        if missing_required:
            focus_text = f"\nPRIORITY: Focus on collecting these REQUIRED fields: {', '.join(missing_required)}\n"
            if next_field:
                next_meta = SPEC_SCHEMA.get(next_field, {})
                focus_text += f"Next field to ask about: {next_field} - {next_meta.get('ask_user', '')}\n"
        elif next_field:
            next_meta = SPEC_SCHEMA.get(next_field, {})
            focus_text = f"\nSUGGESTION: Consider asking about: {next_field} - {next_meta.get('ask_user', '')}\n"
            focus_text += "This is optional, so you can suggest it or make a reasonable assumption.\n"
        return focus_text

