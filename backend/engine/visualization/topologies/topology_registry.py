# backend/engine/visualization/topologies/topology_registry.py

import pkgutil
import inspect
from .topology_base import TopologyDefinition
import backend.engine.visualization.topologies as topologies_pkg


def load_topologies():
    """Auto-discovers topology definitions without modifying this file."""

    topologies = {}

    package = topologies_pkg
    prefix = package.__name__ + "."

    for _, module_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        module = __import__(module_name, fromlist=["dummy"])

        # Find subclasses of TopologyDefinition
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, TopologyDefinition) and obj is not TopologyDefinition:
                instance = obj()
                topologies[instance.name] = instance

    return topologies
