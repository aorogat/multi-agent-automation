# Guidance Agent

The Guidance Agent generates comprehensive design reports to help developers build multi-agent systems based on their requirements.

## Purpose

After the Requirements Agent collects the system requirements, the Guidance Agent analyzes these requirements through a structured 9-step design synthesis process and produces a detailed report that includes:

- **Steps Required**: Step-by-step implementation guide
- **Design Choices**: Key design decisions and their rationale
- **Recommended Framework**: Suggested multi-agent framework (e.g., LangGraph, AutoGen, CrewAI, etc.)
- **Architecture Guidance**: System architecture recommendations
- **Implementation Roadmap**: Phased approach to building the system
- **Detailed Design**: Complete design decisions from all 9 design aspects

## Design Synthesis Process

The agent follows a structured 9-step process, each guided by a specialized prompt:

1. **LLM Backbone Model Selection**: Selects appropriate language models for agents
2. **Network Topology & Framework Architecture**: Determines framework (graph-based, role-based, or GABM) and communication topology
3. **Memory Model Design**: Designs memory subsystem (LTM, STM, Episodic)
4. **Planning Module Design**: Defines planning and reasoning capabilities
5. **Agent Roles and Capabilities Design**: Specifies each agent's role and responsibilities
6. **Tool Use and Integration Design**: Identifies external tools and integration mechanisms
7. **Environment Representation Design**: Defines environment model (if needed)
8. **Execution Semantics Design**: Specifies execution model (synchronous/asynchronous)
9. **Failure Handling and Coordination Policy**: Designs error handling and observability

Each step uses the LLM to generate design decisions based on the requirements and previous design choices, ensuring a coherent and comprehensive design.

## Structure

- `agent.py`: Main orchestrator for report generation
- `design_synthesizer.py`: Orchestrates the 9-step design process
- `prompt_templates.py`: Contains all 9 structured prompts
- `report_generator.py`: Generates JSON and PDF reports

## Usage

```python
from backend.engine.guidance_agent import GuidanceAgent

agent = GuidanceAgent()
report = agent.generate_report(
    requirements_spec=requirements_dict,
    additional_context=optional_context,
    base_filename="my_report"  # Optional
)

# Access the report data
report_data = report["report_data"]
json_path = report["json_path"]
pdf_path = report["pdf_path"]
```

## Input

The agent expects a requirements specification dictionary (from the Requirements Agent) containing information about:
- System goals and tasks
- Agent roles and responsibilities
- Communication patterns
- Memory requirements
- Planning capabilities
- Topology preferences
- Constraints and performance targets
- etc.

## Output

The agent generates reports in **both JSON and PDF formats**:

- **JSON Report**: Machine-readable format with all report data including:
  - `steps_required`: Implementation steps
  - `design_choices`: All design decisions with rationale
  - `recommended_framework`: Framework recommendation
  - `architecture_guidance`: Architecture details
  - `implementation_roadmap`: Phased implementation plan
  - `detailed_design`: Complete design from all 9 prompts
  - `requirements_spec`: Original requirements

- **PDF Report**: Formatted document suitable for sharing and documentation with:
  - Executive summary
  - Recommended framework
  - Implementation steps
  - Design choices with explanations
  - Architecture guidance
  - Implementation roadmap
  - Detailed design decisions

The return value includes:
- `report_data`: The structured report content
- `json_path`: Path to the generated JSON file
- `pdf_path`: Path to the generated PDF file

Reports are saved to the `reports/` directory by default (configurable via `output_dir` parameter).

