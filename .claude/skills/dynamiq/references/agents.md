# Agents Reference

## Agent Types

| Type | Use Case | Tools | Processing |
|------|----------|-------|------------|
| Simple Agent | Content generation, formatting, summarization | None | Single-turn |
| ReAct Agent | Complex tasks, research, data gathering | Extensive | Multiple loops |
| Reflection Agent | Fact-sensitive, high-accuracy needs | Extensive | Multiple loops + self-assessment |

## Agent Configuration

### ReAct Agent

```python
from dynamiq.nodes.agents import Agent
from dynamiq.nodes.types import Behavior, InferenceMode

agent = Agent(
    name="react-agent",
    llm=llm,                              # Required: LLM instance
    tools=[search_tool, python_tool],     # Tools the agent can use
    role="Senior Data Scientist",         # Agent's persona/role
    max_loops=10,                         # Max reasoning cycles
    inference_mode=InferenceMode.XML,     # Output format
    behaviour_on_max_loops=Behavior.RETURN,  # Action at max loops
    direct_tool_output_enabled=False,     # Return raw tool outputs
    memory=memory                         # Optional: Memory instance
)
```

### Simple Agent

```python
agent = Agent(
    name="simple-agent",
    llm=llm,
    role="Professional writer that produces clear, concise summaries"
)
```

### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "Agent" | Identifier for logging |
| `llm` | LLM | Required | Language model instance |
| `tools` | list | [] | Available tools |
| `role` | str | Required | Agent's behavior/purpose |
| `max_loops` | int | 15 | Maximum reasoning cycles |
| `inference_mode` | InferenceMode | DEFAULT | Output format |
| `behaviour_on_max_loops` | Behavior | RAISE | Action when max loops reached |
| `memory` | Memory | None | Conversation memory |

## Behavior Options

```python
from dynamiq.nodes.types import Behavior

Behavior.RAISE   # Raise exception at max loops
Behavior.RETURN  # Return current result at max loops
```

## Running Agents

```python
# Synchronous
result = agent.run(input_data={"input": "Analyze this data"})

# Asynchronous
result = await agent.run(input_data={"input": "Analyze this data"})

# Access output
print(result.output.get("content"))
```

## Agent with Memory

```python
from dynamiq.memory import Memory
from dynamiq.memory.backends import InMemory

memory = Memory(backend=InMemory())

agent = Agent(
    name="chatbot",
    llm=llm,
    role="helpful assistant",
    memory=memory
)

# Memory persists across runs
response1 = agent.run({"input": "My name is John", "user_id": "user1", "session_id": "session1"})
response2 = agent.run({"input": "What's my name?", "user_id": "user1", "session_id": "session1"})
```

## Multi-Agent Delegation

Agents can use other agents as tools:

```python
research_agent = Agent(
    name="Research Analyst",
    role="Find recent market news and provide highlights.",
    llm=llm,
    tools=[search_tool]
)

writer_agent = Agent(
    name="Brief Writer",
    role="Turn research highlights into a concise brief.",
    llm=llm
)

manager_agent = Agent(
    name="Manager",
    role="Delegate research and writing to sub-agents.",
    llm=llm,
    tools=[research_agent, writer_agent],
    parallel_tool_calls_enabled=True
)
```
