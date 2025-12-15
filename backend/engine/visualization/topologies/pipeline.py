from .topology_base import TopologyDefinition


class PipelineTopology(TopologyDefinition):
    """
    FLEXIBLE PIPELINE TOPOLOGY (TYPE-AWARE)

    Supports:
    - fan-in / fan-out
    - node-level connections
    - type-level connections (group expansion)
    - forward-only DAG semantics
    """

    # ------------------------------------------------------------------
    # REGISTRY NAME
    # ------------------------------------------------------------------
    name = "pipeline"

    # ------------------------------------------------------------------
    # HUMAN DESCRIPTION
    # ------------------------------------------------------------------
    description = (
        "An ordered execution pipeline supporting fan-in and fan-out. "
        "Connections may be defined at the node level or the node-type level."
    )

    # ------------------------------------------------------------------
    # LLM GUIDANCE
    # ------------------------------------------------------------------
    ir_hints = """
PIPELINE TOPOLOGY (TYPE-AWARE, MUST FOLLOW):

1) Nodes represent ORDERED execution stages.
2) Connections flow ONLY forward.
3) A connection source/target may be:
   - a node id (e.g., teacher_1)
   - a node type (e.g., teacher)
4) Type-level connections expand automatically.
5) Fan-in and fan-out are allowed.
6) Cycles are NOT allowed.

Example:
principal → teacher → student
"""

    # ------------------------------------------------------------------
    # PARAMETERS
    # ------------------------------------------------------------------
    params_schema = {
        "connections": {
            "type": "dict",
            "description": "Mapping of source (node id or type) to target list."
        }
    }

    default_params = {
        "connections": None
    }

    # ------------------------------------------------------------------
    # EXECUTION LOGIC
    # ------------------------------------------------------------------
    @classmethod
    def build_edges(cls, nodes, params):
        params = cls.merge_params(params)
        edges = []

        if len(nodes) < 2:
            return edges

        # ---------------------------------------
        # 1. Build helpers
        # ---------------------------------------
        ordered_ids = [n["data"]["id"] for n in nodes]
        index = {nid: i for i, nid in enumerate(ordered_ids)}

        # group nodes by base type
        by_type = {}
        for nid in ordered_ids:
            base = nid.rsplit("_", 1)[0]
            by_type.setdefault(base, []).append(nid)

        connections = params.get("connections")

        # ---------------------------------------
        # 2. Default linear pipeline
        # ---------------------------------------
        if not connections:
            for i in range(len(ordered_ids) - 1):
                edges.append({
                    "data": {
                        "source": ordered_ids[i],
                        "target": ordered_ids[i + 1]
                    }
                })
            return edges

        # ---------------------------------------
        # 3. Expand connections (type OR node)
        # ---------------------------------------
        def resolve(key):
            """
            Resolve a key to a list of node ids.
            Key may be a node id or a node type.
            """
            if key in by_type:
                return by_type[key]
            if key in index:
                return [key]
            return []

        for src_key, tgt_keys in connections.items():
            src_nodes = resolve(src_key)

            for tgt_key in tgt_keys:
                tgt_nodes = resolve(tgt_key)

                for src in src_nodes:
                    for tgt in tgt_nodes:
                        # enforce forward-only
                        if index[tgt] <= index[src]:
                            raise ValueError(
                                f"Invalid pipeline edge {src} → {tgt}: "
                                "edges must go forward only."
                            )

                        edges.append({
                            "data": {
                                "source": src,
                                "target": tgt
                            }
                        })

        return edges
