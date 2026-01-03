# backend/engine/visualization/graph_serializer.py

"""
Graph Serializer

Converts GraphBuilder graphs into:
- Cytoscape JSON (used by the web UI)
- Mermaid syntax (optional for docs)
- DOT / GraphViz format

This module MUST remain lightweight and format-focused.
It should not know anything about the MAS domain, only about nodes/edges.
"""

from typing import Dict, Any, List
from backend.engine.visualization.graph_builder import GraphBuilder


class GraphSerializer:
    """
    Converts GraphBuilder → various formats.
    """

    # =====================================================================
    # CYTOSCAPE FORMAT  (Used by web UI)
    # =====================================================================
    def to_cytoscape(self, graph: GraphBuilder) -> List[Dict[str, Any]]:
        """
        Converts the graph into a cytoscape.js-compatible element list.

        Output example:

        [
            {"data": {"id": "student", "label": "Students", "type": "agent"}},
            {"data": {"source": "teacher", "target": "student", "label": "teaches"}}
        ]
        """
        elements = []

        # ---- Nodes ----
        for node_id, node in graph.nodes.items():
            elements.append({
                "data": {
                    "id": node_id,
                    "label": node.get("label", node_id),
                    "type": node.get("type", "agent")
                }
            })

        # ---- Edges ----
        for edge in graph.edges:
            elements.append({
                "data": {
                    "source": edge["source"],
                    "target": edge["target"],
                    "label": edge.get("label", "")
                }
            })

        return elements

    # =====================================================================
    # MERMAID FORMAT (optional)
    # =====================================================================
    def to_mermaid(self, graph: GraphBuilder) -> str:
        """
        Graph → Mermaid Flowchart format.

        Example:

        graph TD
            teacher --> student
            admin --> teacher
        """
        lines = ["graph TD"]

        for edge in graph.edges:
            src = edge["source"]
            tgt = edge["target"]
            lbl = edge.get("label", "")

            if lbl:
                lines.append(f'    {src} -->|{lbl}| {tgt}')
            else:
                lines.append(f'    {src} --> {tgt}')

        return "\n".join(lines)

    # =====================================================================
    # DOT FORMAT
    # =====================================================================
    def to_dot(self, graph: GraphBuilder) -> str:
        """
        Converts graph into DOT (GraphViz) format.
        """
        lines = ["digraph MAS {", "  rankdir=LR;"]

        # Add nodes
        for node_id, node in graph.nodes.items():
            label = node.get("label", node_id)
            lines.append(f'  "{node_id}" [label="{label}"];')

        # Add edges
        for edge in graph.edges:
            src = edge["source"]
            tgt = edge["target"]
            lbl = edge.get("label", "")
            if lbl:
                lines.append(f'  "{src}" -> "{tgt}" [label="{lbl}"];')
            else:
                lines.append(f'  "{src}" -> "{tgt}";')

        lines.append("}")
        return "\n".join(lines)
