"""
Guidance Agent - Main orchestrator for generating design reports.

This agent analyzes the requirements collected by the requirements agent
and generates a comprehensive report to guide developers in building
their multi-agent system.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from backend.engine.guidance_agent.design_synthesizer import DesignSynthesizer
from backend.engine.guidance_agent.report_generator import ReportGenerator
from backend.utils.logger import debug


class GuidanceAgent:
    """
    Guidance agent that generates design reports for multi-agent systems.
    
    Takes the requirements specification and produces:
    - Implementation steps
    - Design choices and recommendations
    - Recommended multi-agent framework
    - Architecture guidance
    - Implementation roadmap
    
    Reports are generated in both JSON and PDF formats.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the guidance agent.
        
        Args:
            output_dir: Directory to save generated reports.
                       If None, uses 'reports' directory in project root.
        """
        if output_dir is None:
            # Default to reports directory in project root
            project_root = Path(__file__).parent.parent.parent.parent
            output_dir = str(project_root / "reports")
        
        self._report_generator = ReportGenerator(output_dir)
        self._design_synthesizer = DesignSynthesizer()
    
    def generate_report(
        self,
        requirements_spec: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None,
        base_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive design report based on requirements.
        
        The report is generated in both JSON and PDF formats.
        
        This method executes a 9-step design synthesis process:
        1. LLM Backbone Model Selection
        2. Network Topology & Framework Architecture
        3. Memory Model Design
        4. Planning Module Design
        5. Agent Roles and Capabilities Design
        6. Tool Use and Integration Design
        7. Environment Representation Design
        8. Execution Semantics Design
        9. Failure Handling and Coordination Policy
        
        Args:
            requirements_spec: The requirements specification collected
                              by the requirements agent
            additional_context: Optional additional context or constraints
            base_filename: Optional base filename (without extension) for reports.
                          If None, generates timestamped filename.
        
        Returns:
            A dictionary containing:
            - report_data: The report content with sections for:
              - steps_required: List of implementation steps
              - design_choices: Design decisions and rationale
              - recommended_framework: Suggested multi-agent framework
              - architecture_guidance: Architecture recommendations
              - implementation_roadmap: Phased implementation plan
              - detailed_design: All detailed design decisions from the 9 prompts
              - requirements_spec: Original requirements specification
            - json_path: Path to the generated JSON file
            - pdf_path: Path to the generated PDF file
        """
        debug("GuidanceAgent.generate_report() called")
        debug(f"Requirements spec: {requirements_spec}")
        
        # Synthesize the design using the 9-step process
        report_data = self._design_synthesizer.synthesize_design(
            requirements_spec,
            additional_context
        )
        
        debug(f"Generated report data with keys: {list(report_data.keys())}")
        
        # Generate both JSON and PDF reports
        file_paths = self._report_generator.generate_both(report_data, base_filename)
        
        return {
            "report_data": report_data,
            "json_path": file_paths["json_path"],
            "pdf_path": file_paths["pdf_path"],
        }

