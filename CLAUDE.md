# CLAUDE.md – Dynamiq Project Guide

## Project Description

This repository builds agentic AI workflows using the entity["organization","Dynamiq","orchestration framework"] framework as a **git submodule**. Code that extends or configures the framework lives in the `docker/` folder, while the framework’s source remains untouched in `dynamiq/`.  All services run through Docker Compose and connect to a local Ollama instance for running OSS Llama‑family models.  The project is designed to be reproducible on any host that supports Docker and Python ≥ 3.11.

## Tech Stack

* **Languages / Runtimes**: Python 3.11, Bash
* **Frameworks & Libraries**: entity["organization","Dynamiq","ai workflow"], FastAPI (optional REST), Pydantic v2, Pytest, Coverage.py
* **Infrastructure**: entity["organization","Docker","container platform"] + Docker Compose, entity["organization","Git","version control"] Submodules, Ollama (local LLM server)
* **Vector DBs (optional)**: entity["organization","Pinecone","vector db"], entity["organization","Qdrant","vector db"]
* **Cloud Keys** (for fallback): entity["organization","OpenAI","api provider"], entity["organization","Anthropic","api provider"]

## 🧱 Code Structure & Modularity (path → purpose)

| Path                         | Purpose                                                   |
| ---------------------------- | --------------------------------------------------------- |
| `/docker/main.py`            | Entrypoint; builds and runs Dynamiq workflows             |
| `/docker/Dockerfile`         | Production image for the app layer                        |
| `/docker/docker-compose.yml` | Orchestration for app + extras (databases, test runners)  |
| `/dynamiq/`                  | **Git submodule** – upstream framework source (read‑only) |
| `/docs/dynamiq.txt`          | **Dynamiq Documentation** – comprehensive framework guide |
| `/reports/`                  | Auto‑generated coverage & test artifacts                  |
| `/tests/`                    | Pytest suites; mirrors app module layout                  |
| `/.env`                      | Runtime configuration (see **Environment Setup**)         |
| `/CLAUDE.md`                 | This guide                                                |

> **Modularity rules**
> • Never create a file longer than **500 lines** – split into helper modules.
> • Keep domain logic inside feature folders; avoid cross‑package imports except via interfaces.
> • When extending Dynamiq, subclass nodes or connections in `docker/` rather than editing the submodule.

## Commands

| Task                  | Command                                                                                        |
| --------------------- | ---------------------------------------------------------------------------------------------- |
| **Build image**       | `docker compose -f docker/docker-compose.yml build`                                            |
| **Run app**           | `docker compose -f docker/docker-compose.yml up dynamiq-app`                                   |
| **Watch logs**        | `docker compose logs -f dynamiq-app`                                                           |
| **Unit tests**        | `docker compose -f docker/docker-compose.yml run --rm dynamiq-app-test`                        |
| **Integration tests** | `docker compose -f docker/docker-compose.yml run --rm dynamiq-app-test-integration-with-creds` |
| **Update submodule**  | `git submodule update --remote --merge`                                                        |

## ✨ Style & Conventions

* **PEP 8** enforced with `ruff` & `black` (run `make lint`).
* **snake_case** for functions/variables; **PascalCase** for classes & Dynamiq nodes.
* Always use type hints + `pydantic` models for I/O schemas.
* Import order: stdlib → third‑party → dynamiq → local app.
* Write Google‑style docstrings for every public callable.

```python
def example(param1: str) -> str:
    """Brief summary.

    Args:
        param1 (str): input value.

    Returns:
        str: transformed value.
    """
    ...
```

## 🧪 Testing & Reliability

* Pytest is mandatory for every new feature (happy path, edge, failure).
* Tests live in `/tests`, mirroring the app layout.
* CI fails if coverage < 90 % (see `reports/coverage.xml`).
* Use Dynamiq’s `on_failure` hooks for retry/back‑off logic inside workflows.

## Environment Setup

| Variable            | Default                                | Description                                    |
| ------------------- | -------------------------------------- | ---------------------------------------------- |
| `OLLAMA_HOST`       | `http://host.docker.internal:11434/v1` | Container → host bridge for local Llama models |
| `OPENAI_API_KEY`    | —                                      | Cloud fallback (optional)                      |
| `ANTHROPIC_API_KEY` | —                                      | Cloud fallback (optional)                      |

1. Copy `.env.example` to `.env` and fill secrets.
2. `ollama pull llama3` on the host before first run.
3. Execute **Build image** command.

## Allowed / Forbidden Tools

* **Allowed**: Docker CLI, Dynamiq CLI (`dynamiq run …`), Ollama, Python 3.11 stdlib, `pytest`, `coverage`, `ruff`, `black`, `make`, `curl` for health checks.
* **Forbidden**: Editing `/dynamiq/` submodule directly, `sudo`, destructive `rm -rf` outside container, hard‑coding API keys in source.

## 📚 Documentation & Explainability

* **Primary Reference**: `docs/dynamiq.txt` – Comprehensive Dynamiq framework documentation (LLMs, Agents, RAG, Orchestrators, Tools, Memory).

* Update `README.md` on every public‑facing change.
* Comment non‑obvious code; add `# Reason:` notes for complex logic.
* All new workflows must include a Markdown diagram (`docs/`) generated with `mermaid`.

## 🧠 AI Behavior Rules

* **Never assume missing context – ask.**
* **Do not hallucinate libraries or functions**; use only verified PyPI packages.
* Confirm file paths before referencing them.
* Do not overwrite existing code unless review approves.

## RAG Guidelines (Quick Reference)

### Indexing

* Use specific converters (e.g., `PyPDFConverter`); retain hierarchy.
* Chunk 256–512 tokens; 10–20 % overlap for prose.
* Enrich metadata (`source`, `tags`, `date`).
* Batch writes (`batch_size`) for large ingestions.

### Retrieval

* Prefer **hybrid search** (vector + BM25).
* Start with `top_k = 5`; tune per workflow.
* Add a query‑rewriter node when user input is ambiguous.

### Evaluation

* Track **Faithfulness**, **Context Recall**, **Answer Correctness** via Dynamiq evaluation suite.

## Glossary

* **Dynamiq** – orchestration framework for building agentic AI workflows.
* **Ollama** – local host service providing OpenAI‑compatible LLM API for OSS models.
* **RAG** – Retrieval‑Augmented Generation; combines retrieval with generative models.
* **Workflow** – Dynamiq object encapsulating a DAG of nodes.
* **Node** – atomic operation in a workflow (LLM, retriever, tool, etc.).

## Tips

* Keep this guide up to date with architectural changes.
* If a single module nears 500 lines, refactor.
* Pin Dynamiq submodule to a tag after major upgrades for stability.
