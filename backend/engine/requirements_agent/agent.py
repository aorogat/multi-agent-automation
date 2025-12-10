import json
from pathlib import Path
from openai import OpenAI
from backend.utils.logger import debug


class RequirementsAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        prompt_path = Path(__file__).parent / "prompts" / "requirements_prompt.txt"
        self.base_prompt = prompt_path.read_text()

    def run(self, message: str, spec: dict, history: list):
        debug(f"RequirementsAgent.run() called with message: {message}")
        debug(f"Current spec: {json.dumps(spec, indent=2)}")
        debug(f"Conversation history: {json.dumps(history[-6:], indent=2)}")

        full_input = (
            self.base_prompt +
            "\n\nCurrent MAS spec:\n" +
            json.dumps(spec, indent=2) +
            "\n\nConversation history:\n" +
            json.dumps(history[-6:], indent=2) +
            f"\n\nUser message:\n{message}\n\n"
            "REMINDER: Return ONE valid JSON object only."
        )

        debug(f"Full prompt sent to LLM:\n{full_input}")

        # --- Call GPT ---
        response = self.client.responses.create(
            model="gpt-4o-mini",
            input=full_input,
            max_output_tokens=300,
        )

        raw_text = response.output_text
        debug(f"Raw LLM Output:\n{raw_text}")

        # --- Extract JSON object from output ---
        import re
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)

        if not match:
            debug("No JSON detected in output!")
            return {
                "reply": "I could not understand. Please restate your answer.",
                "updated_fields": {},
                "needs_more": True
            }

        json_text = match.group(0)

        # --- Parse JSON safely ---
        try:
            data = json.loads(json_text)
            debug(f"Parsed JSON:\n{data}")
        except Exception as e:
            debug(f"JSON parse error: {e}")
            debug(f"JSON text:\n{json_text}")
            return {
                "reply": "I could not parse that. Please rephrase.",
                "updated_fields": {},
                "needs_more": True
            }

        return data
