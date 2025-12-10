import json
from backend.engine.requirements_agent.agent import RequirementsAgent
from backend.engine.requirements_agent.spec_model import SpecificationModel
from backend.utils.logger import debug


class MASAutomationEngine:
    """
    Core engine that:
    - Holds the MAS specification (SpecificationModel)
    - Sends user messages + spec to RequirementsAgent
    - Applies updates to the spec
    - Returns reply + graph + updated spec to API/UI
    """

    def __init__(self):
        # Specification is now schema-driven and dynamic
        self.spec = SpecificationModel()

        # RequirementsAgent no longer needs API key; uses centralized LLM manager
        self.req_agent = RequirementsAgent()

    def process(self, message, history):
        debug(f"MAS Engine processing message: {message}")
        debug(f"Spec before requirement update:\n{json.dumps(self.spec.to_dict(), indent=2)}")

        # Run RequirementsAgent
        agent_output = self.req_agent.run(
            user_message=message,
            current_spec=self.spec,
            history=history,
        )

        debug(f"Agent output:\n{json.dumps(agent_output, indent=2)}")

        # Update spec with deltas proposed by RequirementsAgent
        self.spec.update(agent_output.get("updated_fields", {}))

        debug(f"Spec after applying updates:\n{json.dumps(self.spec.to_dict(), indent=2)}")

        # Agent message to user
        reply = agent_output["reply"]

        # Placeholder graph (will later depend on agents/topology)
        graph = [
            {"data": {"id": "system", "label": "MAS System"}}
        ]

        # Send spec dict to UI
        return reply, graph, self.spec.to_dict()
