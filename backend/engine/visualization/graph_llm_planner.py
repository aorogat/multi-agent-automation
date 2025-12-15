import os
import json
from typing import Dict, Any

from backend.llm.llm_manager import LLM
from backend.engine.visualization.ir_schema import IR_SCHEMA
from backend.engine.visualization.topologies.loader import TopologyLoader
from backend.utils.logger import debug


TOPOLOGY_DIR = os.path.join(
    os.path.dirname(__file__),
    "topologies"
)


class GraphLLMPlanner:
    """
    Converts MAS specification → Intermediate Representation (IR)
    using topology-aware, executable definitions.
    """

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------
    def __init__(self):
        print(f"Trying to load {TOPOLOGY_DIR}=========================================================================")
        loader = TopologyLoader(TOPOLOGY_DIR)
        self.topology_classes = loader.topologies
        self.topology_docs = self._build_topology_docs()

    # ------------------------------------------------------------------
    # Build topology documentation for the LLM
    # ------------------------------------------------------------------
    def _build_topology_docs(self) -> Dict[str, str]:
        docs = {}

        for name, topo_cls in self.topology_classes.items():
            docs[name] = f"""
                DESCRIPTION:
                {topo_cls.description}

                IR CONSTRUCTION HINTS:
                {topo_cls.ir_hints}

                PARAMETERS SCHEMA:
                {json.dumps(topo_cls.params_schema, indent=2)}

                EXAMPLE IR:
                {json.dumps(topo_cls.ir_example, indent=2)}
                """.strip()

        debug(f"GraphLLMPlanner: loaded topology definitions {list(docs.keys())}")
        return docs

    # ------------------------------------------------------------------
    # IR schema → text
    # ------------------------------------------------------------------
    def _ir_schema_text(self) -> str:
        lines = ["INTERMEDIATE REPRESENTATION SCHEMA (STRICT JSON)\n"]

        for name, meta in IR_SCHEMA.items():
            required = "required" if meta.get("required") else "optional"
            ftype = meta["type"]

            lines.append(f"- {name} ({required}, type={ftype})")

            if "structure" in meta:
                struct = meta["structure"]
                example = {k: "<value>" for k in struct}
                lines.append("  Structure example:")
                lines.append(json.dumps([example], indent=2))

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Build prompt
    # ------------------------------------------------------------------
    def _build_prompt(self, spec: Dict[str, Any]) -> str:
        topology_list = ", ".join(self.topology_docs.keys())

        topology_definitions = "\n\n".join(
            f"TOPOLOGY: {name}\n{doc}"
            for name, doc in self.topology_docs.items()
        )

        node_structure = json.dumps(
            [
                {
                    "id": "string_lowercase_identifier",
                    "label": "Human Readable Name",
                    "count": 0
                }
            ],
            indent=2
        )

        return f"""
You are the Graph Planning Agent.

Your task is to convert a Multi-Agent System (MAS) specification
into a strict INTERMEDIATE REPRESENTATION (IR).

❗ CRITICAL RULES:
- Output MUST be valid JSON
- "nodes" MUST be a list of objects with EXACT keys: id, label, count
- id → lowercase_with_underscores
- label → Human readable (Title Case)
- count → integer
- DO NOT invent fields
- DO NOT explain anything

============================== IR SCHEMA ==============================
{self._ir_schema_text()}
======================================================================

VALID NODE FORMAT (STRICT):
{node_structure}

========================== SUPPORTED TOPOLOGIES =======================
{topology_list}

========================= TOPOLOGY DEFINITIONS ========================
{topology_definitions}

====================== CURRENT MAS SPECIFICATION ======================
{json.dumps(spec, indent=2)}
======================================================================

Output ONLY the IR JSON object with:
- topology
- nodes
- params (optional), Add values to the current topology parameter schema from the spec values, if it can help.
""".strip()

    # ------------------------------------------------------------------
    # Generate IR
    # ------------------------------------------------------------------
    def generate_ir(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(spec)
        debug("GraphLLMPlanner prompt:\n" + prompt)

        response = LLM.generate_json(prompt)
        debug(f"GraphLLMPlanner raw output: {response}")

        # ------------------ Validation ------------------
        if not isinstance(response, dict):
            raise ValueError("IR must be a JSON object")

        if "topology" not in response:
            raise ValueError("IR missing required field: topology")

        if response["topology"] not in self.topology_classes:
            raise ValueError(f"Unsupported topology: {response['topology']}")

        if "nodes" not in response or not isinstance(response["nodes"], list):
            raise ValueError("IR missing or invalid 'nodes' field")

        for node in response["nodes"]:
            if set(node.keys()) != {"id", "label", "count"}:
                raise ValueError(f"Invalid node structure: {node}")

        return response

    # ------------------------------------------------------------------
    # Backwards compatibility
    # ------------------------------------------------------------------
    def create_graph_ir(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        return self.generate_ir(spec)
