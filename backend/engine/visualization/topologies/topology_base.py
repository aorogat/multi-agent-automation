from abc import ABC, abstractmethod
from typing import Dict, Any, List


class TopologyDefinition(ABC):
    """
    Base class for all graph topologies.

    A topology definition serves THREE roles:
    1) Documentation for the LLM (planning stage)
    2) Contract for IR structure (validation stage)
    3) Execution logic (graph building stage)

    Every topology MUST subclass this class.
    """

    # ------------------------------------------------------------------
    # REQUIRED METADATA (LLM + REGISTRY)
    # ------------------------------------------------------------------

    #: Unique topology identifier (used in IR)
    name: str = None

    #: Human-readable description of the topology
    description: str = ""

    #: Explicit rules for constructing the IR
    #: (used verbatim in LLM prompt)
    ir_hints: str = ""

    #: Schema for topology-specific parameters
    #: Example:
    #: { "branch_factor": {"type": "int", "default": 2} }
    params_schema: Dict[str, Dict[str, Any]] = {}

    #: Example IR snippet for this topology
    #: Used to anchor LLM output
    ir_example: Dict[str, Any] = {}




    default_params = {}

    # ------------------------------------------------------------------
    # REQUIRED EXECUTION LOGIC
    # ------------------------------------------------------------------

    @classmethod
    def merge_params(cls, params: dict) -> dict:
        """
        Merge user/LLM params with topology defaults.
        User values always override defaults.
        """
        merged = dict(cls.default_params)
        merged.update(params or {})
        return merged

    @classmethod
    @abstractmethod
    def build_edges(
        cls,
        nodes: List[Dict[str, Any]],
        params: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Convert expanded node instances into edges.

        Input nodes format:
        [
            {"data": {"id": "student_1", "label": "Student"}},
            ...
        ]

        Output edges format:
        [
            {"data": {"source": "a", "target": "b"}},
            ...
        ]
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # OPTIONAL VALIDATION
    # ------------------------------------------------------------------

    @classmethod
    def validate_ir(cls, ir: Dict[str, Any]) -> None:
        """
        Optional topology-specific IR validation.
        Called AFTER global IR validation.

        Override if needed.
        """
        return

    # ------------------------------------------------------------------
    # PARAMETER HANDLING
    # ------------------------------------------------------------------

    @classmethod
    def normalize_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fill defaults, cast types, and drop unknown parameters.
        """
        normalized = {}

        for pname, meta in cls.params_schema.items():
            if pname in params:
                normalized[pname] = cls._cast(params[pname], meta.get("type"))
            else:
                normalized[pname] = meta.get("default")

        return normalized

    @staticmethod
    def _cast(value: Any, target_type: str):
        if target_type == "int":
            return int(value)
        if target_type == "float":
            return float(value)
        if target_type == "bool":
            return bool(value)
        if target_type == "str":
            return str(value)
        return value

    # ------------------------------------------------------------------
    # SAFETY CHECKS (RUN AT LOAD TIME)
    # ------------------------------------------------------------------

    @classmethod
    def sanity_check(cls):
        """
        Ensures the topology class is well-defined.
        Called automatically by the loader.
        """
        assert cls.name, "TopologyDefinition must define 'name'"
        assert isinstance(cls.name, str)

        assert cls.description, f"{cls.name}: missing description"
        assert isinstance(cls.description, str)

        assert isinstance(cls.ir_hints, str)

        assert isinstance(cls.params_schema, dict)

        assert isinstance(cls.ir_example, dict)
        assert "topology" in cls.ir_example
        assert cls.ir_example["topology"] == cls.name
        assert "nodes" in cls.ir_example

