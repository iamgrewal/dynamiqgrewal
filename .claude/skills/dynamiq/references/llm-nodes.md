# LLM Nodes Reference

## Supported Providers

| Provider | Models | Connection Class |
|----------|--------|------------------|
| OpenAI | GPT-4o, GPT-4o-mini | `OpenAI` |
| Anthropic | Claude 3.5 Sonnet, Claude 3.5 Haiku | `Anthropic` |
| Cohere | Command R+, Command R | `Cohere` |
| Gemini | Gemini Pro 1.5, Gemini Flash 1.5 | `Gemini` |
| AWS Bedrock | Various proprietary models | `Bedrock` |
| Groq | Llama 3.1, Llama 3.2 | `Groq` |
| Mistral | Mistral Large, Small, Embed | `Mistral` |
| Together AI | Llama, Gemma, Mistral models | `TogetherAI` |
| Hugging Face | Open-source models | `HuggingFace` |
| IBM watsonx | Granite | `WatsonX` |
| Azure AI | OpenAI models | `AzureOpenAI` |
| Replicate | Open-source models | `Replicate` |
| SambaNova | Llama family | `SambaNova` |
| Cerebras | Open-source models | `Cerebras` |
| DeepInfra | Open-source models | `DeepInfra` |
| xAI | Grok-3 | `xAI` |
| Perplexity | Sonar | `Perplexity` |
| **Ollama** | Llama 3, Mistral, Gemma, etc. | `OpenAI` (compatible) |
| Custom | Custom/OpenAI-compatible | `Custom` |

## Configuration

### Basic LLM Setup

```python
from dynamiq.nodes.llms import OpenAI
from dynamiq.connections import OpenAI as OpenAIConnection
from dynamiq.prompts import Prompt, Message

llm = OpenAI(
    id="openai",                    # Unique identifier
    connection=OpenAIConnection(
        api_key="OPENAI_API_KEY"
    ),
    model="gpt-4o",                 # Model name
    temperature=0.3,                # Randomness (0-1)
    max_tokens=1000,                # Max output length
    prompt=Prompt(messages=[
        Message(content="Your prompt with {{ variable }}", role="user")
    ])
)
```

### Core Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | str | Model identifier (supports free-text with auto-suggestions) |
| `temperature` | float | Output randomness (0=deterministic, 1=creative) |
| `max_tokens` | int | Maximum tokens in response |
| `streaming` | bool | Enable token-by-token streaming |

### Prompt Configuration

```python
# Inline prompt with Jinja2 templating
prompt = Prompt(messages=[
    Message(content="Translate to English: {{ text }}", role="user")
])

# System + User messages
prompt = Prompt(messages=[
    Message(content="You are a helpful assistant.", role="system"),
    Message(content="Answer: {{ question }}", role="user")
])
```

### Running LLM Nodes

```python
# Synchronous
result = llm.run(input_data={"text": "Hola Mundo!"})
print(result.output)

# Asynchronous
result = await llm.run(input_data={"text": "Hola Mundo!"})
```

## Inference Modes

| Mode | Description |
|------|-------------|
| `DEFAULT` | Standard text-based response generation |
| `STRUCTURED_OUTPUT` | JSON-formatted structured outputs |
| `FUNCTION_CALLING` | For tool-enabled agents |
| `XML` | XML-formatted outputs (recommended for agents) |

## Error Handling

Configure retry behavior in node settings:

```python
from dynamiq.nodes.node import ErrorHandling

error_handling = ErrorHandling(
    interval=2,           # Seconds before first retry
    max_attempts=3,       # Maximum retry attempts
    backoff_rate=2.0,     # Multiplier for retry interval
    timeout=30            # Timeout in seconds
)
```

## Custom LLM Integration

For self-hosted or OpenAI-compatible models:

```python
from dynamiq.nodes.llms import CustomLLM
from dynamiq.connections import CustomLLM as CustomLLMConnection

custom_llm = CustomLLM(
    connection=CustomLLMConnection(
        url="http://your-server:8000/v1",
        api_key="optional-key"
    ),
    model="your-model-name"
)
```

## Ollama Integration (Local LLMs)

Ollama provides OpenAI-compatible API for running open-source models locally. Use the `OpenAI` connection class with Ollama's base URL.

### Prerequisites

```bash
# Install and run Ollama
ollama pull llama3
ollama serve  # Runs on http://localhost:11434
```

### Basic Ollama Setup

```python
from dynamiq import Workflow
from dynamiq.nodes.llms import OpenAI
from dynamiq.connections import OpenAI as OpenAIConnection
from dynamiq.prompts import Prompt, Message

# Ollama uses OpenAI-compatible API
ollama_connection = OpenAIConnection(
    api_key="ollama",  # Any non-empty string works
    base_url="http://localhost:11434/v1"  # Ollama's OpenAI-compatible endpoint
)

llm = OpenAI(
    id="ollama_node",
    connection=ollama_connection,
    model="llama3",  # Model pulled via 'ollama pull llama3'
    temperature=0.7,
    max_tokens=1000,
    prompt=Prompt(messages=[
        Message(content="You are a helpful assistant. {{ query }}", role="user")
    ])
)

# Run workflow
wf = Workflow()
wf.flow.add_nodes(llm)
result = wf.run(input_data={"query": "Explain quantum computing"})
print(result.output["ollama_node"]["output"]["content"])
```

### Docker Integration

When running Dynamiq in Docker with Ollama on the host:

```python
ollama_connection = OpenAIConnection(
    api_key="ollama",
    base_url="http://host.docker.internal:11434/v1"  # Docker -> host
)
```

### Popular Ollama Models

| Model | Pull Command | Description |
|-------|--------------|-------------|
| llama3 | `ollama pull llama3` | Meta Llama 3 (8B) |
| llama3:70b | `ollama pull llama3:70b` | Meta Llama 3 (70B) |
| mistral | `ollama pull mistral` | Mistral 7B |
| gemma | `ollama pull gemma` | Google Gemma |
| codellama | `ollama pull codellama` | Code-specialized Llama |
| phi3 | `ollama pull phi3` | Microsoft Phi-3 |

### Environment Variable

Use environment variables for configurable deployment:

```python
import os

ollama_connection = OpenAIConnection(
    api_key="ollama",
    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434/v1")
)
```
