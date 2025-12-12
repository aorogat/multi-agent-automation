# backend/engine/visualization/topologies/topology_base.py

class TopologyDefinition:
    """Base class for graph topology definitions."""

    name = "undefined_topology"
    description = ""
    rules = ""
    example = ""

    @classmethod
    def as_text_block(cls):
        """Generate an LLM-friendly description block."""
        return f"""
### {cls.name}
Description:
{cls.description}

Rules:
{cls.rules}

Example (JSON-like pseudo-structure):
{cls.example}
""".strip()
