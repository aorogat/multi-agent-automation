SCHEMA_VERSION = "3.0.0"

SPEC_SCHEMA = {
    "task": {
        "type": "string",
        "required": True,
        "ask_user": "What do you want your system to do? Tell me in simple words what problem you're trying to solve or what you want to accomplish.",
        "description": "A plain-language description of the system's purpose.",
        "conversation_priority": 1
    },

    "goal": {
        "type": "string",
        "required": True,
        "ask_user": "What's the main goal? What should happen when everything works correctly?",
        "description": "High-level purpose or expected outcome of the system.",
        "conversation_priority": 2
    },

    "agents": {
        "type": "list",
        "required": True,
        "ask_user": "What types of participants or workers do you need? For example: 'I need 10 customer service agents and 1 manager' or 'I want 100 students and 5 teachers'. You can tell me what each type should do.",
        "description": "List of agent definitions with comprehensive properties.",
        "conversation_priority": 3,
        "structure": {
            "type": "string",           # e.g., 'Student', 'Teacher', 'Coordinator'
            "count": "integer",          # number of agents of this type
            "role": "string",            # role/responsibility of this agent type
            "capabilities": "list",      # list of capabilities (e.g., ['reasoning', 'memory', 'tool_use'])
            "tools": "list",             # tools specific to this agent type (optional)
            "behavior": "string",        # behavioral characteristics (optional)
            "initial_state": "dict"      # initial state/config for this agent type (optional)
        },
        "replace_on_update": True,
        "example": [
            {
                "type": "Student",
                "count": 100,
                "role": "Learns from teacher and collaborates with peers",
                "capabilities": ["reasoning", "memory", "communication"],
                "tools": ["calculator", "note_taker"],
                "behavior": "Curious and collaborative"
            }
        ]
    },

    "communication": {
        "type": "string",
        "required": False,
        "ask_user": "How should your participants talk to each other? For example: 'They send messages directly to each other' or 'They all see a shared board' or 'One person broadcasts to everyone'. If you're not sure, I can suggest something based on your setup.",
        "description": "Defines the agent communication model.",
        "example": "Agents communicate through direct messaging with message queuing.",
        "conversation_priority": 5,
        "can_assume": True
    },

    "topology": {
        "type": "dict",
        "required": True,
        "ask_user": "How should your participants be organized? For example: 'Everyone can talk to everyone' (fully connected), 'One manager oversees everyone' (hierarchy), or 'They work in small groups' (clusters). If you're not sure, I can suggest something that makes sense for your setup.",
        "description": "Defines agent connectivity, network structure, and connection parameters.",
        "conversation_priority": 4,
        "can_assume": True,
        "structure": {
            "type": "string",            # e.g., 'hierarchy', 'mesh', 'star', 'ring', 'custom', 'fully_connected'
            "params": "dict",            # topology-specific parameters
            "connection_rules": "dict",  # rules for which agents can connect (optional)
            "dynamic": "boolean"         # whether topology can change during execution (optional)
        },
        "example": {
            "type": "hierarchy",
            "params": {
                "levels": 3,
                "fanout": 5
            },
            "connection_rules": {
                "same_level": False,
                "cross_level": True
            },
            "dynamic": False
        }
    },

    "environment": {
        "type": "dict",
        "required": False,
        "ask_user": "Do your participants need a shared space to work in? Like a shared whiteboard, a game board, a virtual room, or a simulation world? If not, we can skip this.",
        "description": "Defines the shared environment where agents interact.",
        "conversation_priority": 7,
        "can_assume": True,
        "structure": {
            "type": "string",            # e.g., 'shared_workspace', 'simulation', 'grid_world', 'virtual_space'
            "properties": "dict",        # environment properties (size, dimensions, rules, etc.)
            "observable": "boolean",     # whether agents can observe the environment
            "mutable": "boolean"         # whether agents can modify the environment
        },
        "example": {
            "type": "shared_workspace",
            "properties": {
                "size": "unlimited",
                "persistence": True
            },
            "observable": True,
            "mutable": True
        }
    },

    "tools": {
        "type": "list",
        "required": False,
        "ask_user": "Do your participants need any special tools or abilities? For example: calculators, web search, file access, databases, or custom tools. You can say 'all participants can use web search' or 'only the manager can access the database'. If they don't need special tools, we can skip this.",
        "description": "List of tools available in the system. Can be global or assigned to specific agents.",
        "conversation_priority": 6,
        "can_assume": True,
        "structure": {
            "name": "string",            # tool name/identifier
            "type": "string",            # tool type (e.g., 'api', 'function', 'external_service')
            "description": "string",     # what the tool does
            "scope": "string",           # 'global' (all agents) or agent type name (specific agents)
            "config": "dict"             # tool-specific configuration (optional)
        },
        "replace_on_update": False,
        "example": [
            {
                "name": "web_search",
                "type": "api",
                "description": "Search the web for information",
                "scope": "global",
                "config": {"max_results": 10}
            },
            {
                "name": "calculator",
                "type": "function",
                "description": "Perform mathematical calculations",
                "scope": "Student",
                "config": {}
            }
        ]
    },

    "memory": {
        "type": "dict",
        "required": False,
        "ask_user": "Should your participants remember things? For example: 'Each person remembers their own conversations' (per-person memory), 'Everyone shares the same memory' (shared memory), or 'No memory needed' (none). If you're not sure, I can suggest something reasonable.",
        "description": "Defines memory usage and configuration.",
        "conversation_priority": 8,
        "can_assume": True,
        "structure": {
            "type": "string",            # 'none', 'per_agent', 'shared', 'hybrid'
            "persistence": "boolean",    # whether memory persists across sessions
            "capacity": "string",        # memory capacity (e.g., 'unlimited', '1000_entries')
            "retrieval_strategy": "string"  # how memories are retrieved (optional)
        },
        "example": {
            "type": "per_agent",
            "persistence": True,
            "capacity": "unlimited",
            "retrieval_strategy": "semantic_search"
        }
    },

    "planning": {
        "type": "dict",
        "required": False,
        "ask_user": "Should your system plan ahead? For example: 'One coordinator makes plans for everyone' or 'Each participant plans their own actions' or 'No planning needed, they just react'. If you're not sure, I can suggest something.",
        "description": "Defines planning capabilities and configuration.",
        "conversation_priority": 9,
        "can_assume": True,
        "structure": {
            "enabled": "boolean",        # whether planning is enabled
            "type": "string",            # 'none', 'lightweight', 'dedicated_agent', 'distributed'
            "agent_type": "string",     # if dedicated_agent, which agent type handles planning (optional)
            "horizon": "integer",        # planning horizon (optional)
            "replanning": "boolean"     # whether replanning is allowed (optional)
        },
        "example": {
            "enabled": True,
            "type": "dedicated_agent",
            "agent_type": "Coordinator",
            "horizon": 5,
            "replanning": True
        }
    },

    "framework_constraints": {
        "type": "dict",
        "required": False,
        "ask_user": "Do you have any performance needs? For example: 'It needs to be very fast' or 'It should handle thousands of participants' or 'It should use minimal resources'. If you don't have specific requirements, we can skip this.",
        "description": "Performance and architectural requirements.",
        "conversation_priority": 10,
        "can_assume": True,
        "example": {
            "latency": "low",
            "scalability": "medium",
            "throughput": "high",
            "resource_usage": "minimal"
        }
    },

    "constraints": {
        "type": "dict",
        "required": False,
        "ask_user": "Do you have any limits or budgets? For example: cost limits, time limits, or usage limits. If you don't have specific constraints, we can skip this.",
        "description": "System constraints or resource limits.",
        "conversation_priority": 11,
        "can_assume": True,
        "example": {
            "cost_budget": 50,
            "max_tokens": 1000000,
            "max_agents": 1000,
            "time_limit": "1_hour"
        }
    },

    # =====================================================================
    # EXECUTION & CONTROL SEMANTICS
    # =====================================================================
    "execution": {
        "type": "dict",
        "required": False,
        "ask_user": "How should your system run? Should all participants act at the same time (synchronous), or can they act independently (asynchronous)? Should it be event-driven (reacting to events) or tick-based (moving in time steps)? If you're not sure, I can suggest something reasonable.",
        "description": "Execution model and control semantics that affect latency, throughput, and coordination behavior.",
        "conversation_priority": 12,
        "can_assume": True,
        "structure": {
            "model": "string",           # 'synchronous', 'asynchronous', 'event_driven', 'tick_based'
            "step_granularity": "string", # 'agent_turn', 'message', 'environment_tick'
            "blocking": "boolean"        # whether execution blocks on agent actions
        },
        "example": {
            "model": "asynchronous",
            "step_granularity": "message",
            "blocking": False
        }
    },

    "failure_handling": {
        "type": "dict",
        "required": False,
        "ask_user": "What should happen when something goes wrong? Should the system retry failed actions, use a backup participant, or gracefully degrade? If you're not sure, I can suggest reasonable defaults.",
        "description": "Failure and recovery policy for handling tool failures, planner failures, and system errors.",
        "conversation_priority": 13,
        "can_assume": True,
        "structure": {
            "retry_policy": "string",      # 'none', 'fixed', 'adaptive'
            "fallback_agent": "string",    # agent type or null
            "timeout": "string",           # timeout duration
            "graceful_degradation": "boolean" # whether to degrade gracefully on failure
        },
        "example": {
            "retry_policy": "adaptive",
            "fallback_agent": None,
            "timeout": "30s",
            "graceful_degradation": True
        }
    },

    # =====================================================================
    # MEMORY SEMANTICS (Beyond Storage)
    # =====================================================================
    "memory_editing": {
        "type": "dict",
        "required": False,
        "ask_user": "Should your participants be able to update or delete their memories? How should conflicts be resolved if multiple participants try to change the same memory? If you're not sure, I can suggest something reasonable.",
        "description": "Memory mutability and editing semantics - how memories can be updated, deleted, and how conflicts are resolved.",
        "conversation_priority": 14,
        "can_assume": True,
        "structure": {
            "supports_update": "boolean",
            "supports_delete": "boolean",
            "conflict_resolution": "string" # 'overwrite', 'versioned', 'timestamp', 'none'
        },
        "example": {
            "supports_update": True,
            "supports_delete": True,
            "conflict_resolution": "timestamp"
        }
    },

    "memory_scope_policy": {
        "type": "string",
        "required": False,
        "ask_user": "If participants have their own memories and also share a common memory, which one takes priority when there's a conflict? Should individual memories override shared ones, or the other way around, or should they be merged? If you're not sure, I can suggest something.",
        "description": "Policy for resolving conflicts between agent-specific memory and shared memory.",
        "conversation_priority": 15,
        "can_assume": True,
        "example": "agent_overrides_shared"
    },

    # =====================================================================
    # PLANNING SEMANTICS (Not Just On/Off)
    # =====================================================================
    "planning_representation": {
        "type": "string",
        "required": False,
        "ask_user": "How should plans be represented? As free text, structured schemas, graph plans, or something else? If you're not sure, I can suggest something based on your planning setup.",
        "description": "Format and representation of plans - affects planning success rates and system robustness.",
        "conversation_priority": 16,
        "can_assume": True,
        "example": "free_text"
    },

    "planning_authority": {
        "type": "string",
        "required": False,
        "ask_user": "Who can change or override plans? Only the planner, or can participants override plans themselves, or should it require consensus? If you're not sure, I can suggest something reasonable.",
        "description": "Authority model for plan modification - who can override plans and under what conditions.",
        "conversation_priority": 17,
        "can_assume": True,
        "example": "planner_only"
    },

    # =====================================================================
    # COORDINATION & COLLABORATION
    # =====================================================================
    "coordination_goal": {
        "type": "string",
        "required": False,
        "ask_user": "What's the main goal of coordination? Should participants reach consensus, complete tasks, share information, or let something emerge naturally? If you're not sure, I can suggest something based on your system.",
        "description": "Primary objective for agent coordination - affects topology effectiveness and collaboration patterns.",
        "conversation_priority": 18,
        "can_assume": True,
        "example": "task_completion"
    },

    "agent_awareness": {
        "type": "string",
        "required": False,
        "ask_user": "How much should participants know about each other? Nothing, just roles, summary of states, or full visibility into each other's states? If you're not sure, I can suggest something reasonable.",
        "description": "Level of mutual awareness between agents - affects collaboration effectiveness.",
        "conversation_priority": 19,
        "can_assume": True,
        "example": "roles_only"
    },

    # =====================================================================
    # ENVIRONMENT DYNAMICS (Beyond Existence)
    # =====================================================================
    "environment_dynamics": {
        "type": "dict",
        "required": False,
        "ask_user": "How should the shared environment change over time? Should changes be predictable, random, or learned? Should time move in steps or continuously? If you're not sure, I can suggest something.",
        "description": "Dynamics of environment state transitions - how the environment evolves over time.",
        "conversation_priority": 20,
        "can_assume": True,
        "structure": {
            "state_transition": "string",  # 'deterministic', 'stochastic', 'learned'
            "time_model": "string",        # 'discrete', 'continuous'
            "central_controller": "boolean" # whether environment has central controller
        },
        "example": {
            "state_transition": "deterministic",
            "time_model": "discrete",
            "central_controller": False
        }
    },

    # =====================================================================
    # OBSERVABILITY, LOGGING & EVALUATION
    # =====================================================================
    "observability": {
        "type": "dict",
        "required": False,
        "ask_user": "How much should the system track and log? No logging, just events, or full detailed traces? Should it be replayable for debugging? If you're not sure, I can suggest reasonable defaults.",
        "description": "Instrumentation and observability settings for debugging, reproducibility, and evaluation.",
        "conversation_priority": 21,
        "can_assume": True,
        "structure": {
            "logging_level": "string",   # 'none', 'events', 'full'
            "trace_agents": "boolean",   # whether to trace individual agent actions
            "replayable": "boolean"      # whether logs are replayable for debugging
        },
        "example": {
            "logging_level": "events",
            "trace_agents": True,
            "replayable": True
        }
    },

    # =====================================================================
    # COST & BACKEND STRATEGY
    # =====================================================================
    "backend_routing": {
        "type": "dict",
        "required": False,
        "ask_user": "How should the system route requests to backend services? Use a single service, tiered services based on complexity, or budget-aware routing? Should there be a fallback? If you're not sure, I can suggest something reasonable.",
        "description": "Backend routing strategy for cost-aware execution and scalability.",
        "conversation_priority": 22,
        "can_assume": True,
        "structure": {
            "strategy": "string",         # 'single_llm', 'tiered', 'budget_aware'
            "fallback_backend": "string", # fallback backend identifier
            "cost_tracking": "boolean"   # whether to track costs
        },
        "example": {
            "strategy": "budget_aware",
            "fallback_backend": "gpt-3.5-turbo",
            "cost_tracking": True
        }
    },
}
