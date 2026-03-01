# Orchestrators Reference

## Overview

Orchestrators coordinate multiple agents to handle complex workflows.

| Type | Use Case | Flexibility |
|------|----------|-------------|
| Linear | Strict sequential tasks | Low - predefined order |
| Adaptive | Dynamic routing based on context | Medium - conditional paths |
| Graph | Complex non-linear workflows | High - any architecture |

## Linear Orchestrator

Sequential execution of agents in a predefined order.

```python
from dynamiq import Workflow
from dynamiq.flows import Flow
from dynamiq.nodes.agents import Agent
from dynamiq.nodes.agents.orchestrators.linear import LinearOrchestrator
from dynamiq.nodes.agents.orchestrators.linear_manager import LinearAgentManager

# Create agents
search_agent = Agent(
    name="Search Agent",
    llm=llm,
    role="Search for information on the web",
    tools=[search_tool]
)

writer_agent = Agent(
    name="Writer Agent",
    llm=llm,
    role="Write a summary based on research"
)

# Create orchestrator
orchestrator = LinearOrchestrator(
    name="linear-orchestrator",
    manager=LinearAgentManager(llm=llm),
    agents=[search_agent, writer_agent]
)

# Run
workflow = Workflow(flow=Flow(nodes=[orchestrator]))
result = workflow.run(input_data={"input": "Research AI trends"})
```

**Best for**: Data processing pipelines, sequential tasks with clear dependencies.

## Adaptive Orchestrator

Dynamic routing based on real-time context and task progress.

```python
from dynamiq.nodes.agents.orchestrators.adaptive import AdaptiveOrchestrator
from dynamiq.nodes.agents.orchestrators.adaptive_manager import AdaptiveAgentManager

# Mix of agent types
react_agent = Agent(
    name="Complex Task Agent",
    llm=llm,
    role="Handle complex queries",
    tools=[search_tool, python_tool]
)

simple_agent = Agent(
    name="Simple Task Agent",
    llm=llm,
    role="Handle simple queries"
)

orchestrator = AdaptiveOrchestrator(
    name="adaptive-orchestrator",
    manager=AdaptiveAgentManager(llm=llm),
    agents=[react_agent, simple_agent]
)
```

**Best for**: Customer support, dynamic workflows, context-dependent routing.

## Graph Orchestrator

Maximum flexibility for complex, non-linear agent interactions.

### Basic Structure

```python
from dynamiq.nodes.agents.orchestrators.graph import GraphOrchestrator, START, END
from dynamiq.nodes.agents.orchestrators.graph_manager import GraphAgentManager

orchestrator = GraphOrchestrator(
    name="graph-orchestrator",
    manager=GraphAgentManager(llm=llm)
)

# Add states with tasks (agents)
orchestrator.add_state_by_tasks("research", [research_agent])
orchestrator.add_state_by_tasks("write", [writer_agent])

# Define edges (flow)
orchestrator.add_edge(START, "research")
orchestrator.add_edge("research", "write")
orchestrator.add_edge("write", END)

# Run
result = orchestrator.run(input_data={"input": "Task description"})
```

### Conditional Edges

```python
def router(context: dict, **kwargs) -> str:
    """Determine next state based on context."""
    if context.get("needs_refinement", False):
        return "refine"
    return END

# Add conditional edge
orchestrator.add_conditional_edge(
    "review",                    # Source state
    ["refine", END],             # Possible destinations
    router                       # Router function
)
```

### Multi-Task States

```python
# A state can have multiple tasks executed in parallel
orchestrator.add_state_by_tasks("parallel_work", [agent1, agent2, agent3])
```

### Context Management

The Graph Orchestrator maintains internal context:

```python
# Context structure
{
    "history": [
        {"content": "message", "type": "user|system|admin"}
    ],
    "key": "value",  # Custom data
    ...
}
```

**Python nodes must return:**
```python
def run(input_data) -> dict:
    return {"result": "output for history", "custom_key": "custom_value"}
```

### Complete Graph Example

```python
from dynamiq.nodes.agents.orchestrators.graph import GraphOrchestrator, START, END
from dynamiq.nodes.agents.orchestrators.graph_manager import GraphAgentManager

# Agents
email_writer = Agent(
    name="email-writer",
    llm=llm,
    role="Write personalized emails taking into account feedback."
)

# Python function for feedback
def gather_feedback(context: dict, **kwargs):
    feedback = input(f"Draft: {context.get('history', [{}])[-1].get('content')}\nFeedback: ")
    reiterate = feedback.strip().lower() not in ["send", "cancel"]
    return {"result": f"Feedback: {feedback}", "reiterate": reiterate}

def router(context: dict, **kwargs):
    if context.get("reiterate", False):
        return "write_email"
    return END

# Orchestrator
orchestrator = GraphOrchestrator(
    name="Email Orchestrator",
    manager=GraphAgentManager(llm=llm)
)

orchestrator.add_state_by_tasks("write_email", [email_writer])
orchestrator.add_state_by_tasks("get_feedback", [gather_feedback])

orchestrator.add_edge(START, "write_email")
orchestrator.add_edge("write_email", "get_feedback")
orchestrator.add_conditional_edge("get_feedback", ["write_email", END], router)

# Run
orchestrator.run(input_data={"input": "Write email about project update"})
```

## Streaming with Orchestrators

```python
orchestrator = LinearOrchestrator(
    name="streaming-orchestrator",
    manager=LinearAgentManager(llm=llm),
    agents=[agent1, agent2],
    streaming=True  # Enable streaming
)
```

## Comparison

| Feature | Linear | Adaptive | Graph |
|---------|--------|----------|-------|
| Execution | Sequential | Dynamic | Flexible |
| Branching | None | Conditional | Conditional + Loops |
| Parallel tasks | No | No | Yes |
| Feedback loops | No | No | Yes |
| Complexity | Low | Medium | High |
| Use case | Pipelines | Routing | Custom architectures |
