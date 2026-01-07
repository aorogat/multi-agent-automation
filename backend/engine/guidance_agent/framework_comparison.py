"""
Framework Comparison - Generates comparison tables for framework architectures.

Provides structured comparison data for graph-based, role-based, and GABM frameworks.
"""
from typing import Any, Dict, List


class FrameworkComparison:
    """
    Generates framework comparison tables and analysis.
    """
    
    FRAMEWORK_COMPARISON_DATA = {
        "graph-based": {
            "name": "Graph-Based",
            "overhead": "lowest",
            "scalability": "high",
            "coordination": "flexible",
            "use_cases": [
                "Complex interdependent tasks",
                "Parallel processing",
                "Flexible message passing"
            ],
            "limitations": [
                "Higher complexity in large graphs",
                "Potential for message loops",
                "No centralized control"
            ],
            "masbench_insights": [
                "Lowest overhead for message passing",
                "Best for tasks with complex dependencies",
                "Scales well with number of agents"
            ]
        },
        "role-based": {
            "name": "Role-Based (Hierarchical)",
            "overhead": "medium",
            "scalability": "medium",
            "coordination": "structured",
            "use_cases": [
                "Clear task decomposition",
                "Manager-worker patterns",
                "Structured workflows"
            ],
            "limitations": [
                "Single point of failure (coordinator)",
                "Bottleneck at coordinator",
                "Less flexible than graph-based"
            ],
            "masbench_insights": [
                "Best task decomposition",
                "Lower coordination overhead for small teams",
                "Can become bottleneck at scale"
            ]
        },
        "GABM": {
            "name": "Generative Agent-Based Modeling",
            "overhead": "highest",
            "scalability": "low",
            "coordination": "environment-mediated",
            "use_cases": [
                "Simulation environments",
                "Emergent behavior",
                "Virtual worlds"
            ],
            "limitations": [
                "Simulation only, not production",
                "High computational cost",
                "Complex environment management"
            ],
            "masbench_insights": [
                "Not suitable for production systems",
                "Best for simulation and research",
                "High overhead for environment updates"
            ]
        }
    }
    
    @staticmethod
    def generate_comparison_table() -> List[Dict[str, Any]]:
        """
        Generate a comparison table of all frameworks.
        
        Returns:
            List of framework comparison dictionaries
        """
        return [
            {
                "framework": "graph-based",
                **FrameworkComparison.FRAMEWORK_COMPARISON_DATA["graph-based"]
            },
            {
                "framework": "role-based",
                **FrameworkComparison.FRAMEWORK_COMPARISON_DATA["role-based"]
            },
            {
                "framework": "GABM",
                **FrameworkComparison.FRAMEWORK_COMPARISON_DATA["GABM"]
            }
        ]
    
    @staticmethod
    def get_framework_details(framework_type: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific framework.
        
        Args:
            framework_type: One of "graph-based", "role-based", "GABM"
        
        Returns:
            Framework details dictionary
        """
        return FrameworkComparison.FRAMEWORK_COMPARISON_DATA.get(
            framework_type,
            {}
        )
    
    @staticmethod
    def compare_frameworks(
        selected_framework: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare frameworks and explain why one was selected.
        
        Args:
            selected_framework: The selected framework type
            requirements: Requirements specification
        
        Returns:
            Comparison analysis dictionary
        """
        all_frameworks = FrameworkComparison.generate_comparison_table()
        selected_details = FrameworkComparison.get_framework_details(selected_framework)
        
        # Find rejected frameworks
        rejected = [
            fw for fw in all_frameworks
            if fw["framework"] != selected_framework
        ]
        
        return {
            "selected": {
                "framework": selected_framework,
                **selected_details
            },
            "rejected": rejected,
            "comparison_criteria": [
                "overhead",
                "scalability",
                "coordination",
                "use_cases",
                "limitations"
            ]
        }

