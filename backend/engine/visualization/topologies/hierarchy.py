from .topology_base import TopologyDefinition


class HierarchyTopology(TopologyDefinition):
    """
    HIERARCHY TOPOLOGY (TYPED)

    A multi-level tree where each level can represent a different
    agent role (e.g., Principal → Teacher → Student).
    """

    # ------------------------------------------------------------------
    # REGISTRY NAME
    # ------------------------------------------------------------------
    name = "hierarchy"

    # ------------------------------------------------------------------
    # HUMAN DESCRIPTION
    # ------------------------------------------------------------------
    description = (
        "A tree-based structure with explicit hierarchy levels. "
        "Each level may represent a different agent role, such as "
        "managers supervising workers or teachers supervising students."
    )

    # ------------------------------------------------------------------
    # LLM GUIDANCE
    # ------------------------------------------------------------------
    ir_hints = """
HIERARCHY TOPOLOGY WITH ROLES (MUST FOLLOW):

1) Nodes are organized into LEVELS.
2) Level 0 represents the ROOT role and may contain one or more nodes.
3) If Level 0 has ONE node, it connects to ALL nodes in Level 1.
4) If Level 0 has MULTIPLE nodes, they form a circular coordination layer.
5) Each level i (i > 0) connects ONLY to level i+1.
6) Each child has exactly ONE parent.
7) No cycles across hierarchy levels (cycles allowed only at level 0).
8) Leaf nodes appear only at the last level.

PARAMS FORMAT:
- levels: ordered list of node ids defining hierarchy roles
- branch_factor: list defining fan-out per level

Example:
levels = ["principal", "teacher", "student"]
branch_factor = [1, 4, 10]
"""

    # ------------------------------------------------------------------
    # PARAMETERS SCHEMA
    # ------------------------------------------------------------------
    params_schema = {
        "levels": {
            "type": "list",
            "description": "Ordered list of node labels representing hierarchy levels."
        },
        "branch_factor": {
            "type": "list",
            "description": "Fan-out per level (length = len(levels) - 1)."
        }
    }

    default_params = {
        "levels": None,        # inferred from nodes
        "branch_factor": 2     # safe, shallow tree
    }

    # ------------------------------------------------------------------
    # IR EXAMPLE
    # ------------------------------------------------------------------
    ir_example = {
        "topology": "hierarchy",
        "nodes": [
            {"id": "principal", "label": "Principal", "count": 1},
            {"id": "teacher", "label": "Teacher", "count": 5},
            {"id": "student", "label": "Student", "count": 100}
        ],
        "params": {
            "levels": ["principal", "teacher", "student"],
            "branch_factor": [5, 20]
        }
    }

    # ------------------------------------------------------------------
    # EXECUTION LOGIC
    # ------------------------------------------------------------------
    @classmethod
    def build_edges(cls, nodes, params):
        params = cls.merge_params(params)
        edges = []

        levels = params.get("levels")
        branch_factor = params.get("branch_factor")

        # -------------------------------
        # 1. GROUP NODES BY TYPE
        # -------------------------------
        by_type = {}
        for n in nodes:
            base = n["data"]["id"].rsplit("_", 1)[0]
            by_type.setdefault(base, []).append(n["data"]["id"])

        # -------------------------------
        # 2. INFER LEVELS (SMART)
        # Administrator > Principal > Teacher > Student
        # -------------------------------
        if not levels:
            priority = ["administrator", "principal", "teacher", "student"]
            levels = [p for p in priority if p in by_type]

        # -------------------------------
        # 3. NORMALIZE BRANCH FACTOR
        # -------------------------------
        if isinstance(branch_factor, int):
            branch_factor = [branch_factor] * (len(levels) - 1)

        if not branch_factor:
            branch_factor = [2] * (len(levels) - 1)

        # -------------------------------
        # 4. HANDLE LEVEL-0 SPECIAL CASES
        # -------------------------------
        level0 = levels[0]
        level1 = levels[1] if len(levels) > 1 else None

        level0_nodes = by_type.get(level0, [])
        level1_nodes = by_type.get(level1, []) if level1 else []

        # Case A: Single root → connect to ALL level-1 nodes
        if len(level0_nodes) == 1 and level1_nodes:
            root = level0_nodes[0]
            for child in level1_nodes:
                edges.append({
                    "data": {
                        "source": root,
                        "target": child
                    }
                })

        # Case B: Multiple roots → circular coordination layer
        elif len(level0_nodes) > 1:
            for i in range(len(level0_nodes)):
                edges.append({
                    "data": {
                        "source": level0_nodes[i],
                        "target": level0_nodes[(i + 1) % len(level0_nodes)]
                    }
                })

        # -------------------------------
        # 5. BUILD HIERARCHICAL TREE
        # -------------------------------
        # Skip level-0 → level-1 if single-root case already handled
        start_level = 1 if len(level0_nodes) == 1 else 0

        for i in range(start_level, len(levels) - 1):
            parents = by_type.get(levels[i], [])
            children = by_type.get(levels[i + 1], [])

            if not parents or not children:
                continue

            fanout = branch_factor[i]
            child_idx = 0

            for p in parents:
                for _ in range(fanout):
                    if child_idx >= len(children):
                        break
                    edges.append({
                        "data": {
                            "source": p,
                            "target": children[child_idx]
                        }
                    })
                    child_idx += 1

        return edges
