---
name: dynamiq
description: |
  Comprehensive framework for building agentic AI workflows and LLM applications with Dynamiq.
  Use when: (1) Building AI workflows with multiple agents, (2) Implementing RAG applications,
  (3) Creating multi-agent orchestration systems, (4) Working with LLM chains and pipelines,
  (5) Setting up vector databases for retrieval, (6) Building conversational AI with memory,
  (7) Deploying compliant GenAI applications on-premise or cloud.
---

# Dynamiq - Agentic AI Workflow Framework

Dynamiq is an orchestration framework for building end-to-end compliant GenAI applications with low-code workflows, RAG capabilities, and flexible deployment options.

## Quick Start

### Basic LLM Call
```python
from dynamiq.nodes.llms import OpenAI
from dynamiq.connections import OpenAI as OpenAIConnection
from dynamiq.prompts import Prompt, Message

llm = OpenAI(
    connection=OpenAIConnection(api_key="OPENAI_API_KEY"),
    model="gpt-4o",
    prompt=Prompt(messages=[Message(content="Translate: {{ text }}", role="user")])
)
result = llm.run(input_data={"text": "Hello"})
```

### Simple Workflow
```python
from dynamiq import Workflow

wf = Workflow()
wf.flow.add_nodes(llm)
result = wf.run(input_data={"text": "Hello"})
```

### Agent with Tools
```python
from dynamiq.nodes.agents import Agent
from dynamiq.nodes.tools import Python

agent = Agent(
    name="assistant",
    llm=llm,
    tools=[Python()],
    role="Helpful coding assistant",
    max_loops=10
)
result = agent.run(input_data={"input": "Write a hello world function"})
```

## Core Concepts

### Workflow
Container for flows that manages execution, serialization, and configuration.

### Nodes
Building blocks: LLMs, Agents, Tools, RAG components, Transformers, Validators.

### Connections
API credentials for external services (OpenAI, Anthropic, Pinecone, etc.).

### Orchestrators
Coordinate multiple agents: Linear (sequential), Adaptive (dynamic), Graph (flexible).

## Key Imports

```python
# Core
from dynamiq import Workflow
from dynamiq.flows import Flow

# LLMs
from dynamiq.nodes.llms import OpenAI, Anthropic, Gemini
from dynamiq.connections import OpenAI as OpenAIConnection

# Agents
from dynamiq.nodes.agents import Agent
from dynamiq.nodes.types import Behavior, InferenceMode

# Tools
from dynamiq.nodes.tools import Python, TavilyTool, ZenRowsTool

# RAG
from dynamiq.nodes.converters import PyPDFConverter
from dynamiq.nodes.splitters.document import DocumentSplitter
from dynamiq.nodes.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from dynamiq.nodes.writers import PineconeDocumentWriter
from dynamiq.nodes.retrievers import PineconeDocumentRetriever

# Memory
from dynamiq.memory import Memory
from dynamiq.memory.backends import InMemory

# Orchestrators
from dynamiq.nodes.agents.orchestrators.graph import GraphOrchestrator, START, END
from dynamiq.nodes.agents.orchestrators.linear import LinearOrchestrator
from dynamiq.nodes.agents.orchestrators.adaptive import AdaptiveOrchestrator

# Node Configuration
from dynamiq.nodes.node import InputTransformer, OutputTransformer, NodeDependency, ErrorHandling
```

## Reference Files

- **[llm-nodes.md](references/llm-nodes.md)**: LLM providers, configuration, inference modes
- **[agents.md](references/agents.md)**: Agent types, configuration, multi-agent delegation
- **[tools.md](references/tools.md)**: Search, scraping, execution, and utility tools
- **[rag.md](references/rag.md)**: Converters, splitters, embedders, vector stores
- **[orchestrators.md](references/orchestrators.md)**: Linear, Adaptive, Graph orchestration
- **[workflows.md](references/workflows.md)**: Workflow creation, transformers, error handling
- **[memory.md](references/memory.md)**: Memory backends, operations, configuration

## Common Patterns

### Sequential Agents
```python
agent1 = Agent(name="First", llm=llm, role="Process", id="a1")
agent2 = Agent(
    name="Second", llm=llm, role="Refine", id="a2",
    depends=[NodeDependency(agent1)],
    input_transformer=InputTransformer({"input": "$.a1.output.content"})
)
wf.flow.add_nodes([agent1, agent2])
```

### RAG Pipeline
```python
# Indexing: Converter → Splitter → Embedder → Writer
# Retrieval: TextEmbedder → Retriever → LLM
```
See [rag.md](references/rag.md) for complete examples.

### Graph Orchestrator
```python
orchestrator = GraphOrchestrator(name="Flow", manager=GraphAgentManager(llm=llm))
orchestrator.add_state_by_tasks("step1", [agent1])
orchestrator.add_state_by_tasks("step2", [agent2])
orchestrator.add_edge(START, "step1")
orchestrator.add_edge("step1", "step2")
orchestrator.add_edge("step2", END)
```

## Best Practices

- Keep modules under 500 lines
- Use type hints and Pydantic models
- Chunk 256-512 tokens with 10-20% overlap for RAG
- Start with `top_k=5` for retrieval
- Prefer hybrid search (vector + BM25) when available
- Configure error handling with retries for production
- Use memory for conversational agents
