"""
Schema formatting for LLM consumption.
Single Responsibility: Formats schema information in user-friendly way.
"""
import json
from typing import Any, Dict

from backend.engine.requirements_agent.interfaces import ISchemaFormatter
from backend.engine.requirements_agent.spec_schema import SPEC_SCHEMA


class SchemaFormatter(ISchemaFormatter):
    """
    Formats schema information for LLM consumption.
    Follows Single Responsibility Principle.
    """
    
    def format_field(self, name: str, meta: Dict[str, Any]) -> str:
        """Generate a user-friendly description of a schema field for the LLM."""
        required = "REQUIRED" if meta.get("required") else "optional"
        ftype = meta.get("type")
        ask = meta.get("ask_user", "")
        example = meta.get("example", "")
        can_assume = meta.get("can_assume", False)

        text = [
            f"Field: {name}",
            f"  Status: {required}",
            f"  Type: {ftype}",
            f"  How to ask user: {ask}",
        ]
        
        if can_assume:
            text.append(f"  Note: You can make a reasonable assumption if the user doesn't specify.")
        
        if example:
            if isinstance(example, dict):
                text.append(f"  Example structure: {json.dumps(example, indent=4)}")
            else:
                text.append(f"  Example: {example}")

        if "structure" in meta:
            struct = meta["structure"]
            keys = list(struct.keys())
            
            # Create a more realistic example
            ex_obj = {}
            for k, t in struct.items():
                if t == "string":
                    ex_obj[k] = f"<{k}_value>"
                elif t == "integer":
                    ex_obj[k] = 1
                elif t == "boolean":
                    ex_obj[k] = True
                elif t == "list":
                    ex_obj[k] = []
                elif t == "dict":
                    ex_obj[k] = {}

            if ftype == "list":
                text.append(f"  Structure: This is a LIST where each item is an object with these keys: {keys}")
                text.append(f"  Example item: {json.dumps(ex_obj, indent=4)}")
            else:
                text.append(f"  Structure: This is an OBJECT with these keys: {keys}")
                text.append(f"  Example: {json.dumps(ex_obj, indent=4)}")

        return "\n".join(text)
    
    def format_schema(self) -> str:
        """Generate schema summary sorted by conversation priority."""
        fields = list(SPEC_SCHEMA.items())
        fields.sort(key=lambda x: x[1].get("conversation_priority", 999))
        return "\n\n".join(
            self.format_field(name, meta)
            for name, meta in fields
        )

