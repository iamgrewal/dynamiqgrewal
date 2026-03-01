# Dynamiq Workflow Project

Build agentic AI workflows using the [Dynamiq](https://github.com/Traitblitz/dynamiq) orchestration framework with local LLM support via Ollama.

## Features

- **Low-Code Workflow Builder**: Create AI workflows with Dynamiq's intuitive node-based system
- **Local LLM Support**: Run Llama 3, Mistral, Gemma, and other models locally via Ollama
- **RAG Capabilities**: Built-in support for document processing, embeddings, and vector stores
- **Multi-Agent Orchestration**: Linear, Adaptive, and Graph orchestrators for complex workflows
- **Docker-Based**: Fully containerized for reproducible deployments

## Project Structure

```
dynamiqgrewal/
├── docker/
│   ├── main.py              # Application entrypoint
│   ├── Dockerfile           # Multi-stage Docker build
│   ├── docker-compose.yml   # Service definitions
│   └── requirements.txt     # Additional dependencies (optional)
├── dynamiq/                 # Git submodule - Dynamiq framework
├── docs/
│   └── dynamiq.txt          # Comprehensive Dynamiq documentation
├── tests/                   # Test suites
├── reports/                 # Coverage and test artifacts
├── .claude/skills/
│   └── dynamiq.skill        # AI assistant skill package
├── .env                     # Environment configuration
├── CLAUDE.md                # Project instructions
└── README.md                # This file
```

## Prerequisites

- **Docker** and **Docker Compose**
- **Ollama** installed and running on the host
- **Python 3.11+** (for local development)

### Setup Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull a model
ollama pull llama3
```

## Quick Start

### 1. Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (optional for cloud fallbacks)
```

### 2. Build and Run

```bash
# Build the Docker image
docker compose -f docker/docker-compose.yml build

# Run the application
docker compose -f docker/docker-compose.yml up dynamiq-app

# Watch logs
docker compose -f docker/docker-compose.yml logs -f dynamiq-app
```

### 3. Expected Output

```
--- Starting Dynamiq + Ollama Agent ---
AI Response: Quantum computing uses quantum bits (qubits) that can exist in multiple states simultaneously, enabling parallel processing of complex calculations.
```

## Docker Services

| Service | Description |
|---------|-------------|
| `dynamiq-app` | Main application container |
| `dynamiq-app-test` | Unit test runner |
| `dynamiq-app-test-cov` | Coverage test runner |
| `dynamiq-app-test-cov-exclude-integration-with-creds` | Coverage excluding integration tests |
| `dynamiq-app-test-integration-with-creds` | Integration tests with credentials |

## Commands

| Task | Command |
|------|---------|
| **Build image** | `docker compose -f docker/docker-compose.yml build` |
| **Run app** | `docker compose -f docker/docker-compose.yml up dynamiq-app` |
| **Watch logs** | `docker compose logs -f dynamiq-app` |
| **Unit tests** | `docker compose -f docker/docker-compose.yml run --rm dynamiq-app-test` |
| **Coverage tests** | `docker compose -f docker/docker-compose.yml run --rm dynamiq-app-test-cov` |
| **Integration tests** | `docker compose -f docker/docker-compose.yml run --rm dynamiq-app-test-integration-with-creds` |
| **Update submodule** | `git submodule update --remote --merge` |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://host.docker.internal:11434/v1` | Ollama API endpoint |
| `OLLAMA_API_KEY` | `ollama` | Ollama API key (any non-empty string for local) |
| `OLLAMA_MODEL` | `gpt-oss:120b-cloud` | Ollama model to use |
| `OPENAI_API_KEY` | - | OpenAI API key (optional fallback) |
| `ANTHROPIC_API_KEY` | - | Anthropic API key (optional fallback) |

## Architecture

### Dockerfile (Multi-Stage Build)

```
runtime (base)
├── Python 3.13.10-slim
├── Poetry 1.8.3
├── System packages (git, curl, make, build-essential)
└── Dynamiq dependencies (from pyproject.toml)

develop (final)
├── Copies dynamiq library from submodule
├── Copies application code (main.py)
└── Sets PYTHONPATH for imports
```

### docker-compose.yml

- Uses `extra_hosts` to enable `host.docker.internal` for Ollama connectivity
- Mounts volumes for hot-reloading during development
- Supports multiple test configurations

### main.py

The entrypoint demonstrates:
1. **Ollama Connection**: Uses OpenAI-compatible API
2. **LLM Node**: Configured for local Llama 3 model
3. **Workflow**: Simple single-node workflow
4. **Query Execution**: Synchronous execution with result extraction

## Extending the Project

### Add Custom Workflows

Edit `docker/main.py` or create new modules in `docker/`:

```python
from dynamiq import Workflow
from dynamiq.nodes.agents import Agent
from dynamiq.nodes.tools import Python

# Create an agent with tools
agent = Agent(
    name="coding-assistant",
    llm=llm,
    tools=[Python()],
    role="Expert Python developer",
    max_loops=10
)

# Build workflow
wf = Workflow()
wf.flow.add_nodes(agent)
```

### Add Vector Store (RAG)

Uncomment in `docker/requirements.txt`:
```
pinecone-client
```

Then rebuild the image.

### Add New LLM Providers

```python
from dynamiq.nodes.llms import Anthropic
from dynamiq.connections import Anthropic as AnthropicConnection

anthropic_llm = Anthropic(
    connection=AnthropicConnection(api_key=os.getenv("ANTHROPIC_API_KEY")),
    model="claude-3-5-sonnet-20241022"
)
```

## Documentation

- **[docs/dynamiq.txt](docs/dynamiq.txt)**: Comprehensive Dynamiq framework documentation
- **[CLAUDE.md](CLAUDE.md)**: Project-specific instructions and conventions
- **[.claude/skills/dynamiq.skill](.claude/skills/dynamiq.skill)**: AI assistant skill package

## Troubleshooting

### Ollama Connection Issues

```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check from inside container
docker compose -f docker/docker-compose.yml exec dynamiq-app curl http://host.docker.internal:11434/api/tags
```

### Model Not Found

```bash
# Pull the model
ollama pull llama3

# List available models
ollama list
```

### Import Errors

```bash
# Rebuild the image
docker compose -f docker/docker-compose.yml build --no-cache
```

## License

See [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
