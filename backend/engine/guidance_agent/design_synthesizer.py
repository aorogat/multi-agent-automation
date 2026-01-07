"""
Design Synthesizer - Orchestrates the 9-step design process.

This module coordinates the sequential execution of all 9 design prompts,
collects responses from the LLM, and structures them into a comprehensive
design report.
"""
from typing import Any, Dict, List, Optional

from backend.engine.guidance_agent.prompt_templates import PromptTemplates
from backend.engine.guidance_agent.output_validator import OutputValidator
from backend.engine.guidance_agent.framework_comparison import FrameworkComparison
from backend.llm.llm_manager import LLM
from backend.utils.logger import debug


class DesignSynthesizer:
    """
    Orchestrates the multi-step design synthesis process.
    
    Executes all 9 prompts sequentially, collecting responses and
    building a comprehensive design report.
    """
    
    def __init__(self, strict_validation: bool = True):
        """
        Initialize the design synthesizer.
        
        Args:
            strict_validation: If True, rejects invalid outputs. If False, attempts to fix them.
        """
        self.prompts = PromptTemplates()
        self.validator = OutputValidator(strict_mode=strict_validation)
        self.framework_comparison = FrameworkComparison()
    
    def synthesize_design(
        self,
        requirements_spec: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute all 9 design prompts sequentially and build the report.
        
        Args:
            requirements_spec: The requirements specification from the requirements agent
            additional_context: Optional additional context or constraints
        
        Returns:
            A comprehensive design report dictionary with all sections
        """
        debug("DesignSynthesizer.synthesize_design() called")
        debug(f"Requirements spec keys: {list(requirements_spec.keys())}")
        
        # Merge additional context into requirements spec if provided
        if additional_context:
            requirements_spec = {**requirements_spec, **additional_context}
        
        # Store all design decisions with validation and confidence scores
        design_decisions = {}
        confidence_scores = {}
        validation_results = {}
        
        # Execute all 9 prompts sequentially
        prompt_functions = [
            (self.prompts.prompt_1_llm_backbone_selection, "llm_backbone"),
            (self.prompts.prompt_2_network_topology, "framework"),
            (self.prompts.prompt_3_memory_model, "memory"),
            (self.prompts.prompt_4_planning_module, "planning"),
            (self.prompts.prompt_5_agent_roles, "roles"),
            (self.prompts.prompt_6_tool_integration, "tools"),
            (self.prompts.prompt_7_environment_representation, "environment"),
            (self.prompts.prompt_8_execution_semantics, "execution"),
            (self.prompts.prompt_9_failure_handling, "failure_handling"),
        ]
        
        for prompt_func, feature_name in prompt_functions:
            section_name = feature_name  # For backward compatibility
            try:
                debug(f"Executing prompt: {section_name}")
                prompt = prompt_func(requirements_spec)
                
                # Call LLM
                response = LLM.generate_json(prompt)
                debug(f"Response for {section_name}: {response}")
                
                # Handle case where JSON parsing failed
                if "raw_output" in response:
                    # Try to parse the raw output
                    import json
                    import re
                    try:
                        raw_text = response["raw_output"]
                        # Remove markdown fences if present
                        if raw_text.startswith("```"):
                            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                            raw_text = re.sub(r"```\s*$", "", raw_text, flags=re.MULTILINE)
                            raw_text = raw_text.strip()
                        response = json.loads(raw_text)
                        debug(f"Successfully parsed raw_output for {section_name}")
                    except Exception as e:
                        debug(f"Failed to parse raw_output for {section_name}: {e}")
                        # Create a fallback structure in canonical format
                        response = {
                            "feature": feature_name,
                            "decision": {"error": "Failed to parse LLM response"},
                            "alternatives_considered": [],
                            "justification": {"summary": f"Error processing {section_name}: {str(e)}", "tradeoffs": []},
                            "limitations": [f"Failed to generate design: {str(e)}"],
                            "assumptions": [],
                            "evidence": [],
                            "risk_assessment": {"risk_level": "high", "primary_risks": ["Parsing failure"], "mitigations": []},
                            "confidence_score": 0.0
                        }
                
                # Validate the response against canonical schema
                is_valid, error_msg, validated_response = self.validator.validate(response, feature_name)
                
                if not is_valid:
                    debug(f"Validation failed for {section_name}: {error_msg}")
                    if validated_response is None:
                        # Could not fix, create error response
                        validated_response = {
                            "feature": feature_name,
                            "decision": {"error": f"Validation failed: {error_msg}"},
                            "alternatives_considered": [],
                            "justification": {"summary": f"Validation error: {error_msg}", "tradeoffs": []},
                            "limitations": [f"Invalid output format: {error_msg}"],
                            "assumptions": [],
                            "evidence": [],
                            "risk_assessment": {"risk_level": "high", "primary_risks": ["Invalid output"], "mitigations": []},
                            "confidence_score": 0.0
                        }
                
                # Compute confidence score if not present
                if "confidence_score" not in validated_response or validated_response["confidence_score"] == 0.0:
                    validated_response["confidence_score"] = self.validator.compute_confidence_score(validated_response)
                
                # Store validated response
                design_decisions[section_name] = validated_response
                confidence_scores[section_name] = validated_response.get("confidence_score", 0.0)
                validation_results[section_name] = {
                    "is_valid": is_valid,
                    "error": error_msg if not is_valid else None
                }
                
                # Update requirements_spec with the new design decision for context in next prompts
                requirements_spec[f"_{section_name}_design"] = validated_response.get("decision", {})
                
            except Exception as e:
                debug(f"Error executing prompt {section_name}: {e}")
                design_decisions[section_name] = {
                    "feature": feature_name,
                    "decision": {"error": str(e)},
                    "alternatives_considered": [],
                    "justification": {"summary": f"Error: {str(e)}", "tradeoffs": []},
                    "limitations": [f"Exception occurred: {str(e)}"],
                    "assumptions": [],
                    "evidence": [],
                    "risk_assessment": {"risk_level": "high", "primary_risks": ["Exception"], "mitigations": []},
                    "confidence_score": 0.0
                }
                confidence_scores[section_name] = 0.0
                validation_results[section_name] = {"is_valid": False, "error": str(e)}
        
        # Build comprehensive report structure
        report = self._build_report(design_decisions, confidence_scores, validation_results, requirements_spec)
        
        return report
    
    def _build_report(
        self,
        design_decisions: Dict[str, Any],
        confidence_scores: Dict[str, float],
        validation_results: Dict[str, Dict[str, Any]],
        requirements_spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the final report structure from all design decisions.
        
        Args:
            design_decisions: Dictionary of all design decisions in canonical format
            confidence_scores: Dictionary of confidence scores per feature
            validation_results: Dictionary of validation results per feature
            requirements_spec: Original requirements specification
        
        Returns:
            Structured report dictionary
        """
        # Extract framework decision and generate comparison
        framework_decision = design_decisions.get("framework", {})
        framework_comparison = None
        recommended_framework = None
        
        if framework_decision and isinstance(framework_decision, dict):
            decision_data = framework_decision.get("decision", {})
            if isinstance(decision_data, dict) and "framework_type" in decision_data:
                framework_type = decision_data["framework_type"]
                recommended_framework = {
                    "name": framework_type,
                    "reasoning": framework_decision.get("justification", {}).get("summary", ""),
                    "confidence_score": confidence_scores.get("framework", 0.0)
                }
                # Generate framework comparison table
                framework_comparison = self.framework_comparison.compare_frameworks(
                    framework_type,
                    requirements_spec
                )
        
        # Build implementation steps from the design decisions
        steps_required = self._build_implementation_steps(design_decisions)
        
        # Build design choices dictionary from canonical format
        design_choices = {}
        feature_mapping = {
            "llm_backbone": "llm_backbone",
            "framework": "architecture",
            "memory": "memory",
            "planning": "planning",
            "roles": "agent_roles",
            "tools": "tools",
            "environment": "environment",
            "execution": "execution",
            "failure_handling": "failure_handling",
        }
        
        for canonical_key, report_key in feature_mapping.items():
            decision = design_decisions.get(canonical_key, {})
            if decision:
                design_choices[report_key] = {
                    "choice": decision.get("decision", {}),
                    "rationale": decision.get("justification", {}).get("summary", ""),
                    "alternatives_considered": decision.get("alternatives_considered", []),
                    "limitations": decision.get("limitations", []),
                    "assumptions": decision.get("assumptions", []),
                    "evidence": decision.get("evidence", []),
                    "risk_assessment": decision.get("risk_assessment", {}),
                    "confidence_score": confidence_scores.get(canonical_key, 0.0),
                    "validation_status": validation_results.get(canonical_key, {})
                }
        
        # Build architecture guidance
        framework_decision_data = design_decisions.get("framework", {}).get("decision", {})
        architecture_guidance = {
            "framework": framework_decision_data,
            "topology": framework_decision_data.get("topology", {}) if isinstance(framework_decision_data, dict) else {},
            "coordination": framework_decision_data.get("coordination_mechanisms", "") if isinstance(framework_decision_data, dict) else "",
            "execution_model": design_decisions.get("execution", {}).get("decision", {}),
            "framework_comparison": framework_comparison,
        }
        
        # Build implementation roadmap
        implementation_roadmap = self._build_implementation_roadmap(design_decisions)
        
        # Overall confidence score (average of all features)
        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            "steps_required": steps_required,
            "design_choices": design_choices,
            "recommended_framework": recommended_framework,
            "framework_comparison": framework_comparison,
            "architecture_guidance": architecture_guidance,
            "implementation_roadmap": implementation_roadmap,
            "detailed_design": design_decisions,  # Include all detailed design decisions in canonical format
            "confidence_scores": confidence_scores,  # Per-feature confidence scores
            "overall_confidence": overall_confidence,
            "validation_results": validation_results,  # Validation status per feature
            "requirements_spec": requirements_spec,  # Include original requirements
        }
    
    def _build_implementation_steps(self, design_decisions: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build a list of implementation steps from design decisions."""
        steps = [
            {
                "step": 1,
                "title": "Set up LLM Backbone",
                "description": "Configure and deploy the selected LLM models according to the backbone selection design."
            },
            {
                "step": 2,
                "title": "Implement Network Topology",
                "description": "Set up the framework architecture and communication topology as specified."
            },
            {
                "step": 3,
                "title": "Implement Memory System",
                "description": "Build the memory subsystem with the specified types, storage, and retrieval mechanisms."
            },
            {
                "step": 4,
                "title": "Implement Planning Module",
                "description": "Develop the planning and reasoning capabilities according to the planning design."
            },
            {
                "step": 5,
                "title": "Define Agent Roles",
                "description": "Implement each agent with its specified role, capabilities, and responsibilities."
            },
            {
                "step": 6,
                "title": "Integrate Tools",
                "description": "Set up and integrate external tools and APIs as specified in the tool integration design."
            },
            {
                "step": 7,
                "title": "Implement Environment (if needed)",
                "description": "Build the environment representation and grounding mechanisms if required."
            },
            {
                "step": 8,
                "title": "Implement Execution Semantics",
                "description": "Set up the execution model, control flow, and concurrency handling."
            },
            {
                "step": 9,
                "title": "Implement Failure Handling",
                "description": "Add failure detection, recovery mechanisms, coordination policies, and observability."
            },
        ]
        return steps
    
    def _build_implementation_roadmap(self, design_decisions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build a phased implementation roadmap."""
        return [
            {
                "phase": "Phase 1: Foundation",
                "description": "Set up core infrastructure",
                "steps": [
                    "Configure LLM backbone models",
                    "Set up basic framework architecture",
                    "Implement basic agent structure"
                ]
            },
            {
                "phase": "Phase 2: Core Capabilities",
                "description": "Implement core agent capabilities",
                "steps": [
                    "Implement memory system",
                    "Add planning module",
                    "Define agent roles and capabilities"
                ]
            },
            {
                "phase": "Phase 3: Integration",
                "description": "Integrate external components",
                "steps": [
                    "Integrate tools and APIs",
                    "Implement environment (if needed)",
                    "Set up execution semantics"
                ]
            },
            {
                "phase": "Phase 4: Reliability",
                "description": "Add reliability and observability",
                "steps": [
                    "Implement failure handling",
                    "Add monitoring and logging",
                    "Test and validate the system"
                ]
            },
        ]

