from typing import Any, Dict, List
import json

from backend.engine.requirements_agent.spec_schema import SPEC_SCHEMA
from backend.engine.requirements_agent.spec_model import SpecificationModel
from backend.llm.llm_manager import LLM
from backend.utils.logger import debug


class RequirementsAgent:
    """
    Requirements collection agent that strictly enforces SPEC_SCHEMA.

    - Explains schema shape to the LLM (including nested structures).
    - Requires LLM to output updated_fields ONLY in valid JSON
      matching the schema types.
    - Requires the LLM to produce the next question explicitly.
    """

    def __init__(self):
        pass

    # =====================================================================
    # PUBLIC ENTRY POINT
    # =====================================================================
    def run(
        self,
        user_message: str,
        current_spec: Any,
        history: List[Dict[str, str]],
    ) -> Dict[str, Any]:

        debug("RequirementsAgent.run() called")
        debug(f"User message: {user_message}")

        # Normalize spec -> model
        spec_model = self._build_spec_model(current_spec)
        spec_dict = spec_model.to_dict()
        missing_required = spec_model.missing_required_fields()

        debug(f"Current spec:\n{json.dumps(spec_dict, indent=2)}")
        debug(f"Missing required fields: {missing_required}")

        # Build LLM prompt
        prompt = self._build_prompt(user_message, spec_dict, history, missing_required)
        debug(f"RequirementsAgent prompt:\n{prompt}")

        # Ask LLM — STRICT JSON expected
        llm_output = LLM.generate_json(prompt)
        debug(f"Raw LLM JSON output: {llm_output}")

        # Extract fields
        updated_fields = llm_output.get("updated_fields", {}) or {}
        reply = llm_output.get("reply")
        follow_up = llm_output.get("follow_up_question")

        # Fallback behavior
        if not reply and follow_up:
            reply = follow_up
        if not reply:
            reply = "Could you clarify what you want next?"

        needs_more = bool(follow_up or updated_fields or missing_required)

        cleaned_updates = self._clean_updates(updated_fields)
        debug(f"Cleaned updated_fields: {json.dumps(cleaned_updates, indent=2)}")
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
        """Ensure we return a SpecificationModel instance."""
        model = SpecificationModel()

        if isinstance(current_spec, SpecificationModel):
            model.update(current_spec.to_dict())
        elif isinstance(current_spec, dict):
            model.update(current_spec)

        return model

    # ---------------------------------------------------------------------
    # Convert schema → clear instructions for LLM
    # ---------------------------------------------------------------------
    def _schema_field_description(self, name: str, meta: Dict[str, Any]) -> str:
        required = "required" if meta.get("required") else "optional"
        ftype = meta.get("type")
        desc = meta.get("description", "")
        ask = meta.get("ask_user", "")
        example = meta.get("example", "")

        text = [
            f"- {name} ({required}, type={ftype}): {desc}",
            f"  Ask user: {ask}",
        ]
        if example:
            text.append(f"  Example: {example}")

        # STRUCTURED FIELD DESCRIPTION
        if "structure" in meta:
            struct = meta["structure"]
            keys = list(struct.keys())

            example_obj_parts = []
            for key, t in struct.items():
                placeholder = '"<string>"' if t == "string" else (
                    0 if t == "integer" else (
                        [] if t == "list" else "{}"
                    )
                )
                example_obj_parts.append(f'"{key}": {placeholder}')
            example_obj = "{ " + ", ".join(example_obj_parts) + " }"

            if ftype == "list":
                text.append(f"  This field is a LIST of OBJECTS with keys: {keys}")
                text.append(f"  Example value: [ {example_obj}, ... ]")
            else:
                text.append(f"  This field is an OBJECT with keys: {keys}")
                text.append(f"  Example value: {example_obj}")

        return "\n".join(text)

    def _schema_summary(self) -> str:
        blocks = [self._schema_field_description(name, meta) for name, meta in SPEC_SCHEMA.items()]
        return "\n\n".join(blocks)

    # ---------------------------------------------------------------------
    # BUILD STRICT JSON PROMPT
    # ---------------------------------------------------------------------
    def _build_prompt(
        self,
        user_message: str,
        spec_dict: Dict[str, Any],
        history: List[Dict[str, str]],
        missing_required: List[str],
    ) -> str:

        # Last few messages only
        history_text = ""
        for msg in history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        schema_text = self._schema_summary()

        return f"""
You are the Requirements Agent.

Your users are NOT technical. Use simple, friendly language.
But your JSON output MUST strictly follow the specification schema.

===================================================
SCHEMA (YOU MUST FOLLOW THIS EXACT SHAPE)
===================================================
{schema_text}

CRITICAL RULES:
- When a field defines a structured object (like agents: list of {{type, count}}),
  YOU MUST return valid JSON objects following exactly that structure.
- NEVER return strings like "200 students".
- ALWAYS return:
    "agents": [
        {{"type": "Student", "count": 200}},
        {{"type": "Teacher", "count": 10}}
    ]
- Never invent fields not in the schema.
- Never output malformed JSON.

===================================================
CURRENT SPECIFICATION:
{json.dumps(spec_dict, indent=2)}

MISSING REQUIRED FIELDS:
{missing_required}

CONVERSATION HISTORY:
{history_text}

USER MESSAGE:
{user_message}

===================================================
NOW PRODUCE STRICT JSON:
{{
  "updated_fields": {{
       // ONLY fields from SPEC_SCHEMA
       // MUST follow schema type exactly
  }},
  "reply": "Short natural message for the user.",
  "follow_up_question": "ONE short question the system should ask next, or null."
}}
===================================================
IF YOU ARE ASKING A QUESTION:
- Put it ONLY in follow_up_question.
- reply should acknowledge progress.

Output ONLY valid JSON.
""".strip()

    # ---------------------------------------------------------------------
    def _clean_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Keep only valid schema fields."""
        if not isinstance(updates, dict):
            return {}
        return {k: v for k, v in updates.items() if k in SPEC_SCHEMA}
