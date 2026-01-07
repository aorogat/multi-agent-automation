"""
Guidance Agent - Generates design reports for multi-agent systems.

This agent takes the requirements collected by the requirements agent
and produces a comprehensive report including:
- Steps required to build the system
- Design choices and recommendations
- Recommended multi-agent framework
- Architecture guidance
- Implementation roadmap
"""

from backend.engine.guidance_agent.agent import GuidanceAgent
from backend.engine.guidance_agent.report_generator import ReportGenerator
from backend.engine.guidance_agent.design_synthesizer import DesignSynthesizer
from backend.engine.guidance_agent.prompt_templates import PromptTemplates
from backend.engine.guidance_agent.output_validator import OutputValidator
from backend.engine.guidance_agent.framework_comparison import FrameworkComparison
from backend.engine.guidance_agent.design_rules import GLOBAL_RULES, FEATURE_RULES

__all__ = [
    "GuidanceAgent",
    "ReportGenerator",
    "DesignSynthesizer",
    "PromptTemplates",
    "OutputValidator",
    "FrameworkComparison",
    "GLOBAL_RULES",
    "FEATURE_RULES",
]

