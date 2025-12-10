SCHEMA_VERSION = "1.0.0"

SPEC_SCHEMA = {
    "task": {
        "type": "string",
        "required": True,
        "ask_user": "What should the multi-agent system do? (Describe the main task in simple words.)",
        "description": "A plain-language description of the system’s purpose."
    },

    "goal": {
        "type": "string",
        "required": True,
        "ask_user": "What is the goal of this system?",
        "description": "High-level purpose or expected outcome of the system."
    },

    "agents": {
        "type": "list",
        "required": True,
        "ask_user": "Which agents should exist? You may specify counts like '100 students, 10 teachers'.",
        "description": "List of agent definitions.",
        "structure": {
            "type": "string",        # e.g., 'Student', 'Teacher'
            "count": "integer",      # number of agents
        },
        "replace_on_update": True
    },

    "agent_purposes": {
        "type": "dict",
        "required": False,
        "ask_user": "What is the role or responsibility of each agent type?",
        "description": "Natural-language description of each agent’s purpose."
    },

    "communication": {
        "type": "string",
        "required": False,
        "ask_user": "How should agents communicate? (Direct messages, shared environment, broadcast, etc.)",
        "description": "Defines the agent communication model.",
        "example": "Agents communicate through direct messaging."
    },

    "topology": {
        "type": "string",
        "required": False,
        "ask_user": "How should the agents be connected? (Pipeline, hierarchical, peer-to-peer, centralized, etc.)",
        "description": "Defines logical connectivity or network structure."
    },

    "tools": {
        "type": "list",
        "required": False,
        "ask_user": "Do any agents need tools? (For example: search tools, calculators, API access, memory lookup.)",
        "description": "List of tools available in the system."
    },

    "memory": {
        "type": "string",
        "required": False,
        "ask_user": "Should the system use memory? (None, shared memory for all agents, or per-agent memory.)",
        "description": "Defines memory usage.",
        "example": "per-agent, shared memory"
    },

    "planning": {
        "type": "string",
        "required": False,
        "ask_user": "Should the system include planning? (None, lightweight planning, or a dedicated planning agent.)",
        "description": "Defines whether planning is needed.",
        "example": "A planning agent coordinates tasks."
    },

    "framework_constraints": {
        "type": "dict",
        "required": False,
        "ask_user": "Do you have any performance requirements (speed, scalability, low latency)?",
        "description": "Performance and architectural requirements.",
        "example": {"latency": "low", "scalability": "medium"}
    },

    "constraints": {
        "type": "dict",
        "required": False,
        "ask_user": "Do you have system constraints? (Cost limits, compute budget, token usage, etc.)",
        "description": "System constraints or resource limits.",
        "example": {"cost_budget": 50}
    },
}
