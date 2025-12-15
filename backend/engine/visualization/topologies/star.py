from .topology_base import TopologyDefinition


class StarTopology(TopologyDefinition):
    """
    STAR TOPOLOGY

    A central hub node connected to all other nodes.
    Commonly used for coordinator, orchestrator, or router agents.
    """

    # ------------------------------------------------------------------
    # REGISTRY NAME
    # ------------------------------------------------------------------
    name = "star"

    # ------------------------------------------------------------------
    # HUMAN DESCRIPTION
    # ------------------------------------------------------------------
    description = (
        "A star-shaped structure with a single central node. "
        "All other nodes connect directly to the center, enabling "
        "fast coordination and centralized control."
    )

    # ------------------------------------------------------------------
    # LLM GUIDANCE
    # ------------------------------------------------------------------
    ir_hints = """
STAR TOPOLOGY (MUST FOLLOW):

1) Exactly ONE node acts as the CENTER.
2) All other nodes connect directly to the center.
3) No edges exist between non-center nodes.
4) The center may optionally be inferred automatically.

PARAMS FORMAT:
- center: node id OR node type acting as the hub

Example:
center = "manager"
"""

    # ------------------------------------------------------------------
    # PARAMETERS SCHEMA
    # ------------------------------------------------------------------
    params_schema = {
        "center": {
            "type": "string",
            "description": "Node id or node type to use as the star center."
        }
    }

    # ------------------------------------------------------------------
    # DEFAULT PARAMETERS
    # ------------------------------------------------------------------
    default_params = {
        "center": None  # inferred automatically
    }

    # ------------------------------------------------------------------
    # IR EXAMPLE
    # ------------------------------------------------------------------
    ir_example = {
        "topology": "star",
        "nodes": [
            {"id": "manager", "label": "Manager", "count": 1},
            {"id": "worker", "label": "Worker", "count": 6}
        ],
        "params": {
            "center": "manager"
        }
    }

    # ------------------------------------------------------------------
    # EXECUTION LOGIC
    # ------------------------------------------------------------------
    @classmethod
    def build_edges(cls, nodes, params):
        params = cls.merge_params(params)
        edges = []

        # -------------------------------
        # 1. GROUP NODES BY BASE TYPE
        # -------------------------------
        by_type = {}
        for n in nodes:
            base = n["data"]["id"].rsplit("_", 1)[0]
            by_type.setdefault(base, []).append(n["data"]["id"])

        # -------------------------------
        # 2. RESOLVE CENTER NODE(S)
        # -------------------------------
        center_param = params.get("center")

        center_nodes = []

        # Case A: explicit center type
        if center_param in by_type:
            center_nodes = by_type[center_param]

        # Case B: explicit center node id
        else:
            for ids in by_type.values():
                for nid in ids:
                    if nid == center_param:
                        center_nodes = [nid]
                        break

        # Case C: infer automatically (single highest-priority node)
        if not center_nodes:
            # Prefer unique node types with count == 1
            for ids in by_type.values():
                if len(ids) == 1:
                    center_nodes = ids
                    break

        # Final fallback
        if not center_nodes:
            center_nodes = [nodes[0]["data"]["id"]]

        # Star supports ONE center
        center = center_nodes[0]

        # -------------------------------
        # 3. CONNECT ALL OTHERS TO CENTER
        # -------------------------------
        for n in nodes:
            nid = n["data"]["id"]
            if nid == center:
                continue

            edges.append({
                "data": {
                    "source": center,
                    "target": nid
                }
            })

        return edges
