"""
Prompt Templates for Multi-Agent System Design Guidance.

Contains all 9 structured prompts for guiding the Design Synthesizer LLM
through the MAS design process according to the v3.0.0 schema.
"""
import json
from typing import Any, Dict

from backend.engine.guidance_agent.design_rules import (
    GLOBAL_RULES,
    FEATURE_RULES,
    CANONICAL_JSON_SCHEMA,
)


class PromptTemplates:
    """Contains all prompt templates for the 9-step design process."""
    
    @staticmethod
    def build_context_preamble(
        requirements_spec: Dict[str, Any],
        feature_name: str = "",
        schema_version: str = "3.0.0"
    ) -> str:
        """Build the context preamble that appears in all prompts."""
        # Get feature-specific rules if available
        feature_rules = FEATURE_RULES.get(feature_name, "")
        
        rules_section = GLOBAL_RULES
        if feature_rules:
            rules_section += f"\n\n{feature_rules}"
        
        return f"""
{rules_section}

======================================================================
CONTEXT
======================================================================

You are a Design Synthesis Agent tasked with designing a Multi-Agent System (MAS) according to schema v{schema_version}.

CURRENT MAS REQUIREMENTS AND PARTIAL DESIGN:
{json.dumps(requirements_spec, indent=2)}

You have access to the full design schema and all previously filled fields. Your task is to produce detailed specifications for the current design aspect using the canonical JSON format below.
""".strip()
    
    @staticmethod
    def build_canonical_output_format(feature_name: str) -> str:
        """Build the canonical JSON output format specification."""
        return f"""
======================================================================
REQUIRED OUTPUT FORMAT (STRICT)
======================================================================

You MUST respond with ONLY valid JSON in this exact format:

{{
  "feature": "{feature_name}",
  "decision": {{
    // Feature-specific decision fields (see below)
  }},
  "alternatives_considered": [
    {{
      "option": "alternative_option_name",
      "rejected_because": "concrete empirical reason for rejection"
    }}
    // MUST include at least 2 alternatives
  ],
  "justification": {{
    "summary": "Human-readable summary explaining the decision",
    "tradeoffs": [
      "Trade-off 1: benefit vs cost",
      "Trade-off 2: benefit vs cost"
    ]
  }},
  "limitations": [
    "Explicit limitation 1",
    "Explicit limitation 2"
  ],
  "assumptions": [
    "Assumption 1",
    "Assumption 2"
  ],
  "evidence": [
    {{
      "source": "MASBench|MemoryAgentBench|experiment_name",
      "experiment": "specific experiment or study",
      "finding": "specific empirical finding",
      "implication": "what this means for the design"
    }}
    // MUST include at least one evidence source
  ],
  "risk_assessment": {{
    "risk_level": "low|medium|high",
    "primary_risks": [
      "Risk 1",
      "Risk 2"
    ],
    "mitigations": [
      "Mitigation 1",
      "Mitigation 2"
    ]
  }},
  "confidence_score": 0.0  // Your confidence in this decision (0.0 to 1.0)
}}

CRITICAL REQUIREMENTS:
1. You MUST compare at least 2 alternatives and explain why they were rejected
2. You MUST provide evidence from MASBench or empirical studies
3. You MUST explicitly state limitations and assumptions
4. You MUST NOT invent benchmarks or performance claims
5. You MUST separate what CAN be supported vs what CANNOT be supported
""".strip()
    
    @staticmethod
    def prompt_1_llm_backbone_selection(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 1: LLM Backbone Model Selection"""
        context = PromptTemplates.build_context_preamble(requirements_spec, "llm_backbone")
        output_format = PromptTemplates.build_canonical_output_format("llm_backbone")
        return f"""
{context}

======================================================================
PROMPT 1: LLM BACKBONE MODEL SELECTION
======================================================================

Goal: Select the most suitable backbone language model(s) for the agents, given the tasks and constraints, and justify the choice using empirical evidence.

TASK:
Choose an appropriate backbone LLM model (or models) for the agents. Consider:
- Model Choice: Identify which LLM or combination of LLMs (e.g. GPT-4, open-source models, domain-specific models)
- Model Assignments: If different agents have specialized roles, assign different models appropriately
- Configuration: Context length, knowledge cutoff, access method (API vs local)
- Performance & Budget: Align with user-specified latency targets and resource budgets

REQUIREMENTS:
- You MUST compare at least 2 alternative model choices
- You MUST justify using MASBench or empirical results
- You MUST state limitations (e.g., knowledge gaps, maintenance overhead)
- You MUST separate what CAN be supported vs what CANNOT be supported

{output_format}

For the "decision" field, include:
{{
  "primary_model": "model_name",
  "model_assignments": {{"agent_type": "model_name"}},
  "configuration": {{
    "context_length": "...",
    "access_method": "API|local",
    "cost_model": "..."
  }},
  "performance_targets": {{
    "latency": "...",
    "throughput": "..."
  }}
}}
""".strip()
    
    @staticmethod
    def prompt_2_network_topology(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 2: Network Topology & Framework Architecture"""
        context = PromptTemplates.build_context_preamble(requirements_spec, "framework")
        output_format = PromptTemplates.build_canonical_output_format("framework")
        return f"""
{context}

======================================================================
PROMPT 2: NETWORK TOPOLOGY & FRAMEWORK ARCHITECTURE
======================================================================

Goal: Determine the overall MAS framework architecture (graph-based, role-based, or GABM) and the communication topology among agents, then justify this choice against the alternatives using MASBench results.

TASK:
Choose one of the three framework architectures:
1. Graph-based: Lowest overhead, flexible message passing
2. Role-based: Best task decomposition, structured hierarchy
3. GABM: Simulation only, NOT for production

CRITICAL RULES:
- You MUST evaluate all three categories
- You MUST reject at least one category explicitly with empirical reason
- You MUST NOT recommend GABM unless environment grounding is required AND simulation is the primary goal
- You MUST justify scalability, latency, and throughput using MASBench results

REQUIREMENTS:
- Select the best-fitting architecture for the system
- Describe the communication topology in detail
- Explain coordination mechanisms
- Compare with rejected alternatives using empirical evidence

{output_format}

For the "decision" field, include:
{{
  "framework_type": "graph-based|role-based|GABM",
  "topology": {{
    "type": "hierarchy|mesh|star|pipeline|tree|chain|custom",
    "structure": "detailed description",
    "connection_rules": "rules for agent connections"
  }},
  "coordination_mechanisms": "how coordination/routing works",
  "scalability_analysis": "how it scales with number of agents",
  "latency_considerations": "latency implications"
}}
""".strip()
    
    @staticmethod
    def prompt_3_memory_model(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 3: Memory Model Design"""
        context = PromptTemplates.build_context_preamble(requirements_spec)
        return f"""
{context}

======================================================================
PROMPT 3: MEMORY MODEL DESIGN
======================================================================

Goal: Design the memory subsystem for the agents (types of memory, how it's organized and accessed) and explain how this supports the MAS's needs.

With the architecture decided, focus now on the Memory System of the MAS. The user's requirements and schema indicate how information should be retained and recalled by agents. Design the memory model in detail, covering the following:

Memory Types & Scope: Determine what types of memory each agent (or the system as a whole) will use. Consider Long-Term Memory (LTM) for persistent knowledge, Short-Term/Working Memory (STM/WM) for the current context or recent information, and Episodic Memory (EM) for event-specific recollections. Clearly specify which memories are per-agent and which are shared across the system.

Organization & Storage Mechanism: Describe how the memories are structured and stored. Options include a vector database (for semantic embedding storage of LTM items), a key-value store or dictionary for quick look-ups of facts, or simple in-memory lists of recent events. Indicate any strategies for memory management, such as summarization or forgetting.

Memory Retrieval & Usage: Explain how agents retrieve and use information from memory during conversations or planning. Will there be explicit retrieval queries (e.g., embedding similarity search when an agent faces a new question, retrieving top relevant past facts)? Does an agent have a dedicated memory-retrieval tool or module? For a shared memory (if any), detail how agents coordinate access.

Integration with LLM Context: Clarify how the memory content is fed into the LLM's context. If using a long context model, some LTM facts might be directly appended to prompts. If context is limited, outline a retrieval-augmented approach: e.g., the agent first performs a vector search in LTM for relevant facts, then injects those facts into its prompt before responding. The design should aim for efficiency (only retrieve what's likely needed) to meet performance targets.

Output Format: Provide the memory design specification (detailing types of memory, data structures, and retrieval process). Then give an explanation paragraph for the user, describing why this memory model was chosen. In the explanation, discuss how the memory system will improve the agents' performance and reference any MASBench findings about memory if available. Highlight trade-offs and note any limitations.

Respond in JSON format:
{{
  "memory_design": {{
    "memory_types": {{
      "LTM": "...",
      "STM": "...",
      "EM": "..."
    }},
    "organization": {{
      "per_agent": "...",
      "shared": "...",
      "storage_mechanism": "..."
    }},
    "retrieval_mechanism": "...",
    "llm_integration": "..."
  }},
  "explanation": "Justification paragraph explaining why this memory model was chosen..."
}}
""".strip()
    
    @staticmethod
    def prompt_4_planning_module(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 4: Planning Module Design"""
        context = PromptTemplates.build_context_preamble(requirements_spec)
        return f"""
{context}

======================================================================
PROMPT 4: PLANNING MODULE DESIGN
======================================================================

Goal: Define the planning and reasoning capabilities of the agents, including how far ahead they plan and how plans are represented, with justification.

Next, design the Planning module or strategy for the agents. The MAS should be capable of formulating and executing plans to achieve the user's goals. Describe in detail how the agents plan their actions, considering:

Planning Approach: Determine whether the agents use a reactive planning approach (planning step-by-step on the fly) or a more deliberative planning approach (formulating multi-step plans before execution). Indicate if the planning is centralized (e.g., only a coordinator agent plans for everyone) or decentralized (each agent plans its own actions with some coordination).

Horizon and Granularity: Specify the planning horizon – how far ahead and how detailed the plans are. Does the MAS plan only one step at a time (relying on feedback to adjust next steps), or does it create a full sequence of actions upfront? If the user's problem is complex (per the Task/Goal), a longer-horizon plan or even hierarchical planning (plans within plans) might be appropriate.

Plan Representation: Describe how plans are represented and updated. Are plans written in natural language descriptions, formal logic, pseudocode, or as a list of sub-tasks? Mention if there is a concept of plan memory or scratchpad where the plan is stored and potentially shared among agents.

Re-planning and Adaptation: Explain how the agents will react if the plan needs to change. Include failure triggers or new information triggers that cause the agents to re-plan.

Output Format: Present the planning design (approach, horizon, representation, coordination of plans) as part of the design spec. Then write an explanation paragraph for the user, clarifying why this planning method was chosen. Ground your explanation in the context and mention any relevant MASBench or research insights. Also, note any limitations.

Respond in JSON format:
{{
  "planning_design": {{
    "approach": "reactive|deliberative",
    "centralization": "centralized|decentralized",
    "horizon": "...",
    "granularity": "...",
    "representation": "...",
    "replanning_strategy": "..."
  }},
  "explanation": "Justification paragraph explaining why this planning method was chosen..."
}}
""".strip()
    
    @staticmethod
    def prompt_5_agent_roles(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 5: Agent Roles and Capabilities Design"""
        context = PromptTemplates.build_context_preamble(requirements_spec)
        return f"""
{context}

======================================================================
PROMPT 5: AGENT ROLES AND CAPABILITIES DESIGN
======================================================================

Goal: Define the role of each agent and their specific capabilities/responsibilities in the MAS, ensuring the team structure meets the requirements.

Now, delineate the Agent role structure and capabilities in the MAS. Using the list of agents and their high-level descriptions from the schema, produce a detailed design of each agent's role, including what each agent is responsible for and what skills or knowledge it possesses. Cover the following:

Role Definition: For each agent in the system, provide a clear definition of its role. Identify any specialized expertise or function it has. Ensure that these roles collectively cover all aspects of the user's Task/Goal without significant gaps or unnecessary overlaps.

Capabilities and Tools: For each agent, list its key capabilities, such as access to specific knowledge bases, ability to invoke certain tools, or particular methods it uses. Also note if an agent has greater computation budget or a dedicated LLM instance with certain parameters.

Interaction & Coordination Responsibilities: Explain how each role interacts with others. Clarify these interaction patterns relative to roles. This should be consistent with the previously defined topology.

Scalability & Constraints: Address the number of agents and scalability. If the user has a constraint on how many agents, ensure you meet that. Leverage MASBench insights if relevant: for example, note that while adding more specialized agents can increase parallelism, coordination overhead grows and can hit diminishing returns. The design should therefore find an optimal team size – justify that your chosen number of agents is appropriate.

Output Format: Provide a structured list or description of each agent and its role & capabilities as part of the design spec. Then include an explanation paragraph for the user describing why the agent roles are structured this way. In the explanation, emphasize how this role distribution satisfies the user's requirements and explain any design decisions.

Respond in JSON format:
{{
  "agent_roles": [
    {{
      "agent_type": "...",
      "role_definition": "...",
      "capabilities": ["..."],
      "tools": ["..."],
      "interaction_patterns": "..."
    }}
  ],
  "team_structure": {{
    "total_agents": 0,
    "rationale": "..."
  }},
  "explanation": "Justification paragraph explaining why the agent roles are structured this way..."
}}
""".strip()
    
    @staticmethod
    def prompt_6_tool_integration(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 6: Tool Use and Integration Design"""
        context = PromptTemplates.build_context_preamble(requirements_spec)
        return f"""
{context}

======================================================================
PROMPT 6: TOOL USE AND INTEGRATION DESIGN
======================================================================

Goal: Specify what external tools or APIs the agents will use, how those tools are integrated, and any constraints on tool usage, with justification.

Focus now on Tool usage and integration in the MAS. Many multi-agent systems augment their abilities by calling external tools or APIs (e.g., search engines, calculators, databases). Identify which tools will be used and design how agents interact with them, given the user's requirements and any provided constraints. Include the following details:

Tool Identification: List any specific tools or external systems that are necessary to achieve the task. Align this with the Task/Goal.

Agent-Tool Assignment: For each tool, specify which agent(s) have access to it and under what conditions. Reflect any user constraints: for instance, if the user restricts internet access for security, then no web search should be included (or a local database alternative is used).

Integration Mechanism: Describe how the tool calls are integrated into the agent's workflow. Does the agent automatically invoke the tool when needed (autonomously deciding based on the conversation), or does it have to get permission from a coordinator agent? Specify if tool usage is synchronous or asynchronous. Also, note how results from tools are handled.

Error Handling & Limits: Address what happens if a tool call fails or the tool returns nothing useful. Maybe the agent will retry, or inform another agent (like the coordinator) of the failure. Also mention any usage limits in line with user's resource constraints.

MASBench Insights: Incorporate any relevant findings about tool use. For instance, note that MASBench and other studies have shown that agents augmented with tools or shortcuts can significantly outperform those without on complex tasks. Emphasize that the chosen tools are expected to boost performance based on such evidence.

Output Format: Present the tool integration design (which tools, which agents, how they call them) in the design spec format. Then provide an explanation paragraph for the user. In the explanation, justify why these tools were included and how they improve the system. Mention any expected overhead and why it's justified by the benefit.

Respond in JSON format:
{{
  "tools": [
    {{
      "tool_name": "...",
      "tool_type": "...",
      "assigned_agents": ["..."],
      "integration_mechanism": "...",
      "error_handling": "...",
      "usage_limits": "..."
    }}
  ],
  "explanation": "Justification paragraph explaining why these tools were included..."
}}
""".strip()
    
    @staticmethod
    def prompt_7_environment_representation(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 7: Environment Representation Design"""
        context = PromptTemplates.build_context_preamble(requirements_spec)
        return f"""
{context}

======================================================================
PROMPT 7: ENVIRONMENT REPRESENTATION DESIGN
======================================================================

Goal: Define how the environment or world is represented in the system (if applicable) and how agents perceive and interact with it, with justification.

Now, address the Environment representation and grounding aspect of the MAS. Not all systems have an environment simulation, but if the user's requirements involve agents interacting with a dynamic world (physical, virtual, or digital), specify how this is modeled. Cover these points:

Need for Environment: Clarify whether a simulated or explicit environment is needed for this MAS. If the agents are purely conversational (e.g., writing an essay, analyzing data), the "environment" might just be the information space or the user's input, and you can state that an explicit environment model is not necessary beyond the shared memory or context.

Environment Model: If applicable, describe how the environment is represented. For example, in a GABM approach, there could be a central "World State" or simulation managed by a special environment agent (Game Master). Describe the key state components that need to be tracked.

Grounding and Perception: Explain how agents perceive and influence the environment. Do agents query the environment state at regular intervals or get notified of changes? Can they directly modify it? If using a Game Master, detail how it converts agent actions into environment updates and generates observations for other agents.

No Environment Case: If you determine that no explicit environment module is needed, clearly state that and reason why. You might say, "All necessary state is maintained in the agents' memory and message exchanges, so we do not model an external environment."

Output Format: Provide the environment design portion of the spec (which may be a description of the simulated world state and the mediator agent, or a note that no separate environment is used). Then give an explanation paragraph for the user. In the explanation, state why this environment representation was chosen. Mention any trade-offs.

Respond in JSON format:
{{
  "environment_design": {{
    "needed": true/false,
    "model": "...",
    "state_components": ["..."],
    "perception_mechanism": "...",
    "modification_mechanism": "..."
  }},
  "explanation": "Justification paragraph explaining why this environment representation was chosen..."
}}
""".strip()
    
    @staticmethod
    def prompt_8_execution_semantics(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 8: Execution Semantics Design"""
        context = PromptTemplates.build_context_preamble(requirements_spec)
        return f"""
{context}

======================================================================
PROMPT 8: EXECUTION SEMANTICS DESIGN
======================================================================

Goal: Define how the agents execute (synchronously vs asynchronously, turn-taking, parallelism) and the overall execution cycle of the MAS, with justification.

Design the Execution semantics of the MAS – in other words, describe how the agents operate over time to carry out their tasks. This covers whether they work in turns or in parallel, how they schedule actions, and how the overall process flows. Please address:

Synchronous vs Asynchronous: Determine if agent interactions are synchronous (agents act one at a time in a fixed turn order or under a central clock) or asynchronous (agents act whenever they have something to do, possibly in parallel threads). Choose the approach that fits the scenario.

Execution Cycle & Control Flow: Describe the control flow of the system. For instance, how does the MAS start and proceed? If using synchronous rounds, define the order of turns. If using an asynchronous/event-driven model, explain how agents know when to act.

Concurrency and Resource Use: If agents run in parallel, mention how concurrency is handled in terms of computing resources (threads or processes) and data consistency (like how shared memory or environment state is updated without conflicts).

Temporal Planning: If relevant, note any timing or scheduling considerations. Include any mechanism to prevent infinite loops or deadlocks (like a max number of iterations or a watchdog that can break cycles if agents keep chatting without progress).

MASBench/Empirical Context: Tie in any known guidance. For instance, if MASBench results showed that asynchronous execution significantly reduced waiting time in scenarios with independent sub-tasks, mention that as a reason to go async.

Output Format: Provide the execution semantics design as part of the spec (detailing whether it's sync/async, the turn order or triggering mechanism, and any scheduling policies like timeouts or iteration limits). Then include an explanation paragraph for the user. In the explanation, justify why this execution mode was chosen. Mention any limitations or potential issues.

Respond in JSON format:
{{
  "execution_semantics": {{
    "mode": "synchronous|asynchronous",
    "control_flow": "...",
    "turn_order": "...",
    "concurrency_handling": "...",
    "temporal_planning": "...",
    "safeguards": "..."
  }},
  "explanation": "Justification paragraph explaining why this execution mode was chosen..."
}}
""".strip()
    
    @staticmethod
    def prompt_9_failure_handling(requirements_spec: Dict[str, Any]) -> str:
        """Prompt 9: Failure Handling and Coordination Policy"""
        context = PromptTemplates.build_context_preamble(requirements_spec)
        return f"""
{context}

======================================================================
PROMPT 9: FAILURE HANDLING AND COORDINATION POLICY
======================================================================

Goal: Describe how the MAS handles errors, unexpected outcomes, and coordinates agent behaviors (including conflict resolution and observability/monitoring), with justification.

Finally, design the Failure handling, coordination policy, and observability mechanisms for the MAS. This ensures the system is robust and its operations are transparent to the user. Include details on:

Failure Detection: Explain how the system detects when something goes wrong. This could be an agent failing to produce a result (e.g., timing out or returning an error), an agent producing an invalid or low-confidence output, or a conflict (two agents with inconsistent conclusions).

Recovery and Mitigation: For each type of failure, describe the recovery strategy. Examples: if an agent times out, the system could retry the action, or hand the task to another agent. If an agent returns an error, the coordinator might re-plan or ask a different agent to attempt an alternative approach. In case of conflicting answers from agents, maybe the coordinator or a designated "judge" agent reconciles them.

Coordination Policies: Detail any protocols or rules that govern agent interactions to prevent failures or conflicts in the first place. This can include priority rules, turn-order rules, locking mechanisms on shared memory, or negotiation/consensus strategies.

Observability & Logging: Describe how the system's process is made observable for monitoring and debugging. For example, will there be a central log of all agent messages and actions? Perhaps each agent keeps an audit trail of important decisions. Also consider metrics that the system tracks.

MASBench Insights: Infuse any empirical evidence on reliability measures. For example, note that coordination complexity is a known challenge and production systems often fail not due to poor reasoning but due to tool and coordination issues. Therefore, your design emphasizes robust coordination and careful tool usage checks.

Output Format: Provide the failure handling & coordination design as part of the spec (this can be in a structured list of "If X, then Y" policies, and descriptions of monitoring/logging features). Then write the explanation paragraph for the user. In the explanation, reassure the user by describing why these measures make the system reliable and transparent. Mention any limitation, such as slight overhead for monitoring or the fact that not all failures can be automatically fixed.

Respond in JSON format:
{{
  "failure_handling": {{
    "detection_mechanisms": ["..."],
    "recovery_strategies": {{
      "timeout": "...",
      "error": "...",
      "conflict": "..."
    }},
    "coordination_policies": ["..."],
    "observability": {{
      "logging": "...",
      "monitoring": "...",
      "metrics": ["..."]
    }}
  }},
  "explanation": "Justification paragraph explaining why these measures make the system reliable..."
}}
""".strip()

