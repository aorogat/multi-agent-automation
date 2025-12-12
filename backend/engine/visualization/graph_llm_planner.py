# backend/engine/visualization/graph_llm_planner.py

import os
import json
from typing import Dict, Any, List

from backend.llm.llm_manager import LLM
from backend.engine.visualization.ir_schema import IR_SCHEMA
from backend.utils.logger import debug


TOPOLOGY_DIR = os.path.join(
    os.path.dirname(__file__), 
    "topologies"
)


class GraphLLMPlanner:
    """
    Converts MAS spec → Intermediate Representation (IR) using an LLM.
    IR looks like:

    {
        "topology": "star",
        "nodes": [
            {"id": "students", "label": "Students", "count": 200},
            {"id": "teachers", "label": "Teachers", "count": 10}
        ],
        "params": {"branch_factor": 3}
    }
    """

    def __init__(self):
        self.topology_docs = self._load_topology_docs()

    # ----------------------------------------------------------------------
    # Load topology descriptions
    # ----------------------------------------------------------------------
    def _load_topology_docs(self) -> Dict[str, str]:
        docs = {}

        if not os.path.isdir(TOPOLOGY_DIR):
            debug("GraphLLMPlanner: Topology directory not found.")
            return docs

        for fname in os.listdir(TOPOLOGY_DIR):
            if fname.endswith(".txt"):
                path = os.path.join(TOPOLOGY_DIR, fname)
                topo_name = fname.replace(".txt", "")

                with open(path, "r") as f:
                    docs[topo_name] = f.read().strip()

        debug(f"Loaded topology definitions: {list(docs.keys())}")
        return docs

    # ----------------------------------------------------------------------
    # IR Schema → text for prompt
    # ----------------------------------------------------------------------
    def _ir_schema_text(self) -> str:

        out = ["INTERMEDIATE REPRESENTATION SCHEMA (STRICT JSON)\n"]

        for name, meta in IR_SCHEMA.items():
            required = "required" if meta.get("required") else "optional"
            ftype = meta["type"]

            out.append(f"- {name} ({required}, type={ftype})")

            if "structure" in meta:
                struct = meta["structure"]
                example_obj = {k: "<value>" for k in struct}
                out.append("  Structure example:")
                out.append("  " + json.dumps([example_obj], indent=2))

        return "\n".join(out)

    # ----------------------------------------------------------------------
    # Create LLM prompt
    # ----------------------------------------------------------------------
    def _build_prompt(self, spec: Dict[str, Any]) -> str:

        topology_list = ", ".join(self.topology_docs.keys()) or "(none)"

        topology_definitions = "\n\n".join(
            f"TOPOLOGY: {name}\n{doc}" for name, doc in self.topology_docs.items()
        )

        # ❗ Hard enforce node structure
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

    Your task: Convert the MAS specification into a strict INTERMEDIATE REPRESENTATION (IR)
    that follows IR_SCHEMA EXACTLY.

    ❗ CRITICAL RULES:
    - "nodes" MUST be a list of OBJECTS with EXACT KEYS:
        id, label, count
    - DO NOT output keys like "type", "agent_type", or anything else.
    - `id` must be lowercase with underscores.
    - `label` must be human readable (title-case).
    - `count` must be an integer.
    - Any deviation will break the system.

    ============================== IR SCHEMA =============================
    {self._ir_schema_text()}
    =====================================================================

    VALID NODE FORMAT (you MUST FOLLOW THIS EXACTLY):
    {node_structure}

    =====================================================================
    SUPPORTED TOPOLOGIES:
    {topology_list}

    TOPOLOGY DEFINITIONS:
    {topology_definitions}

    =====================================================================
    CURRENT MAS SPECIFICATION:
    {json.dumps(spec, indent=2)}
    =====================================================================

    Now output ONLY a valid JSON IR object with:
    - topology
    - nodes
    - params (optional)

    Output ONLY JSON. DO NOT explain anything.
    """.strip()

    # ----------------------------------------------------------------------
    # Public: Generate IR
    # ----------------------------------------------------------------------
    def generate_ir(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(spec)
        debug("GraphLLMPlanner prompt:\n" + prompt)

        response = LLM.generate_json(prompt)
        debug(f"Graph LLM raw output: {response}")

        for node in response["nodes"]:
            if set(node.keys()) != {"id", "label", "count"}:
                raise ValueError(f"Invalid node structure: {node}")


        if not isinstance(response, dict):
            raise ValueError("LLM produced non-dict IR.")

        if "topology" not in response:
            raise ValueError("IR missing required field: topology")

        if "nodes" not in response:
            raise ValueError("IR missing required field: nodes")

        return response

    # ----------------------------------------------------------------------
    # Backwards compatibility wrapper
    # VisualizationManager calls this
    # ----------------------------------------------------------------------
    def create_graph_ir(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        For compatibility with VisualizationManager.
        """
        return self.generate_ir(spec)



