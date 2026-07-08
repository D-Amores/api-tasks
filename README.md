# API Tasks

A production-style task management REST API built as a hands-on learning project — from clean architecture and JWT auth to RAG, LangChain, LangGraph agents, and MCP. Built with **FastAPI**, **PostgreSQL + pgvector**, and **uv**.

This isn't a tutorial clone. It's a from-scratch build that layers in real-world concerns one at a time: versioned REST resources, SOLID-oriented service/repository layers, JWT authentication with per-user data isolation, background indexing, semantic search, structured LLM output, a memory-persistent LangGraph agent, and a standalone MCP server exposing the same business logic to any MCP-compatible client.

## Table of contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Running with Docker](#running-with-docker)
- [Running the AI layer](#running-the-ai-layer)
- [Tests](#tests)
- [API overview](#api-overview)
- [Design decisions worth knowing](#design-decisions-worth-knowing)
- [Known limitations & next steps](#known-limitations--next-steps)

## Features

**Core REST API**

- Versioned API (`/api/v1`) with a layered architecture: endpoint → service → repository → model
- JWT authentication (Argon2 password hashing via `pwdlib`, tokens via `PyJWT`)
- Projects and tasks as nested REST resources, fully isolated per authenticated user
- Centralized error handling via domain exceptions (`NotFoundError`, `ConflictError`) mapped to HTTP responses
- Request logging middleware and CORS configured for a React frontend
- Alembic migrations for every schema change

**AI layer**

- **RAG**: task embeddings (OpenAI `text-embedding-3-small`) stored in Postgres via `pgvector`, with an HNSW index for fast semantic search — scoped to the authenticated user
- Automatic background indexing on task create/update (no blocking the request)
- **LangChain**: natural language → structured tasks, using `with_structured_output` against a Pydantic schema
- **LangGraph**: a hand-built `StateGraph` (not the prebuilt `create_agent` shortcut) implementing the ReAct loop — model node, tool node, conditional routing, cycle back — with **persistent conversation memory** via `AsyncSqliteSaver`
- **MCP**: the agent's tools are exposed through a standalone MCP server (`app/mcp_server.py`), authenticated with its own JWT validation middleware, reusing the exact same services/repositories as the REST API. The chat endpoint acts as an MCP _client_, discovering and invoking tools over HTTP.

## Architecture

```
Client (Swagger / future React app)
        │
        ▼
┌────────────────────────────┐        ┌─────────────────────────────┐
│   FastAPI app (:8000)      │        │   MCP server (:8001)         │
│   /api/v1/...               │        │   app/mcp_server.py           │
│                              │        │                                │
│  endpoints ─ services ─┐    │  HTTP  │  AuthMiddleware (JWT)          │
│                          │    │◄──────►│  tools: list/create/complete/  │
│  /chat → LangGraph agent│    │  MCP   │  delete tasks, search_tasks    │
│  (StateGraph, checkpointer)  │        │        │                       │
└──────────────┬──────────┘   │        └────────┼───────────────────────┘
               │               │                  │
               ▼               │                  ▼
   agent_memory.db (SQLite)    │      ProjectService / TaskService / SearchService
   (conversation memory)       │      (same code the REST endpoints use)
                                │                  │
                                ▼                  ▼
                        PostgreSQL + pgvector (projects, tasks, users, task_embeddings)
```

Key idea: the MCP server doesn't duplicate business logic. Its tools call the same `ProjectService` / `TaskService` / `SearchService` the REST endpoints use — MCP is just a new, authenticated, standardized _entry point_ into logic that already existed.

## Tech stack

| Layer                 | Choice                                                    |
| --------------------- | --------------------------------------------------------- |
| Language / runtime    | Python 3.13, managed with `uv`                            |
| Web framework         | FastAPI                                                   |
| Database              | PostgreSQL 16 + `pgvector`                                |
| ORM / migrations      | SQLAlchemy 2.0 (typed `Mapped`) + Alembic                 |
| Auth                  | JWT (`PyJWT`), password hashing via `pwdlib` (Argon2)     |
| Testing               | pytest, SQLite in-memory (via dependency override)        |
| Embeddings            | OpenAI `text-embedding-3-small`                           |
| Structured extraction | LangChain + DeepSeek (`deepseek-v4-flash`)                |
| Agent orchestration   | LangGraph (`StateGraph`, `AsyncSqliteSaver` checkpointer) |
| Tool protocol         | MCP (`fastmcp`, `langchain-mcp-adapters`)                 |
| Containerization      | Docker + Docker Compose                                   |

## Project structure

```
app/
├── main.py                  # FastAPI app, middleware, exception handler
├── mcp_server.py             # Standalone MCP server (tools + JWT auth middleware)
├── core/                     # Settings, security (JWT/hashing), domain exceptions
├── db/                       # Engine, session, declarative base
├── models/                   # SQLAlchemy models (User, Project, Task, TaskEmbedding)
├── schemas/                  # Pydantic request/response contracts
├── repositories/              # Data access layer (one per aggregate)
├── services/                  # Business logic (project, task, user, search,
│                               embedding, task_extraction, agent_graph, indexing)
├── api/
│   ├── deps.py                # get_db, get_current_user, get_user_from_token
│   └── v1/
│       ├── router.py
│       └── endpoints/         # health, auth, projects, tasks, search, ai, chat
scripts/
└── index_tasks.py             # Manual/backfill embedding indexing script
migrations/                    # Alembic revisions
tests/                         # pytest suite (SQLite in-memory, JWT-isolated)
```

## Getting started

**Prerequisites**: [uv](https://docs.astral.sh/uv/), Docker.

```bash
git clone <your-repo-url>
cd api-tasks
cp .env.example .env   # fill in SECRET_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY
uv sync
docker compose up -d db
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

Generate a strong `SECRET_KEY`:

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

## Running with Docker

Runs the API and Postgres (with `pgvector`) together:

```bash
docker compose up --build
```

Migrations run automatically on container start. The API is available at `http://localhost:8000`.

> Note: inside Docker, the API reaches the database at host `db` (the Compose service name), not `localhost` — Compose overrides `DATABASE_URL` accordingly.

## Running the AI layer

The chat/agent feature requires **two processes** running simultaneously:

```bash
# Terminal 1 — MCP server (agent tools)
uv run python -m app.mcp_server

# Terminal 2 — main API
uv run fastapi dev app/main.py
```

To backfill embeddings for tasks created before indexing existed (or after a bulk import):

```bash
uv run python -m scripts.index_tasks
```

## Tests

```bash
uv run pytest -v
```

Tests run against an in-memory SQLite database via a FastAPI dependency override on `get_db` — no Docker or network calls required. The `task_embeddings` table (Postgres/pgvector-only) is excluded from the test schema, since embedding/search flows are exercised separately and aren't covered by this in-memory suite.

## API overview

| Method           | Path                                     | Description                                                     |
| ---------------- | ---------------------------------------- | --------------------------------------------------------------- |
| POST             | `/api/v1/auth/register`                  | Create a user                                                   |
| POST             | `/api/v1/auth/login`                     | Get a JWT access token                                          |
| GET              | `/api/v1/auth/me`                        | Current authenticated user                                      |
| GET/POST         | `/api/v1/projects`                       | List / create projects (own only)                               |
| GET/PATCH/DELETE | `/api/v1/projects/{id}`                  | Read / update / delete a project                                |
| GET/POST         | `/api/v1/projects/{id}/tasks`            | List / create tasks in a project                                |
| GET/PATCH/DELETE | `/api/v1/projects/{id}/tasks/{task_id}`  | Read / update / delete a task                                   |
| GET              | `/api/v1/search/tasks?q=...`             | Semantic search over the user's tasks                           |
| POST             | `/api/v1/ai/projects/{id}/extract-tasks` | Free text → structured tasks (LangChain)                        |
| POST             | `/api/v1/chat`                           | Conversational agent (LangGraph + MCP tools, persistent memory) |

All endpoints except `register`, `login`, and `health` require a `Bearer` JWT.

## Design decisions worth knowing

- **Model vs. schema separation**: SQLAlchemy models describe DB shape; Pydantic schemas describe API contracts. A `ProjectCreate` never accepts a client-supplied `id`; a `UserRead` never leaks a password hash.
- **Repository pattern**: all DB access for an aggregate goes through one repository. Services never write raw queries.
- **Services raise, endpoints don't check**: business rules raise domain exceptions (`NotFoundError`, `ConflictError`); a single `@app.exception_handler` translates them to HTTP responses, keeping endpoints thin.
- **User-scoped everything**: every repository query — including vector similarity search — filters by the authenticated user's ID. Requesting another user's resource returns `404`, not `403`, to avoid confirming it exists.
- **Embeddings live in their own table** (`task_embeddings`), not a column on `tasks`. This keeps the core schema portable (SQLite-testable) while the vector column stays Postgres/pgvector-only.
- **MCP tools never trust the LLM with `user_id`**: the authenticated user is resolved server-side (JWT middleware → context state), never passed as a tool argument the model could manipulate.
- **Hand-built LangGraph over `create_agent`**: the agent's `StateGraph` (model node, tool node, conditional edge, cycle) is written explicitly rather than using LangChain's prebuilt agent factory, trading a little convenience for full control over prompt injection, routing, and future extensions like human-in-the-loop confirmation.

## Known limitations & next steps

- Background embedding indexing uses FastAPI `BackgroundTasks` (simple, but not retried on crash) — a real queue (Celery/RQ/Arq) would be the production upgrade.
- No rate limiting on `/auth/login` yet.
- No refresh tokens — access tokens expire and require re-login.
- Agent conversation memory can "remember" past tool failures and avoid retrying even after a bug is fixed — worth revisiting with an explicit retry instruction or memory pruning.
- Planned: React frontend, human-in-the-loop confirmation for destructive agent actions, n8n automation workflows on top of the API.
