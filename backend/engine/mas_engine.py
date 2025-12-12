import json
from backend.engine.requirements_agent.agent import RequirementsAgent
from backend.engine.requirements_agent.spec_model import SpecificationModel
from backend.engine.visualization.visualization_manager import VisualizationManager
from backend.utils.logger import debug
import requests



class MASAutomationEngine:
    """
    Core engine that:
    - Maintains MAS specification (SpecificationModel)
    - Interacts with RequirementsAgent for schema-aligned updates
    - Uses VisualizationManager to generate a graph from the spec
    - Returns: assistant reply + graph JSON + spec JSON
    """

    def __init__(self):
        # Dynamic, schema-driven MAS specification
        self.spec = SpecificationModel()

        # Requirement collection via LLM
        self.req_agent = RequirementsAgent()

        # Visualization subsystem (LLM → IR → GraphBuilder)
        self.visualizer = VisualizationManager()

    # ------------------------------------------------------------------
    # PROCESS USER MESSAGE
    # ------------------------------------------------------------------
    def process(self, message, history):
        debug(f"\n===== MAS Engine processing message: {message} =====")

        before = self.spec.to_dict()
        debug(f"Spec BEFORE update:\n{json.dumps(before, indent=2)}")

        # ------------------------------------------------------------
        # 1. REQUIREMENTS AGENT — Schema-aware spec update
        # ------------------------------------------------------------
        agent_output = self.req_agent.run(
            user_message=message,
            current_spec=self.spec,
            history=history,
        )

        debug(f"RequirementsAgent OUTPUT:\n{json.dumps(agent_output, indent=2)}")

        updates = agent_output.get("updated_fields", {})
        if updates:
            self.spec.update(updates)

        after = self.spec.to_dict()
        debug(f"Spec AFTER update:\n{json.dumps(after, indent=2)}")

        # ------------------------------------------------------------
        # 2. VISUALIZATION PIPELINE — Convert spec → IR → graph
        # ------------------------------------------------------------
        try:
            graph = self.visualizer.generate_graph(after)

            # Guarantee structure is list-of-dicts for Cytoscape
            if not isinstance(graph, list):
                debug("Graph was not a list. Wrapping inside placeholder.")
                graph = [{"data": {"id": "invalid_graph", "label": "Invalid Graph"}}]



        except Exception as e:
            debug(f"Graph generation FAILED: {e}")

            # Provide a safe fallback graph so UI never breaks
            graph = [
                {"data": {"id": "system", "label": "MAS System"}},
                {"data": {"id": "error", "label": "Graph Error"}},
            ]
        
        debug(f"Try to update the graph {graph}")
        requests.post(
            "http://localhost:8050/update-graph",
            json={"elements": graph}
        )

        # ------------------------------------------------------------
        # 3. COLLECT REPLY FOR USER
        # ------------------------------------------------------------
        reply = agent_output.get("reply", "Okay.")

        return reply, graph, after
