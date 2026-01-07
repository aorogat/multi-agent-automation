"""
Output Validator - Validates LLM outputs against canonical JSON schema.

This validator ensures that LLM responses conform to the strict
evidence-grounded design format and rejects invalid outputs.
"""
import json
from typing import Any, Dict, List, Optional, Tuple

from backend.utils.logger import debug


class OutputValidator:
    """
    Validates LLM outputs against the canonical JSON schema.
    
    Ensures all required fields are present and properly formatted.
    """
    
    REQUIRED_TOP_LEVEL_FIELDS = [
        "feature",
        "decision",
        "alternatives_considered",
        "justification",
        "limitations",
        "assumptions",
        "evidence",
        "risk_assessment",
    ]
    
    REQUIRED_JUSTIFICATION_FIELDS = ["summary", "tradeoffs"]
    REQUIRED_RISK_ASSESSMENT_FIELDS = ["risk_level", "primary_risks", "mitigations"]
    REQUIRED_EVIDENCE_FIELDS = ["source", "finding"]
    REQUIRED_ALTERNATIVE_FIELDS = ["option", "rejected_because"]
    
    VALID_RISK_LEVELS = ["low", "medium", "high"]
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize the validator.
        
        Args:
            strict_mode: If True, rejects outputs missing required fields.
                        If False, attempts to fix missing fields.
        """
        self.strict_mode = strict_mode
    
    def validate(
        self,
        output: Dict[str, Any],
        feature_name: str,
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate an LLM output against the canonical schema.
        
        Args:
            output: The LLM output dictionary to validate
            feature_name: The name of the feature being designed
        
        Returns:
            Tuple of (is_valid, error_message, fixed_output)
            - is_valid: True if output is valid
            - error_message: Error description if invalid, None if valid
            - fixed_output: Fixed output if fixable, None if not fixable
        """
        if not isinstance(output, dict):
            return False, "Output must be a dictionary", None
        
        # Check required top-level fields
        missing_fields = []
        for field in self.REQUIRED_TOP_LEVEL_FIELDS:
            if field not in output:
                missing_fields.append(field)
        
        if missing_fields:
            if self.strict_mode:
                return (
                    False,
                    f"Missing required fields: {', '.join(missing_fields)}",
                    None
                )
            else:
                # Attempt to fix
                fixed = output.copy()
                for field in missing_fields:
                    fixed[field] = self._get_default_value(field)
                output = fixed
        
        # Validate feature name matches
        if "feature" in output and output["feature"] != feature_name:
            debug(f"Feature name mismatch: expected {feature_name}, got {output['feature']}")
            # Don't fail on this, just log it
        
        # Validate decision object
        if not isinstance(output.get("decision"), dict):
            return False, "decision must be a dictionary", None
        
        # Validate alternatives_considered
        if not isinstance(output.get("alternatives_considered"), list):
            return False, "alternatives_considered must be a list", None
        
        for alt in output.get("alternatives_considered", []):
            if not isinstance(alt, dict):
                return False, "Each alternative must be a dictionary", None
            for field in self.REQUIRED_ALTERNATIVE_FIELDS:
                if field not in alt:
                    if self.strict_mode:
                        return False, f"Alternative missing field: {field}", None
                    else:
                        alt[field] = ""
        
        # Validate justification
        justification = output.get("justification", {})
        if not isinstance(justification, dict):
            return False, "justification must be a dictionary", None
        
        for field in self.REQUIRED_JUSTIFICATION_FIELDS:
            if field not in justification:
                if self.strict_mode:
                    return False, f"justification missing field: {field}", None
                else:
                    if field == "tradeoffs":
                        justification[field] = []
                    else:
                        justification[field] = ""
        
        # Validate limitations and assumptions are lists
        if not isinstance(output.get("limitations"), list):
            if self.strict_mode:
                return False, "limitations must be a list", None
            else:
                output["limitations"] = []
        
        if not isinstance(output.get("assumptions"), list):
            if self.strict_mode:
                return False, "assumptions must be a list", None
            else:
                output["assumptions"] = []
        
        # Validate evidence
        if not isinstance(output.get("evidence"), list):
            if self.strict_mode:
                return False, "evidence must be a list", None
            else:
                output["evidence"] = []
        
        for evidence in output.get("evidence", []):
            if not isinstance(evidence, dict):
                return False, "Each evidence item must be a dictionary", None
            for field in self.REQUIRED_EVIDENCE_FIELDS:
                if field not in evidence:
                    if self.strict_mode:
                        return False, f"Evidence missing field: {field}", None
                    else:
                        evidence[field] = ""
        
        # Validate risk_assessment
        risk_assessment = output.get("risk_assessment", {})
        if not isinstance(risk_assessment, dict):
            return False, "risk_assessment must be a dictionary", None
        
        for field in self.REQUIRED_RISK_ASSESSMENT_FIELDS:
            if field not in risk_assessment:
                if self.strict_mode:
                    return False, f"risk_assessment missing field: {field}", None
                else:
                    if field == "risk_level":
                        risk_assessment[field] = "medium"
                    else:
                        risk_assessment[field] = []
        
        # Validate risk_level value
        if risk_assessment.get("risk_level") not in self.VALID_RISK_LEVELS:
            if self.strict_mode:
                return False, f"risk_level must be one of: {', '.join(self.VALID_RISK_LEVELS)}", None
            else:
                risk_assessment["risk_level"] = "medium"
        
        # Validate confidence_score if present
        if "confidence_score" in output:
            score = output["confidence_score"]
            if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                if self.strict_mode:
                    return False, "confidence_score must be a float between 0.0 and 1.0", None
                else:
                    output["confidence_score"] = 0.5
        
        # Check minimum requirements
        if len(output.get("alternatives_considered", [])) < 1:
            if self.strict_mode:
                return False, "Must consider at least one alternative", None
            else:
                output["alternatives_considered"] = [
                    {
                        "option": "Not specified",
                        "rejected_because": "No alternative was explicitly considered"
                    }
                ]
        
        if len(output.get("evidence", [])) < 1:
            debug("Warning: No evidence provided, but allowing it (may be assumption-based)")
        
        return True, None, output
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for a missing field."""
        defaults = {
            "feature": "",
            "decision": {},
            "alternatives_considered": [],
            "justification": {"summary": "", "tradeoffs": []},
            "limitations": [],
            "assumptions": [],
            "evidence": [],
            "risk_assessment": {
                "risk_level": "medium",
                "primary_risks": [],
                "mitigations": []
            },
            "confidence_score": 0.5,
        }
        return defaults.get(field, None)
    
    def compute_confidence_score(self, output: Dict[str, Any]) -> float:
        """
        Compute a confidence score based on output quality.
        
        Factors:
        - Presence of evidence (higher = better)
        - Number of alternatives considered (more = better)
        - Completeness of justification (more complete = better)
        - Risk assessment quality
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # Evidence presence (40% weight)
        evidence = output.get("evidence", [])
        if len(evidence) > 0:
            score += 0.4
        elif len(evidence) == 0:
            # No evidence is a red flag, but not fatal
            score += 0.1
        
        # Alternatives considered (20% weight)
        alternatives = output.get("alternatives_considered", [])
        if len(alternatives) >= 2:
            score += 0.2
        elif len(alternatives) == 1:
            score += 0.1
        
        # Justification completeness (20% weight)
        justification = output.get("justification", {})
        if justification.get("summary") and justification.get("tradeoffs"):
            if len(justification.get("tradeoffs", [])) > 0:
                score += 0.2
            else:
                score += 0.1
        else:
            score += 0.05
        
        # Limitations and assumptions (10% weight)
        if len(output.get("limitations", [])) > 0:
            score += 0.05
        if len(output.get("assumptions", [])) > 0:
            score += 0.05
        
        # Risk assessment (10% weight)
        risk_assessment = output.get("risk_assessment", {})
        if risk_assessment.get("primary_risks") and risk_assessment.get("mitigations"):
            if len(risk_assessment.get("primary_risks", [])) > 0:
                score += 0.1
        
        return min(score, 1.0)

