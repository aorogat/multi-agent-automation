# Requirements Agent - SOLID Architecture

This module follows SOLID principles for easy modification and expansion.

## Architecture Overview

The requirements agent is split into focused, single-responsibility components:

```
requirements_agent/
├── interfaces.py              # Abstract interfaces (DIP)
├── agent.py                   # Main orchestrator
├── conversation_manager.py    # Conversation flow management
├── assumption_engine.py       # Assumption orchestration
├── assumption_strategies.py   # Assumption strategies (Strategy Pattern)
├── prompt_builder.py          # LLM prompt construction
├── schema_formatter.py        # Schema formatting for LLM
├── field_validator.py         # Field validation
├── spec_model.py              # Specification data model
└── spec_schema.py             # Schema definition
```

## SOLID Principles Applied

### 1. Single Responsibility Principle (SRP)

Each class has one reason to change:

- **ConversationManager**: Only handles conversation flow and question prioritization
- **AssumptionEngine**: Only orchestrates assumption strategies
- **AssumptionStrategies**: Each strategy handles one field type
- **PromptBuilder**: Only builds prompts
- **SchemaFormatter**: Only formats schema information
- **FieldValidator**: Only validates fields
- **RequirementsAgent**: Only orchestrates the process

### 2. Open/Closed Principle (OCP)

The system is open for extension, closed for modification:

- **Adding new assumption strategies**: Just create a new class implementing `IAssumptionStrategy` and add it to the strategies list. No need to modify existing code.
- **Changing prompt format**: Implement a new `IPromptBuilder` and inject it.
- **Different conversation logic**: Implement `IConversationManager` and inject it.

### 3. Liskov Substitution Principle (LSP)

All implementations can be substituted with their interfaces:

- Any `IAssumptionStrategy` can replace another
- Any `IPromptBuilder` can replace another
- Any `IConversationManager` can replace another

### 4. Interface Segregation Principle (ISP)

Interfaces are focused and clients only depend on what they need:

- `IAssumptionStrategy`: Only methods needed for assumptions
- `IConversationManager`: Only methods for conversation flow
- `IPromptBuilder`: Only methods for prompt building
- `ISchemaFormatter`: Only methods for schema formatting
- `IFieldValidator`: Only methods for validation

### 5. Dependency Inversion Principle (DIP)

High-level modules depend on abstractions, not concretions:

- `RequirementsAgent` depends on interfaces, not concrete classes
- All components are injected via constructor
- Easy to swap implementations for testing or different behaviors

## How to Extend

### Adding a New Assumption Strategy

1. Create a new class implementing `IAssumptionStrategy`:

```python
from backend.engine.requirements_agent.interfaces import IAssumptionStrategy

class EnvironmentAssumptionStrategy(IAssumptionStrategy):
    def can_assume(self, field_name: str, spec: Dict[str, Any]) -> bool:
        return field_name == "environment" and bool(spec.get("agents"))
    
    def assume(self, field_name: str, spec: Dict[str, Any]) -> Optional[Any]:
        if not self.can_assume(field_name, spec):
            return None
        return {
            "type": "shared_workspace",
            "properties": {},
            "observable": True,
            "mutable": True
        }
```

2. Add it to the strategies list in `agent.py`:

```python
strategies = [
    CommunicationAssumptionStrategy(),
    TopologyAssumptionStrategy(),
    MemoryAssumptionStrategy(),
    PlanningAssumptionStrategy(),
    EnvironmentAssumptionStrategy(),  # New strategy
]
```

### Adding a Custom Prompt Builder

1. Implement `IPromptBuilder`:

```python
from backend.engine.requirements_agent.interfaces import IPromptBuilder

class CustomPromptBuilder(IPromptBuilder):
    def build_prompt(self, user_message, spec_dict, history, missing_required, next_field):
        # Your custom prompt logic
        return prompt_string
```

2. Inject it when creating `RequirementsAgent`:

```python
agent = RequirementsAgent(
    prompt_builder=CustomPromptBuilder(schema_formatter)
)
```

### Adding a Custom Conversation Manager

1. Implement `IConversationManager`:

```python
from backend.engine.requirements_agent.interfaces import IConversationManager

class CustomConversationManager(IConversationManager):
    def determine_next_field(self, spec, missing_required):
        # Your custom logic
        return next_field
    
    def get_assumable_fields(self, spec):
        # Your custom logic
        return assumable_fields
```

2. Inject it:

```python
agent = RequirementsAgent(
    conversation_manager=CustomConversationManager(field_validator)
)
```

### Testing with Mocks

Since everything uses dependency injection, testing is easy:

```python
from unittest.mock import Mock

# Create mock components
mock_conversation_manager = Mock(spec=IConversationManager)
mock_assumption_engine = Mock(spec=AssumptionEngine)
mock_prompt_builder = Mock(spec=IPromptBuilder)

# Create agent with mocks
agent = RequirementsAgent(
    conversation_manager=mock_conversation_manager,
    assumption_engine=mock_assumption_engine,
    prompt_builder=mock_prompt_builder,
)
```

## Benefits

1. **Easy to Modify**: Change one component without affecting others
2. **Easy to Extend**: Add new strategies/implementations without modifying existing code
3. **Easy to Test**: Mock dependencies for isolated unit testing
4. **Easy to Understand**: Each class has a clear, single purpose
5. **Flexible**: Swap implementations for different behaviors

## Usage

Default usage (backward compatible):

```python
from backend.engine.requirements_agent import RequirementsAgent

agent = RequirementsAgent()
result = agent.run(user_message, current_spec, history)
```

Custom usage with dependency injection:

```python
from backend.engine.requirements_agent import RequirementsAgent
from backend.engine.requirements_agent.assumption_strategies import (
    CommunicationAssumptionStrategy,
    CustomAssumptionStrategy,
)

# Create custom components
strategies = [
    CommunicationAssumptionStrategy(),
    CustomAssumptionStrategy(),
]
assumption_engine = AssumptionEngine(strategies, field_validator)

# Inject custom components
agent = RequirementsAgent(
    assumption_engine=assumption_engine,
    # ... other custom components
)
```

