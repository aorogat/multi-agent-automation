# backend/engine/visualization/graph_builder.py

from typing import Dict, Any, List
from backend.utils.logger import debug


class GraphBuilder:
    """
    Converts an Intermediate Representation (IR) into a final visualization graph.

    The IR format is always:
    {
        "topology": "star" | "pipeline" | "hierarchy" | ...
        "nodes": [
            {"id": "students", "label": "Students", "count": 200},
            {"id": "teachers", "label": "Teachers", "count": 10}
        ],
        "params": { ... }   # topology-specific parameters
    }

    GraphBuilder produces a final graph:
    [
        {"data": {"id": "students_1", "label": "Students"}},
        {"data": {"id": "students_2", "label": "Students"}},
        ...
        {"data": {"id": "teachers_1", "label": "Teachers"}},
        ...
        {"data": {"source": "...", "target": "..."}}
    ]

    Topology logic is in separate builder functions.
    Contributors add new topology functions in the TOPOLOGY_BUILDERS dict.
    """

    # ------------------------------------------------------------------
    # TOPOLOGY REGISTRY (EASY TO EXTEND)
    # ------------------------------------------------------------------
    def __init__(self):
        self.TOPOLOGY_BUILDERS = {
            "star": self._build_star_topology,
            "pipeline": self._build_pipeline_topology,
            "hierarchy": self._build_hierarchy_topology,
            "p2p": self._build_p2p_mesh,
        }

    # ------------------------------------------------------------------
    # MAIN ENTRY POINT
    # ------------------------------------------------------------------
    def build(self, ir: Dict[str, Any]) -> List[Dict[str, Any]]:
        debug(f"GraphBuilder received IR:\n{ir}")

        topology = ir.get("topology")
        nodes = ir.get("nodes", [])
        params = ir.get("params", {})

        if topology not in self.TOPOLOGY_BUILDERS:
            raise ValueError(f"Unsupported topology: {topology}")

        # Build full node list with instance IDs
        flat_nodes = self._expand_node_instances(nodes)

        # Topology builder returns edges only
        edges = self.TOPOLOGY_BUILDERS[topology](flat_nodes, params)

        final_graph = flat_nodes + edges
        debug(f"GraphBuilder produced graph with {len(final_graph)} elements")
        return final_graph

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------
    def _expand_node_instances(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert logical node groups into individual graph nodes.
        Example:
           {"id": "students", "label": "Students", "count": 3}
        becomes:
           students_1, students_2, students_3
        """
        flat = []

        for group in nodes:
            base_id = group["id"]
            label = group["label"]
            count = group.get("count", 1)

            for i in range(1, count + 1):
                instance_id = f"{base_id}_{i}"
                flat.append({
                    "data": {
                        "id": instance_id,
                        "label": label
                    }
                })

        return flat

    # ==================================================================
    #            TOPOLOGY BUILDERS (AUTONOMOUS MODULES)
    # ==================================================================

    # -------------------------
    # STAR (hub-and-spoke)
    # -------------------------
    def _build_star_topology(self, nodes: List[Dict[str, Any]], params: Dict[str, Any]):
        edges = []

        if not nodes:
            return edges

        hub = nodes[0]["data"]["id"]

        for n in nodes[1:]:
            edges.append({
                "data": {
                    "source": hub,
                    "target": n["data"]["id"]
                }
            })

        return edges

    # -------------------------
    # PIPELINE (linear chain)
    # -------------------------
    def _build_pipeline_topology(self, nodes: List[Dict[str, Any]], params: Dict[str, Any]):
        edges = []

        for i in range(len(nodes) - 1):
            edges.append({
                "data": {
                    "source": nodes[i]["data"]["id"],
                    "target": nodes[i + 1]["data"]["id"]
                }
            })

        return edges

    # -------------------------
    # HIERARCHY (tree)
    # params:
    #   branch_factor (default 2)
    # -------------------------
    def _build_hierarchy_topology(self, nodes: List[Dict[str, Any]], params: Dict[str, Any]):
        edges = []

        if not nodes:
            return edges

        branch = int(params.get("branch_factor", 2))
        root = nodes[0]["data"]["id"]

        queue = [root]
        idx = 1
        total = len(nodes)

        while queue and idx < total:
            parent = queue.pop(0)
            for _ in range(branch):
                if idx >= total:
                    break
                child = nodes[idx]["data"]["id"]
                edges.append({"data": {"source": parent, "target": child}})
                queue.append(child)
                idx += 1

        return edges

    # -------------------------
    # PEER-TO-PEER MESH
    # -------------------------
    def _build_p2p_mesh(self, nodes: List[Dict[str, Any]], params: Dict[str, Any]):
        edges = []
        total = len(nodes)

        for i in range(total):
            for j in range(i + 1, total):
                edges.append({
                    "data": {
                        "source": nodes[i]["data"]["id"],
                        "target": nodes[j]["data"]["id"]
                    }
                })

        return edges
