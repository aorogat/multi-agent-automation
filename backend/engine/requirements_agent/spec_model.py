# backend/engine/requirements_agent/spec_model.py

from typing import Any, Dict
from backend.engine.requirements_agent.spec_schema import SPEC_SCHEMA
import copy
import json


class SpecificationModel:
    """
    Schema-driven MAS requirement specification.
    
    IMPORTANT:
    - No parsing of LLM strings.
    - Structured list fields must ALREADY be valid JSON objects.
    - This class only validates & replaces according to schema rules.
    """

    def __init__(self):
        self.values: Dict[str, Any] = {}
        self._initialize_from_schema()

    # ---------------------------------------------------------
    # INITIALIZATION BASED ON SCHEMA
    # ---------------------------------------------------------
    def _initialize_from_schema(self):
        for field, meta in SPEC_SCHEMA.items():
            ftype = meta.get("type")

            if ftype == "string":
                self.values[field] = None
            elif ftype == "list":
                self.values[field] = []
            elif ftype == "dict":
                self.values[field] = {}
            else:
                self.values[field] = None

    # ---------------------------------------------------------
    # MAIN UPDATE FUNCTION  — STRICT JSON ACCEPTANCE
    # ---------------------------------------------------------
    def update(self, updates: Dict[str, Any]):
        """
        Update fields according to schema rules (no parsing).
        LLM must supply correct structure for structured list fields.
        """
        for key, new_value in updates.items():
            
            if key not in SPEC_SCHEMA:
                self.values[key] = new_value
                continue

            schema = SPEC_SCHEMA[key]
            ftype = schema["type"]

            # --------------------------
            # STRING
            # --------------------------
            if ftype == "string":
                self.values[key] = str(new_value).strip()

            # --------------------------
            # DICT (including structured dicts)
            # --------------------------
            elif ftype == "dict":
                if not isinstance(new_value, dict):
                    raise ValueError(f"Expected dict for field '{key}', got {type(new_value)}")
                
                # Validate structure if schema defines it
                if "structure" in schema:
                    for skey, stype in schema["structure"].items():
                        # Only validate required structure fields if they're present
                        # (optional fields may not be in new_value)
                        if skey in new_value:
                            # Basic type checking for structure fields
                            expected_type = stype
                            actual_value = new_value[skey]
                            
                            if expected_type == "string" and not isinstance(actual_value, str):
                                raise ValueError(
                                    f"Field '{key}.{skey}' expects string, got {type(actual_value)}"
                                )
                            elif expected_type == "integer" and not isinstance(actual_value, int):
                                raise ValueError(
                                    f"Field '{key}.{skey}' expects integer, got {type(actual_value)}"
                                )
                            elif expected_type == "boolean" and not isinstance(actual_value, bool):
                                raise ValueError(
                                    f"Field '{key}.{skey}' expects boolean, got {type(actual_value)}"
                                )
                            elif expected_type == "list" and not isinstance(actual_value, list):
                                raise ValueError(
                                    f"Field '{key}.{skey}' expects list, got {type(actual_value)}"
                                )
                            elif expected_type == "dict" and not isinstance(actual_value, dict):
                                raise ValueError(
                                    f"Field '{key}.{skey}' expects dict, got {type(actual_value)}"
                                )
                
                # Update dict (merge, not replace)
                self.values[key].update(new_value)

            # --------------------------
            # LIST (including structured lists)
            # --------------------------
            elif ftype == "list":

                # Strict schema: items must already match schema["structure"]
                if "structure" in schema:
                    if not isinstance(new_value, list):
                        raise ValueError(f"Field '{key}' expects a list of structured objects.")

                    # Validate structure
                    for obj in new_value:
                        if not isinstance(obj, dict):
                            raise ValueError(f"Field '{key}' expects structured dict items, got: {obj}")

                        # Validate types for fields that are present
                        # (fields may be optional, so we only validate when present)
                        for skey, stype in schema["structure"].items():
                            if skey in obj:
                                actual_value = obj[skey]
                                
                                if stype == "string" and not isinstance(actual_value, str):
                                    raise ValueError(
                                        f"Field '{key}[].{skey}' expects string, got {type(actual_value)}"
                                    )
                                elif stype == "integer" and not isinstance(actual_value, int):
                                    raise ValueError(
                                        f"Field '{key}[].{skey}' expects integer, got {type(actual_value)}"
                                    )
                                elif stype == "boolean" and not isinstance(actual_value, bool):
                                    raise ValueError(
                                        f"Field '{key}[].{skey}' expects boolean, got {type(actual_value)}"
                                    )
                                elif stype == "list" and not isinstance(actual_value, list):
                                    raise ValueError(
                                        f"Field '{key}[].{skey}' expects list, got {type(actual_value)}"
                                    )
                                elif stype == "dict" and not isinstance(actual_value, dict):
                                    raise ValueError(
                                        f"Field '{key}[].{skey}' expects dict, got {type(actual_value)}"
                                    )

                    # Overwrite or extend
                    if schema.get("replace_on_update", False):
                        self.values[key] = new_value
                    else:
                        self.values[key].extend(new_value)

                # NON-STRUCTURED LIST
                else:
                    if isinstance(new_value, list):
                        if schema.get("replace_on_update", False):
                            self.values[key] = new_value
                        else:
                            self.values[key].extend(new_value)
                    else:
                        if schema.get("replace_on_update", False):
                            self.values[key] = [new_value]
                        else:
                            self.values[key].append(new_value)

            # --------------------------
            # FALLBACK
            # --------------------------
            else:
                self.values[key] = new_value

    # ---------------------------------------------------------
    # REQUIRED FIELDS CHECK
    # ---------------------------------------------------------
    def missing_required_fields(self):
        missing = []
        for key, meta in SPEC_SCHEMA.items():
            if meta.get("required"):
                val = self.values.get(key)
                if val in [None, "", [], {}]:
                    missing.append(key)
        return missing

    # ---------------------------------------------------------
    # SERIALIZATION
    # ---------------------------------------------------------
    def to_dict(self):
        return copy.deepcopy(self.values)

    def __repr__(self):
        return json.dumps(self.values, indent=2)
