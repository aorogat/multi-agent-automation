# backend/llm/llm_manager.py

import os
from dotenv import load_dotenv
from openai import OpenAI
import re
import json

# ---------------------------------------------------------
# LOAD ENVIRONMENT AND GLOBAL LLM CONFIG
# ---------------------------------------------------------
load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing in .env")

# Create a global client instance
_global_client = OpenAI(api_key=API_KEY)


class LLM:
    """
    Centralized interface for all LLM calls in the system.
    Any other class should import and call this file only.
    """

    # MODEL SETTINGS (modifiable anytime)
    model = DEFAULT_MODEL
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "256"))
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    @staticmethod
    def configure(model=None, temperature=None, max_tokens=None):
        """Reconfigure LLM at runtime."""
        if model:
            LLM.model = model
        if temperature is not None:
            LLM.temperature = temperature
        if max_tokens is not None:
            LLM.max_tokens = max_tokens

    # ---------------------------------------------------------
    # BASIC GENERATION
    # ---------------------------------------------------------
    @staticmethod
    def generate(prompt: str) -> str:
        """
        Simple prompt → text completion using OpenAI Responses API.
        """
        response = _global_client.responses.create(
            model=LLM.model,
            input=prompt,
            max_output_tokens=LLM.max_tokens,
            temperature=LLM.temperature,
        )
        return response.output_text.strip()

    # ---------------------------------------------------------
    # JSON OUTPUT UTILITY
    # ---------------------------------------------------------
    @staticmethod
    def generate_json(prompt: str) -> dict:
        """
        Prompts the model and tries to parse the output as JSON.
        Automatically strips markdown fences like ```json and ```.

        Returns:
            dict: Parsed JSON object
                  or {"raw_output": "..."} on failure
        """
        raw = LLM.generate(prompt).strip()

        # ---------------------------------------------------------
        # Remove Markdown fences: ```json ... ``` or ``` ... ```
        # ---------------------------------------------------------
        # Remove opening ```json or ```
        if raw.startswith("```"):
            raw = raw.lstrip("`")
            raw = raw.replace("json", "", 1).strip()

        # Remove trailing ```
        if raw.endswith("```"):
            raw = raw[:-3].strip()

        # Also handle multi-line fenced blocks
        import re
        fenced = re.findall(r"```(?:json)?(.*?)```", raw, re.DOTALL)
        if fenced:
            raw = fenced[0].strip()

        # ---------------------------------------------------------
        # Attempt JSON parsing
        # ---------------------------------------------------------
        try:
            return json.loads(raw)
        except Exception:
            # Return raw output for debugging
            return {"raw_output": raw}


    # ---------------------------------------------------------
    # CHAT-STYLE INTERFACE (future ready)
    # ---------------------------------------------------------
    @staticmethod
    def chat(messages: list) -> str:
        """
        Accepts chat-like messages: [{"role": "user", "content": "..."}, ...]
        """
        prompt = "\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in messages
        ) + "\nASSISTANT:"

        return LLM.generate(prompt)
