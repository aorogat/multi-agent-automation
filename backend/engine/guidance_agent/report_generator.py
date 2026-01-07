"""
Report Generator - Generates JSON and PDF reports from guidance data.

This module handles the generation of both JSON and PDF formatted reports
for the multi-agent system design guidance.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from backend.utils.logger import debug


class ReportGenerator:
    """
    Generates design reports in both JSON and PDF formats.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports. If None, uses current directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_json_report(
        self,
        report_data: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate a JSON report file.
        
        Args:
            report_data: The report data dictionary
            filename: Optional filename. If None, generates timestamped filename.
        
        Returns:
            Path to the generated JSON file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"guidance_report_{timestamp}.json"
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        debug(f"Generated JSON report: {filepath}")
        return str(filepath)
    
    def generate_pdf_report(
        self,
        report_data: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate a PDF report file.
        
        Args:
            report_data: The report data dictionary
            filename: Optional filename. If None, generates timestamped filename.
        
        Returns:
            Path to the generated PDF file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"guidance_report_{timestamp}.pdf"
        
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for PDF elements
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=30,
            alignment=1,  # Center alignment
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=12,
            spaceBefore=12,
        )
        subheading_style = ParagraphStyle(
            "CustomSubHeading",
            parent=styles["Heading3"],
            fontSize=14,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=8,
            spaceBefore=8,
        )
        normal_style = styles["Normal"]
        normal_style.fontSize = 11
        normal_style.leading = 14
        
        # Title
        story.append(Paragraph("Multi-Agent System Design Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Metadata
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Recommended Framework
        if report_data.get("recommended_framework"):
            story.append(Paragraph("Recommended Framework", heading_style))
            framework = report_data["recommended_framework"]
            if isinstance(framework, dict):
                framework_name = framework.get("name", "N/A")
                framework_reason = framework.get("reasoning", "")
                confidence = framework.get("confidence_score", 0.0)
                story.append(Paragraph(f"<b>{framework_name}</b>", normal_style))
                story.append(Paragraph(f"<b>Confidence Score:</b> {confidence:.2f}", normal_style))
                if framework_reason:
                    story.append(Paragraph(framework_reason, normal_style))
            else:
                story.append(Paragraph(str(framework), normal_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Framework Comparison Table
        if report_data.get("framework_comparison"):
            story.append(Paragraph("Framework Comparison", heading_style))
            comparison = report_data["framework_comparison"]
            if isinstance(comparison, dict) and "selected" in comparison:
                selected = comparison.get("selected", {})
                rejected = comparison.get("rejected", [])
                
                story.append(Paragraph(f"<b>Selected:</b> {selected.get('name', 'N/A')}", subheading_style))
                
                if rejected:
                    story.append(Paragraph("<b>Rejected Alternatives:</b>", subheading_style))
                    for alt in rejected:
                        alt_name = alt.get("name", "Unknown")
                        story.append(Paragraph(f"• {alt_name}", normal_style))
            
            story.append(Spacer(1, 0.2 * inch))
        
        # Overall Confidence Score
        if report_data.get("overall_confidence") is not None:
            story.append(Paragraph("Overall Design Confidence", heading_style))
            overall_conf = report_data["overall_confidence"]
            story.append(Paragraph(f"<b>Overall Confidence Score:</b> {overall_conf:.2f}", normal_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Steps Required
        if report_data.get("steps_required"):
            story.append(Paragraph("Implementation Steps", heading_style))
            steps = report_data["steps_required"]
            for i, step in enumerate(steps, 1):
                if isinstance(step, dict):
                    step_title = step.get("title", step.get("step", f"Step {i}"))
                    step_description = step.get("description", step.get("details", ""))
                    story.append(Paragraph(f"<b>Step {i}: {step_title}</b>", subheading_style))
                    if step_description:
                        story.append(Paragraph(step_description, normal_style))
                else:
                    story.append(Paragraph(f"<b>Step {i}:</b> {str(step)}", normal_style))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))
        
        # Design Choices
        if report_data.get("design_choices"):
            story.append(Paragraph("Design Choices", heading_style))
            design_choices = report_data["design_choices"]
            if isinstance(design_choices, dict):
                for choice_name, choice_details in design_choices.items():
                    story.append(Paragraph(f"<b>{choice_name}</b>", subheading_style))
                    if isinstance(choice_details, dict):
                        choice_value = choice_details.get("choice", choice_details.get("value", ""))
                        choice_rationale = choice_details.get("rationale", choice_details.get("reasoning", ""))
                        if choice_value:
                            story.append(Paragraph(f"<b>Choice:</b> {choice_value}", normal_style))
                        if choice_rationale:
                            story.append(Paragraph(f"<b>Rationale:</b> {choice_rationale}", normal_style))
                    else:
                        story.append(Paragraph(str(choice_details), normal_style))
                    story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))
        
        # Architecture Guidance
        if report_data.get("architecture_guidance"):
            story.append(Paragraph("Architecture Guidance", heading_style))
            arch_guidance = report_data["architecture_guidance"]
            if isinstance(arch_guidance, dict):
                for section_name, section_content in arch_guidance.items():
                    story.append(Paragraph(f"<b>{section_name}</b>", subheading_style))
                    if isinstance(section_content, (list, dict)):
                        content_text = json.dumps(section_content, indent=2)
                        story.append(Paragraph(content_text.replace("\n", "<br/>"), normal_style))
                    else:
                        story.append(Paragraph(str(section_content), normal_style))
                    story.append(Spacer(1, 0.1 * inch))
            else:
                story.append(Paragraph(str(arch_guidance), normal_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Implementation Roadmap
        if report_data.get("implementation_roadmap"):
            story.append(Paragraph("Implementation Roadmap", heading_style))
            roadmap = report_data["implementation_roadmap"]
            if isinstance(roadmap, list):
                for phase in roadmap:
                    if isinstance(phase, dict):
                        phase_name = phase.get("phase", phase.get("name", "Phase"))
                        phase_desc = phase.get("description", "")
                        phase_steps = phase.get("steps", phase.get("tasks", []))
                        story.append(Paragraph(f"<b>{phase_name}</b>", subheading_style))
                        if phase_desc:
                            story.append(Paragraph(phase_desc, normal_style))
                        if isinstance(phase_steps, list):
                            for step in phase_steps:
                                story.append(Paragraph(f"• {step}", normal_style))
                        story.append(Spacer(1, 0.1 * inch))
                    else:
                        story.append(Paragraph(f"• {str(phase)}", normal_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Detailed Design (if available)
        if report_data.get("detailed_design"):
            story.append(Paragraph("Detailed Design Decisions", heading_style))
            detailed_design = report_data["detailed_design"]
            if isinstance(detailed_design, dict):
                design_sections = [
                    ("LLM Backbone Selection", "llm_backbone"),
                    ("Network Topology & Framework", "network_topology"),
                    ("Memory Model", "memory_model"),
                    ("Planning Module", "planning_module"),
                    ("Agent Roles", "agent_roles"),
                    ("Tool Integration", "tool_integration"),
                    ("Environment Representation", "environment"),
                    ("Execution Semantics", "execution_semantics"),
                    ("Failure Handling", "failure_handling"),
                ]
                
                for section_title, section_key in design_sections:
                    if section_key in detailed_design:
                        story.append(Paragraph(f"<b>{section_title}</b>", subheading_style))
                        section_data = detailed_design[section_key]
                        if isinstance(section_data, dict):
                            # Format dict as readable text
                            for key, value in section_data.items():
                                if key != "error":  # Skip error keys
                                    value_str = json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value)
                                    # Truncate very long values
                                    if len(value_str) > 500:
                                        value_str = value_str[:500] + "..."
                                    story.append(Paragraph(f"<b>{key}:</b> {value_str}", normal_style))
                        else:
                            section_str = json.dumps(section_data, indent=2) if isinstance(section_data, (dict, list)) else str(section_data)
                            if len(section_str) > 500:
                                section_str = section_str[:500] + "..."
                            story.append(Paragraph(section_str, normal_style))
                        story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))
        
        # Build PDF
        doc.build(story)
        
        debug(f"Generated PDF report: {filepath}")
        return str(filepath)
    
    def generate_both(
        self,
        report_data: Dict[str, Any],
        base_filename: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate both JSON and PDF reports.
        
        Args:
            report_data: The report data dictionary
            base_filename: Optional base filename (without extension).
                          If None, generates timestamped filename.
        
        Returns:
            Dictionary with 'json_path' and 'pdf_path' keys
        """
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"guidance_report_{timestamp}"
        
        json_path = self.generate_json_report(report_data, f"{base_filename}.json")
        pdf_path = self.generate_pdf_report(report_data, f"{base_filename}.pdf")
        
        return {
            "json_path": json_path,
            "pdf_path": pdf_path,
        }

