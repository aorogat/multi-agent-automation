import os
import importlib
import inspect

from backend.engine.visualization.topologies.topology_base import TopologyDefinition
from backend.utils.logger import debug


class TopologyLoader:
    """
    Dynamically loads all topology definitions from this folder.

    Rules:
    - Only Python files
    - Ignore files starting with 'topology_' (base, utils, etc.)
    - Ignore __init__.py
    - Each file must define at least one subclass of TopologyDefinition

    NOTE:
    - This loader eagerly loads topologies on init
    - Exposes `topologies` attribute for backward compatibility
    """

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(__file__)
        self.topologies = {}

        self._load_topologies()

    # ------------------------------------------------------------------
    # PUBLIC API (EXPECTED BY GraphLLMPlanner)
    # ------------------------------------------------------------------
    def load(self):
        """
        Backward-compatible API.
        GraphLLMPlanner may call loader.load() OR access loader.topologies.
        """
        return self.topologies

    def get(self, name: str):
        """Return a topology class by name."""
        return self.topologies.get(name)

    def list_topologies(self):
        """Return list of registered topology names."""
        return list(self.topologies.keys())

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------
    def _load_topologies(self):
        debug("TopologyLoader: scanning topology folder")

        for fname in os.listdir(self.base_path):

            # -------------------------------
            # Apply filtering rules
            # -------------------------------
            if not fname.endswith(".py"):
                continue
            if fname.startswith("topology_"):
                continue
            if fname == "__init__.py":
                continue

            module_name = fname[:-3]  # strip .py
            module_path = (
                f"backend.engine.visualization.topologies.{module_name}"
            )

            debug(f"TopologyLoader: importing {module_path}")

            module = importlib.import_module(module_path)

            # -------------------------------
            # Register topology subclasses
            # -------------------------------
            for _, obj in inspect.getmembers(module, inspect.isclass):

                if (
                    issubclass(obj, TopologyDefinition)
                    and obj is not TopologyDefinition
                ):
                    if not hasattr(obj, "name"):
                        raise ValueError(
                            f"Topology class {obj.__name__} "
                            f"in {module_path} is missing 'name'"
                        )

                    debug(
                        f"TopologyLoader: registered topology '{obj.name}'"
                    )

                    self.topologies[obj.name] = obj
