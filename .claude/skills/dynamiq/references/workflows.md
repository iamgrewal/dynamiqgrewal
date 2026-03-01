# Workflows Reference

## Creating Workflows

```python
from dynamiq import Workflow
from dynamiq.flows import Flow

# Empty workflow
wf = Workflow()

# Workflow with name and version
wf = Workflow(
    name="My Workflow",
    id="unique-id",
    version="1.0.0"
)

# Workflow with pre-configured flow
wf = Workflow(flow=Flow(nodes=[agent1, agent2]))
```

## Adding Nodes

```python
# Add nodes individually
wf.flow.add_nodes(agent1)
wf.flow.add_nodes(agent2)

# Add multiple nodes
wf.flow.add_nodes([agent1, agent2, llm1])
```

## Connecting Nodes

### Method 1: Direct Connection
```python
wf.flow.add_nodes([agent1, agent2])
# Nodes execute in parallel unless dependencies are set
```

### Method 2: With Dependencies
```python
from dynamiq.nodes.node import NodeDependency, InputTransformer

first_agent = Agent(name="First", llm=llm, role="Process input", id="agent_1")

second_agent = Agent(
    name="Second",
    llm=llm,
    role="Process output of first",
    id="agent_2",
    depends=[NodeDependency(first_agent)],
    input_transformer=InputTransformer(
        selector={"input": "$.agent_1.output.content"}
    )
)

wf.flow.add_nodes([first_agent, second_agent])
```

### Method 3: Fluent API
```python
splitter = DocumentSplitter(
    split_by="sentence", split_length=10
).inputs(
    documents=converter.outputs.documents
).depends_on(converter)
```

## Input/Output Transformers

### Input Transformer
Maps outputs from previous nodes to current node inputs using JSONPath.

```python
from dynamiq.nodes.node import InputTransformer

input_transformer = InputTransformer({
    "documents": "$.retriever.output.documents",
    "query": "$.input.output.query"
})

llm = OpenAI(
    connection=conn,
    model="gpt-4o",
    input_transformer=input_transformer
)
```

**JSONPath Syntax**: `$.{node_id}.output.{parameter_name}`

### Output Transformer
Transforms output before passing to next node.

```python
from dynamiq.nodes.node import OutputTransformer

output_transformer = OutputTransformer({
    "result": "$.output.content",
    "sources": "$.output.sources"
})
```

## Running Workflows

### Synchronous
```python
result = wf.run(input_data={"input": "query"})
```

### Asynchronous
```python
result = await wf.run(input_data={"input": "query"})
```

### Accessing Results
```python
# Access by node ID
agent_output = result.output["agent_1"]
content = agent_output.get("output", {}).get("content")

# Direct output for single-node workflows
content = result.output.get("content")
```

## Error Handling

### Node-Level Error Handling
```python
from dynamiq.nodes.node import ErrorHandling

error_handling = ErrorHandling(
    interval=2,          # Seconds before first retry
    max_attempts=3,      # Maximum retry attempts
    backoff_rate=2.0,    # Exponential backoff multiplier
    timeout=30           # Timeout in seconds
)

llm = OpenAI(
    connection=conn,
    model="gpt-4o",
    error_handling=error_handling
)
```

### Behavior on Error
```python
from dynamiq.nodes.types import Behavior

# For Map nodes
Behavior.RAISE   # Raise exception on failure
Behavior.RETURN  # Return partial results with error info
```

## Caching

```python
from dynamiq.nodes.node import CachingConfig

caching = CachingConfig(
    enabled=True,
    ttl=3600  # Cache TTL in seconds
)

llm = OpenAI(
    connection=conn,
    model="gpt-4o",
    caching_config=caching
)
```

## YAML Serialization

### Save to YAML
```python
wf.to_yaml_file("workflow.yaml")
```

### Load from YAML
```python
from dynamiq.serializers.loaders.yaml import WorkflowYAMLLoader

wf = Workflow.from_yaml_file("workflow.yaml")
```

## Conditional Nodes (Choice)

```python
from dynamiq.nodes.types import ChoiceCondition, ConditionOperator

choice = ChoiceNode(
    name="route",
    conditions=[
        ChoiceCondition(
            variable="$.classifier.output.category",
            operator=ConditionOperator.EQUALS,
            value="urgent"
        )
    ]
)
```

## Map Node (Parallel Processing)

```python
from dynamiq.nodes import MapNode

map_node = MapNode(
    name="parallel-embed",
    node=embedder,  # Node to execute for each item
    behavior=Behavior.RETURN  # On error behavior
)

# Input: {"input": [{"query": "text1"}, {"query": "text2"}, ...]}
```

## Parallel vs Sequential Execution

```python
# Parallel: No dependencies
wf.flow.add_nodes([agent1, agent2])  # Run in parallel

# Sequential: With dependencies
agent2.depends = [NodeDependency(agent1)]  # agent2 waits for agent1
```
