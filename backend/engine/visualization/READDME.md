# Visualization Module — README

## Overview

The **Visualization Module** transforms a Multi-Agent System (MAS) specification into an interactive graph visualization.  
It uses a two-stage pipeline:

1. **GraphLLMPlanner** — interprets the MAS specification and generates a structured **Intermediate Representation (IR)**.
2. **GraphBuilder** — converts the IR into a **Cytoscape-compatible graph** (nodes + edges).

This separation ensures clean architecture, prevents LLM hallucinations, and enables contributors to add new topologies without modifying core logic.

---

## Architecture

### Core Components

| Component | Responsibility |
|----------|----------------|
| **VisualizationManager** | Main orchestrator that ties planner + builder together |
| **GraphLLMPlanner** | Uses LLM to convert MAS spec → IR using dynamic topology definitions |
| **GraphBuilder** | Converts IR → Cytoscape nodes/edges using modular topology handlers |
| **Topology Plugins** | Folder of pluggable modules; each defines rules for building a graph layout |

---

## Data Flow Pipeline
```
MAS Specification
    ↓
GraphLLMPlanner (LLM-based)
    ↓ IR (Intermediate Representation)
GraphBuilder
    ↓
Cytoscape Graph (nodes + edges)
```

---

## How It Works

### Stage 1 — MAS Specification

Example spec (produced by RequirementsAgent):
```json
{
  "task": "Simulate a school",
  "goal": "Study how LLMs influence student learning behavior",
  "agents": [
    { "type": "Student", "count": 100 },
    { "type": "Teacher", "count": 10 },
    { "type": "Admin", "count": 3 }
  ],
  "communication": "direct",
  "topology": "hierarchy",
  "tools": [],
  "memory": "per-agent",
  "planning": "none"
}
```

### Stage 2 — Intermediate Representation (IR)

The GraphLLMPlanner transforms the MAS spec into a topology-agnostic IR.
The IR is not tied to a specific graph layout — only logical structure.

Example IR:
```json
{
  "topology": "hierarchy",
  "groups": [
    { "type": "Admin", "count": 3, "role": "root", "connect_to": ["Teacher"] },
    { "type": "Teacher", "count": 10, "role": "middle", "connect_to": ["Student"] },
    { "type": "Student", "count": 100, "role": "leaf", "connect_to": [] }
  ],
  "constraints": {
    "branching_factor": 4,
    "max_depth": 3
  }
}
```

#### Why IR Matters

- Keeps LLM output simple, structured, and predictable
- Prevents hallucinated node IDs or graph layouts
- Allows contributors to add new topologies without changing LLM prompts
- Clear separation of planning vs. rendering

### Stage 3 — Graph Output

The GraphBuilder converts IR into Cytoscape JSON:
```json
[
  { "data": { "id": "admin_1", "label": "Admin" } },
  { "data": { "id": "teacher_1", "label": "Teacher" } },
  { "data": { "id": "student_1", "label": "Student" } },

  { "data": { "source": "admin_1", "target": "teacher_1" } },
  { "data": { "source": "teacher_1", "target": "student_1" } }
]
```

The UI can render this directly.

---

## Usage Example
```python
from backend.engine.visualization.visualization_manager import VisualizationManager

spec = {
    "task": "Simulate a school",
    "goal": "Study LLM impact",
    "agents": [
        {"type": "Student", "count": 50},
        {"type": "Teacher", "count": 5}
    ],
    "topology": "star"
}

viz = VisualizationManager()
graph = viz.generate_graph(spec)

print(graph)  # Cytoscape-ready
```

---

## Extending the Visualization Module

The module was designed for easy community contributions.

### 1. Adding New Topologies (Plugin System)

All topologies live in:
```
backend/engine/visualization/topologies/
```

Each file is automatically discovered.

#### To add a new topology:

**Step 1 — Create a new file**

Example: `backend/engine/visualization/topologies/ring.py`

**Step 2 — Implement required interface:**
```python
def description():
    return "A circular chain where each agent connects to the next."

def build(ir):
    # return a list of Cytoscape nodes + edges
    ...
```

**Step 3 — Done!**

- The planner automatically includes your topology in its LLM prompt.
- The builder automatically uses it when IR contains `"topology": "ring"`.
- No core code modification required.

### 2. IR Format Extensions

Contributors can add new IR attributes:
```json
{
  "groups": [
    {
      "type": "Teacher",
      "count": 10,
      "attributes": {
        "llm_model": "gpt-4",
        "memory_size": "16MB"
      }
    }
  ]
}
```

GraphBuilder automatically merges these into node metadata.

### 3. IR Validation

To ensure clean graph generation:
```python
from backend.engine.visualization.ir_validator import IRValidator

IRValidator.validate(ir)
```

Validators ensure:

- Required fields exist
- Each group has "type" and "count"
- No invalid values (e.g., count < 1)

---

## Best Practices for Contributors

### DO:

- Keep IR clean and minimal
- Add new topology modules instead of editing core files
- Write unit tests for new topologies
- Document new attributes in the README

### DON'T:

- Hardcode node IDs
- Add topology logic to GraphLLMPlanner
- Modify IR format without updating GraphBuilder
- Return invalid or partial IR from planner

---

## Testing New Topologies

Example unit test:
```python
import unittest
from backend.engine.visualization.topologies.ring import build

class TestRingTopology(unittest.TestCase):
    def test_ring_edges(self):
        ir = {
            "topology": "ring",
            "groups": [{"type": "Agent", "count": 5}]
        }
        graph = build(ir)

        edges = [e for e in graph if "source" in e["data"]]
        self.assertEqual(len(edges), 5)  # ring has N edges
```

---

## Troubleshooting

| Issue | Possible Cause | Fix |
|-------|----------------|-----|
| No graph output | IR malformed | Enable IR validation |
| Missing edges | connect_to incorrect | Adjust IR or constraints |
| Slow rendering | Too many nodes | Add clustering or summarization |
| LLM hallucinating IR | Planner prompt too loose | Strengthen schema / examples |

---

## Contributing

1. Fork repository
2. Create feature branch
3. Add topology or IR extension
4. Write tests
5. Open Pull Request

---

## License

Your License Here

---

## Contact

For questions or contributions, contact: Your contact info here