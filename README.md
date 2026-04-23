# Sovereign AGI (Version 2.0)

A production-grade, multi-provider, multi-runtime autonomous agentic system featuring mechanically rigorous safety and execution layers.

## Architecture

This project implements a highly structured, 10-persona agentic fleet built on a six-layer architecture designed for deterministic orchestration, strict safety boundaries, and robust error recovery.

### The Six Layers
1.  **L0 - User Interface:** Next.js Dashboard and Server-Sent Events (SSE) stream.
2.  **L1 - Orchestrator (Madara):** A DAG Engine managing task scheduling and routing based on structured metadata (not LLM hallucination).
3.  **L2 - Persona Agents:** 10 specialized sub-agents with unique prompts, LLM targets, and tool access.
4.  **L3 - Critic & Safety:** Schema validation, semantic security gates (Ichigo), diff auditing (Itachi), and rollback controllers.
5.  **L4 - Execution:** FastMCP server handling sandboxed file/shell operations.
6.  **L5 - Persistence:** SQLite (WAL) for state, ChromaDB for vector failure memory, and Redis for rate-limiting.

### Core Components (`/core`)
*   **`schemas.py`:** Strict Pydantic models (e.g., `AgentResult`, `HandoffPayload`) enforcing explicit JSON outputs from all agents.
*   **`db.py`:** SQLModel mappings for `DAGTask`, `Anchor`, `ExecutionSnapshot`, and `ExecutionLog` stored in SQLite (WAL).
*   **`memory.py`:** ChromaDB integration using `sentence-transformers` for deduplicating and preventing cyclical agent failures.
*   **`proxy.py`:** Redis-backed Token Bucket rate limiter that transparently handles multi-provider LLM failovers (Ollama, Anthropic, OpenAI).
*   **`dry_run.py`:** SHA-256 snapshot engine supporting base64 binary encoding for formal Two-Phase Commit rollbacks.
*   **`watchdog.py`:** Asynchronous execution daemon tracking TTLs and driving automatic retries.

### The Persona Fleet (`/agents`)
*   **Orchestration & Safety:** `Madara` (DAG Controller), `Itachi` (Sandbox Auditor), `Ichigo` (Tier 1 Firewall).
*   **Execution & Integration:** `Natsu` (MVP Executor), `Goku` (Optimizer), `Doraemon` (API Integrator), `Ben10` (MCP Compositor).
*   **Support & Heavy Lift:** `Naruto` (Self-Healer), `Rimuru` (Context Bridge), `Chhota Bheem` (Colab Dispatcher).

## Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Python 3.12+ (if running locally)
*   A running local instance of [Ollama](https://ollama.com/) (or configure endpoints in `.env`)

### Installation & Execution

The system is fully containerized. Start the multi-container stack (Orchestrator, FastAPI, Redis):

```bash
docker-compose up --build
```

Alternatively, to run the Python host directly:
```bash
pip install -r requirements.txt
python run.py
```

### FastMCP Sandbox
The execution environment enforces strict path isolation via `mcp_server.py`. Actuation limits are strictly bounded to the `./sandbox` and `./tmp` directories. Directory traversal attempts are proactively blocked.
