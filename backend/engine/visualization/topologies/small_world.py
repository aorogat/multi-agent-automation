from .topology_base import TopologyDefinition
import random


class SmallWorldTopology(TopologyDefinition):
    """
    SMALL-WORLD TOPOLOGY

    High local clustering + short global paths.
    Inspired by Watts–Strogatz small-world networks.

    Typical use cases:
    - Social-style agent interaction
    - Knowledge diffusion
    - Brain-inspired coordination
    - Peer-to-peer MAS
    """

    # ------------------------------------------------------------------
    # REGISTRY NAME
    # ------------------------------------------------------------------
    name = "small_world"

    # ------------------------------------------------------------------
    # HUMAN DESCRIPTION
    # ------------------------------------------------------------------
    description = (
        "A small-world network with strong local clustering and a few "
        "long-range shortcut connections, enabling efficient global reachability."
    )

    # ------------------------------------------------------------------
    # LLM GUIDANCE
    # ------------------------------------------------------------------
    ir_hints = """
SMALL-WORLD TOPOLOGY (MUST FOLLOW):

1) Nodes form local neighborhoods (high clustering).
2) Each node connects to K nearest neighbors.
3) A small fraction of edges are rewired to distant nodes.
4) Resulting graph has short average path lengths.
5) Connections are peer-to-peer (no strict hierarchy).

PARAMS:
- node_type: type of nodes to connect (optional)
- k: number of local neighbors per node (even number)
- rewiring_prob: probability of long-range rewiring (0.0–1.0)

Example:
node_type = "student"
k = 6
rewiring_prob = 0.1
"""

    # ------------------------------------------------------------------
    # PARAMETERS SCHEMA
    # ------------------------------------------------------------------
    params_schema = {
        "node_type": {
            "type": "string",
            "description": "Node type to apply the small-world structure to."
        },
        "k": {
            "type": "int",
            "description": "Number of local neighbors per node (even number)."
        },
        "rewiring_prob": {
            "type": "float",
            "description": "Probability of rewiring an edge to a random node."
        }
    }

    # ------------------------------------------------------------------
    # DEFAULT PARAMETERS
    # ------------------------------------------------------------------
    default_params = {
        "node_type": None,     # apply to all nodes
        "k": 4,                # small local neighborhood
        "rewiring_prob": 0.1   # few shortcuts
    }

    # ------------------------------------------------------------------
    # IR EXAMPLE
    # ------------------------------------------------------------------
    ir_example = {
        "topology": "small_world",
        "nodes": [
            {"id": "student", "label": "Student", "count": 100}
        ],
        "params": {
            "node_type": "student",
            "k": 6,
            "rewiring_prob": 0.1
        }
    }

    # ------------------------------------------------------------------
    # EXECUTION LOGIC
    # ------------------------------------------------------------------
    @classmethod
    def build_edges(cls, nodes, params):
        params = cls.merge_params(params)
        edges = []

        node_type = params.get("node_type")
        k = params.get("k")
        rewiring_prob = params.get("rewiring_prob")

        # -------------------------------
        # 1. SELECT NODES
        # -------------------------------
        all_ids = [n["data"]["id"] for n in nodes]

        by_type = {}
        for nid in all_ids:
            base = nid.rsplit("_", 1)[0]
            by_type.setdefault(base, []).append(nid)

        if node_type:
            node_ids = by_type.get(node_type, [])
        else:
            node_ids = all_ids

        n = len(node_ids)
        if n < 3:
            return edges

        # Ensure valid k
        k = min(k, n - 1)
        if k % 2 != 0:
            k -= 1

        # -------------------------------
        # 2. BUILD LOCAL RING LATTICE
        # -------------------------------
        for i, src in enumerate(node_ids):
            for j in range(1, k // 2 + 1):
                tgt = node_ids[(i + j) % n]

                # Rewire with probability p
                if random.random() < rewiring_prob:
                    tgt = random.choice(node_ids)
                    if tgt == src:
                        continue

                edges.append({
                    "data": {
                        "source": src,
                        "target": tgt
                    }
                })

        return edges
