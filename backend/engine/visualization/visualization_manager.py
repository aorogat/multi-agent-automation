# backend/engine/visualization/visualization_manager.py

from typing import Dict, Any, List
from backend.engine.visualization.graph_llm_planner import GraphLLMPlanner
from backend.engine.visualization.graph_builder import GraphBuilder
from backend.utils.logger import debug


class VisualizationManager:
    """
    Full visualization pipeline:

    SPEC → (LLM Planner) → IR → (GraphBuilder) → nodes + edges

    Responsibilities:
    -----------------
    ✓ Validate that the spec contains enough information
    ✓ Ask the planner to create a topology-aware intermediate representation
    ✓ Convert IR into final Cytoscape-ready graph
    ✓ Handle errors gracefully
    """

    def __init__(self):
        self.planner = GraphLLMPlanner()
        self.builder = GraphBuilder()

    # ----------------------------------------------------------------------
    # PUBLIC ENTRY POINT
    # ----------------------------------------------------------------------
    def generate_graph(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes the MAS spec (dict) and returns a graph suitable for UI display.

        spec MUST contain:
            - agents: list of objects {type, count}
            - topology: string (e.g., 'star', 'pipeline', ...)
        """

        debug("VisualizationManager: received spec")
        debug(spec)

        # --------------------------------------------------------
        # VALIDATE MINIMUM SPEC CONTENT
        # --------------------------------------------------------
        agents = spec.get("agents", [])
        topology = spec.get("topology")

        if not agents:
            debug("VisualizationManager: missing agents, returning empty graph.")
            return []

        if not topology:
            debug("VisualizationManager: missing topology, returning agent-only nodes.")
            return self._simple_node_graph(agents)

        # --------------------------------------------------------
        # STEP 1: Produce intermediate representation
        # --------------------------------------------------------
        try:
            ir = self.planner.create_graph_ir(spec)
            debug(f"VisualizationManager: IR produced:\n{ir}")
        except Exception as e:
            debug(f"ERROR in GraphLLMPlanner: {e}")
            return self._simple_node_graph(agents)

        # --------------------------------------------------------
        # STEP 2: Build final graph from IR
        # --------------------------------------------------------
        try:
            graph = self.builder.build(ir)
            debug(f"VisualizationManager: Final graph built successfully {graph}")
            return graph
        except Exception as e:
            debug(f"ERROR in GraphBuilder: {e}")
            return self._simple_node_graph(agents)

    # ----------------------------------------------------------------------
    # FALLBACK GRAPH CREATION
    # ----------------------------------------------------------------------
    def _simple_node_graph(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        If topology or planner fails, produce a simple node-only visualization.

        agents = [
            {"type": "Student", "count": 100},
            {"type": "Teacher", "count": 10}
        ]

        This will return 110 nodes with no edges.
        """

        debug("VisualizationManager: generating fallback simple graph")

        nodes = []
        for group in agents:
            base_label = group["type"].title()
            base_id = base_label.lower()
            count = group.get("count", 1)

            for i in range(1, count + 1):
                nodes.append({
                    "data": {
                        "id": f"{base_id}_{i}",
                        "label": base_label
                    }
                })

        return nodes
