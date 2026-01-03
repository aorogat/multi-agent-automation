"""
Assumption strategies for different field types.
Follows Strategy Pattern for Open/Closed Principle - easy to add new strategies.
"""
from typing import Any, Dict, Optional

from backend.engine.requirements_agent.interfaces import IAssumptionStrategy


class CommunicationAssumptionStrategy(IAssumptionStrategy):
    """Strategy for assuming communication method."""
    
    def can_assume(self, field_name: str, spec: Dict[str, Any]) -> bool:
        return field_name == "communication" and bool(spec.get("agents"))
    
    def assume(self, field_name: str, spec: Dict[str, Any]) -> Optional[Any]:
        if not self.can_assume(field_name, spec):
            return None
        # Default: direct messaging for most cases
        return "Participants send messages directly to each other when they need to communicate."


class TopologyAssumptionStrategy(IAssumptionStrategy):
    """Strategy for assuming topology structure."""
    
    def can_assume(self, field_name: str, spec: Dict[str, Any]) -> bool:
        return field_name == "topology" and bool(spec.get("agents"))
    
    def assume(self, field_name: str, spec: Dict[str, Any]) -> Optional[Any]:
        if not self.can_assume(field_name, spec):
            return None
        
        agents = spec.get("agents", [])
        if not agents:
            return None
        
        agent_count = sum(agent.get("count", 1) for agent in agents)
        
        if len(agents) == 1 or agent_count <= 10:
            # Single agent type or small system - fully connected
            return {
                "type": "fully_connected",
                "params": {},
                "dynamic": False
            }
        else:
            # Larger system - suggest hierarchy if there's a manager/coordinator type
            has_manager = any(
                "manager" in agent.get("type", "").lower() or 
                "coordinator" in agent.get("type", "").lower() or
                "leader" in agent.get("type", "").lower()
                for agent in agents
            )
            if has_manager:
                return {
                    "type": "hierarchy",
                    "params": {"levels": 2},
                    "dynamic": False
                }
            else:
                return {
                    "type": "mesh",
                    "params": {},
                    "dynamic": False
                }


class MemoryAssumptionStrategy(IAssumptionStrategy):
    """Strategy for assuming memory configuration."""
    
    def can_assume(self, field_name: str, spec: Dict[str, Any]) -> bool:
        return field_name == "memory" and bool(spec.get("agents"))
    
    def assume(self, field_name: str, spec: Dict[str, Any]) -> Optional[Any]:
        if not self.can_assume(field_name, spec):
            return None
        # Default: per-agent memory
        return {
            "type": "per_agent",
            "persistence": True,
            "capacity": "unlimited"
        }


class PlanningAssumptionStrategy(IAssumptionStrategy):
    """Strategy for assuming planning configuration."""
    
    def can_assume(self, field_name: str, spec: Dict[str, Any]) -> bool:
        return field_name == "planning" and bool(spec.get("agents"))
    
    def assume(self, field_name: str, spec: Dict[str, Any]) -> Optional[Any]:
        if not self.can_assume(field_name, spec):
            return None
        
        agents = spec.get("agents", [])
        if not agents:
            return None
        
        # Check for coordinator/planner agent type
        has_coordinator = any(
            "coordinator" in agent.get("type", "").lower() or
            "planner" in agent.get("type", "").lower()
            for agent in agents
        )
        
        if has_coordinator:
            coordinator_type = next(
                agent.get("type") for agent in agents
                if "coordinator" in agent.get("type", "").lower() or
                   "planner" in agent.get("type", "").lower()
            )
            return {
                "enabled": True,
                "type": "dedicated_agent",
                "agent_type": coordinator_type,
                "horizon": 5,
                "replanning": True
            }
        else:
            return {
                "enabled": True,
                "type": "lightweight",
                "horizon": 3,
                "replanning": True
            }

