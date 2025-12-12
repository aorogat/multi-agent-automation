# backend/engine/visualization/ir_schema.py

"""
Graph Intermediate Representation (IR) Schema

The LLM must produce JSON that conforms to this schema.

Any topology (pipeline, hierarchy, hub-spoke, peer-to-peer, etc.)
must ultimately describe:

- nodes: list of {
      "id": string,
      "type": string,
      "count": integer       # may represent clusters of identical agents
  }

- edges: list of {
      "source": string,
      "target": string,
      "relation": string     # optional semantic label
  }

Optionally, the LLM may also output:

- topology: one of ["pipeline", "hierarchy", "star", "p2p", ...]
- parameters: {
        "branch_factor": int,
        "depth": int,
        ...
  }

This schema is intentionally minimal so contributors can add new fields.
"""

IR_SCHEMA = {
    "topology": {"type": "string", "required": True},
    "nodes": {
        "type": "list",
        "required": True,
        "structure": {
            "id": "string",
            "label": "string",
            "count": "integer"
        }
    },
    "params": {"type": "dict", "required": False}
}
