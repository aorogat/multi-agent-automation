import os
from backend.engine.requirements_agent.agent import RequirementsAgent
from backend.utils.logger import debug
import json



class MASAutomationEngine:
    def __init__(self):
        self.spec = {
            "task": None,
            "goal": None,
            "framework_constraints": {},
            "agents": {},
            "tools": [],
            "memory": {},
            "planning": None,
            "communication": None,
            "topology": None,
            "constraints": {},
        }

        api_key = os.getenv("OPENAI_API_KEY")
        self.req_agent = RequirementsAgent(api_key)

    def process(self, message, history):
        debug(f"MAS Engine processing message: {message}")
        debug(f"Spec before requirement update:\n{json.dumps(self.spec, indent=2)}")

        agent_output = self.req_agent.run(message, self.spec, history)

        debug(f"Agent output:\n{agent_output}")

        for k, v in agent_output.get("updated_fields", {}).items():
            self.spec[k] = v

        debug(f"Spec after applying updates:\n{json.dumps(self.spec, indent=2)}")

        reply = agent_output["reply"]
        graph = [{"data": {"id": "agent1", "label": "Agent 1"}}]

        return reply, graph, self.spec
