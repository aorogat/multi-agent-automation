# backend/engine/visualization/graph_builder.py

from __future__ import annotations

from typing import Any, Dict, List, Type

from backend.utils.logger import debug
from backend.engine.visualization.topologies.loader import TopologyLoader
from backend.engine.visualization.topologies.topology_base import TopologyDefinition


class GraphBuilder:
    """
    Converts an Intermediate Representation (IR) into a Cytoscape graph.

    IR format (always):
    {
        "topology": "star" | "pipeline" | "hierarchy" | ...
        "nodes": [
            {"id": "students", "label": "Students", "count": 200},
            {"id": "teachers", "label": "Teachers", "count": 10}
        ],
        "params": { ... }   # optional topology-specific parameters
    }

    Output graph format:
    [
      {"data": {"id": "students_1", "label": "Students"}},
      ...
      {"data": {"source": "...", "target": "...", "id": "edge_1"}}
    ]
    """

    def __init__(self) -> None:
        loader = TopologyLoader()

        # Support both styles:
        # - loader.topologies (your current code)
        # - loader.load() (older GraphBuilder refactor attempt)
        topo_map = None
        if hasattr(loader, "topologies") and isinstance(loader.topologies, dict):
            topo_map = loader.topologies
        elif hasattr(loader, "load") and callable(getattr(loader, "load")):
            topo_map = loader.load()
        else:
            topo_map = {}

        # Normalize: map name -> class
        self._topology_classes: Dict[str, Type[TopologyDefinition]] = {}
        for name, cls in topo_map.items():
            # cls might already be a TopologyDefinition subclass
            self._topology_classes[name] = cls

        debug(f"GraphBuilder: loaded topologies: {list(self._topology_classes.keys())}")



    def _color_for_type(self, node_type: str) -> str:
        """
        Deterministically assign a color per node type.
        Same type => same color across runs.
        """
        palette = [
            "#1f77b4",  # blue
            "#ff7f0e",  # orange
            "#2ca02c",  # green
            "#d62728",  # red
            "#9467bd",  # purple
            "#8c564b",  # brown
            "#e377c2",  # pink
            "#7f7f7f",  # gray
            "#bcbd22",  # olive
            "#17becf",  # cyan
        ]

        idx = abs(hash(node_type)) % len(palette)
        return palette[idx]

    # ------------------------------------------------------------------
    # MAIN ENTRY
    # ------------------------------------------------------------------
    def build(self, ir: Dict[str, Any]) -> List[Dict[str, Any]]:
        debug(f"GraphBuilder received IR:\n{ir}")

        if not isinstance(ir, dict):
            raise ValueError("IR must be a dict.")

        topology = ir.get("topology")
        if not topology:
            raise ValueError("IR missing required field: topology")

        node_groups = ir.get("nodes", [])
        if not isinstance(node_groups, list):
            raise ValueError("IR field 'nodes' must be a list.")

        params = ir.get("params", {}) or {}
        if not isinstance(params, dict):
            raise ValueError("IR field 'params' must be a dict if present.")

        topo_cls = self._topology_classes.get(topology)
        if topo_cls is None:
            raise ValueError(
                f"Unsupported topology: {topology}. "
                f"Available: {list(self._topology_classes.keys())}"
            )

        topo = topo_cls()

        # 1) Expand logical node groups -> concrete instance nodes
        flat_nodes = self._expand_node_instances(node_groups)

        # 2) Build edges using topology implementation
        # TopologyDefinition should expose: build_edges(nodes, params) -> edges
        edges = topo.build_edges(flat_nodes, params)

        # 3) Ensure edges have ids (Cytoscape works without, but ids help)
        edges = self._ensure_edge_ids(edges)

        final_graph = flat_nodes + edges
        debug(f"GraphBuilder produced graph with {len(final_graph)} elements")
        return final_graph

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------
    def _expand_node_instances(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert logical groups into instance nodes.
        Example group:
           {"id": "students", "label": "Students", "count": 3}
        becomes:
           students_1, students_2, students_3
        """
        flat: List[Dict[str, Any]] = []

        for group in nodes:
            if not isinstance(group, dict):
                continue

            base_id = str(group.get("id", "")).strip()
            label = str(group.get("label", base_id)).strip() or base_id
            count = int(group.get("count", 1) or 1)

            if not base_id:
                continue

            for i in range(1, count + 1):
                instance_id = f"{base_id}_{i}"
                node_type = base_id
                color = self._color_for_type(node_type)

                flat.append({
                    "data": {
                        "id": instance_id,
                        "label": label,
                        "type": node_type,
                        "color": color,
                    }
                })


        return flat

    def _ensure_edge_ids(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adds missing edge ids to avoid collisions / help debugging.
        """
        out: List[Dict[str, Any]] = []
        for idx, e in enumerate(edges, start=1):
            if not isinstance(e, dict) or "data" not in e or not isinstance(e["data"], dict):
                continue
            data = e["data"]
            # If edge already has an id, keep it
            if "id" not in data:
                src = data.get("source", "src")
                tgt = data.get("target", "tgt")
                data["id"] = f"e_{idx}_{src}_to_{tgt}"
            out.append({"data": data})
        return out
