# Memory Reference

## Overview

Memory enables agents to retain information across interactions, providing context and continuity for conversations.

## Memory Backends

| Backend | Best For | Persistence |
|---------|----------|-------------|
| InMemory | Development, testing | Session only |
| Pinecone | Production, semantic search | Persistent |
| Qdrant | Production, alternative to Pinecone | Persistent |
| PostgreSQL | Production, relational data | Persistent |
| SQLite | Local development | Persistent |
| DynamoDB | AWS environments | Persistent |
| Weaviate | Production, hybrid search | Persistent |

## Basic Usage

### InMemory Backend

```python
from dynamiq.memory import Memory
from dynamiq.memory.backends import InMemory

memory = Memory(backend=InMemory())

agent = Agent(
    name="ChatAgent",
    llm=llm,
    role="helpful assistant",
    memory=memory
)

# Memory persists across runs with same user_id/session_id
response1 = agent.run({
    "input": "My name is John",
    "user_id": "user123",
    "session_id": "session456"
})

response2 = agent.run({
    "input": "What's my name?",
    "user_id": "user123",
    "session_id": "session456"
})
# Agent remembers "John"
```

### Pinecone Backend

```python
from dynamiq.memory import Memory
from dynamiq.memory.backends import Pinecone as PineconeMemoryBackend
from dynamiq.connections import Pinecone as PineconeConnection

memory = Memory(
    backend=PineconeMemoryBackend(
        connection=PineconeConnection(api_key="PINECONE_API_KEY"),
        index_name="conversations",
        namespace="default",
        dimension=1536,
        create_if_not_exists=True
    )
)
```

### Qdrant Backend

```python
from dynamiq.memory.backends import Qdrant as QdrantMemoryBackend
from dynamiq.connections import Qdrant as QdrantConnection

memory = Memory(
    backend=QdrantMemoryBackend(
        connection=QdrantConnection(
            url="http://localhost:6333",
            api_key="optional"
        ),
        index_name="memory",
        dimension=1536
    )
)
```

## Memory Configuration

```python
memory = Memory(
    backend=InMemory(),
    message_limit=1000,  # Max messages to retrieve
    filters={"category": "support"}  # Default filters
)
```

## Memory Operations

### Adding Messages

```python
# Automatic via agent
agent.run({"input": "Hello", "user_id": "user1", "session_id": "session1"})

# Manual
memory.add(
    role="user",  # "user", "assistant", "system"
    content="Hello, how can I help?",
    metadata={"user_id": "user1", "session_id": "session1"}
)
```

### Retrieving Messages

```python
# Get all messages
messages = memory.get_all(limit=100)

# Get relevant messages (semantic search)
messages = memory.get_relevant(
    query="What did we discuss about pricing?",
    top_k=10
)

# Get with filters
messages = memory.get_all(
    filters={"session_id": "session1"},
    limit=50
)
```

### Clearing Memory

```python
# Clear all messages
memory.clear()

# Clear with filters
memory.clear(filters={"session_id": "old_session"})
```

## Retrieval Strategies

```python
from dynamiq.memory import MemoryRetrievalStrategy

# All messages
strategy = MemoryRetrievalStrategy.ALL

# Relevant messages (semantic search)
strategy = MemoryRetrievalStrategy.RELEVANT

# Both (all + relevant)
strategy = MemoryRetrievalStrategy.BOTH
```

## Format Types

```python
from dynamiq.memory import FormatType

format_type = FormatType.PLAIN      # Plain text
format_type = FormatType.MARKDOWN    # Markdown formatted
format_type = FormatType.XML         # XML formatted
```

## Memory with Embedders

For semantic search, configure an embedder:

```python
from dynamiq.memory import Memory
from dynamiq.memory.backends import Pinecone as PineconeMemoryBackend
from dynamiq.nodes.embedders import OpenAITextEmbedder

memory = Memory(
    backend=PineconeMemoryBackend(
        connection=PineconeConnection(api_key="KEY"),
        index_name="memory",
        dimension=1536
    )
)
```

## Best Practices

1. **Session Management**: Use `user_id` and `session_id` to segment conversations
2. **Memory Limits**: Set appropriate `message_limit` to prevent context overflow
3. **Filters**: Use filters to scope memory retrieval
4. **Cleanup**: Periodically clear old sessions to manage storage
5. **Embeddings**: Match embedder dimension to vector store configuration
