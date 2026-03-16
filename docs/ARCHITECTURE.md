# Architecture

## System Overview

GovDoc AI is a three-tier application: a React SPA frontend, a FastAPI async backend, and PostgreSQL for persistence. An LLM layer (Claude API) processes documents on demand with chunking support for large files.

## Data Flow

### Document Upload

```
User drops file → FileUpload component → Axios POST /api/documents/upload
                                              │
                                    ┌─────────▼──────────┐
                                    │  FastAPI Router     │
                                    │  (validate type/size)│
                                    └─────────┬──────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │  Document Service   │
                                    │  1. Save to disk    │
                                    │  2. Extract text    │
                                    │  3. Store in DB     │
                                    │  4. Log audit       │
                                    └─────────┬──────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │  PostgreSQL         │
                                    │  documents table    │
                                    │  audit_logs table   │
                                    └────────────────────┘
```

### Document Analysis

```
User clicks "Analyze" → Axios POST /api/documents/{id}/analyze
                              │
                    ┌─────────▼──────────┐
                    │  Document Service   │
                    │  Load text from DB  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────────────┐
                    │  LLM Service               │
                    │                             │
                    │  Text ≤ 80k chars?          │
                    │  ├─ YES → Direct analysis   │
                    │  └─ NO  → Chunk pipeline:   │
                    │     1. Split into 80k chunks│
                    │     2. Summarize each chunk  │
                    │     3. Combine summaries     │
                    │     4. Final analysis        │
                    └─────────┬──────────────────┘
                              │ Claude Sonnet 4
                    ┌─────────▼──────────┐
                    │  Parse JSON result  │
                    │  - classification   │
                    │  - summary          │
                    │  - entities[]       │
                    │  - compliance_flags[]│
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  PostgreSQL         │
                    │  extracted_metadata │
                    │  analysis_history   │
                    │  audit_logs         │
                    └────────────────────┘
```

## Database Schema

```
documents                    extracted_metadata           analysis_history
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ id (UUID PK)        │──┐  │ id (UUID PK)        │     │ id (UUID PK)        │
│ filename            │  │  │ document_id (FK)     │◀─┐  │ document_id (FK)     │◀─┐
│ original_filename   │  │  │ classification       │  │  │ analysis_type        │  │
│ content_type        │  ├──│                      │  │  │ input_tokens         │  │
│ file_size           │  │  │ summary              │  │  │ output_tokens        │  │
│ text_content        │  │  │ entities (JSON)      │  │  │ model_used           │  │
│ uploaded_by         │  │  │ compliance_flags(JSON)│  │  │ duration_ms          │  │
│ created_at          │  │  │ created_at           │  │  │ status (enum)        │  │
└─────────────────────┘  │  └─────────────────────┘  │  │ error_message        │  │
                         │                            │  │ created_at           │  │
                         │  audit_logs                │  └─────────────────────┘  │
                         │  ┌─────────────────────┐   │                           │
                         │  │ id (UUID PK)        │   │                           │
                         └──│ document_id (FK)     │◀──┴───────────────────────────┘
                            │ action              │
                            │ actor               │
                            │ details             │
                            │ created_at          │
                            └─────────────────────┘
```

### Table Purposes

- **documents** — Source file metadata and extracted text content. Cascade deletes to all related tables.
- **extracted_metadata** — AI analysis results. One-to-many with documents (each analysis creates a new record, latest is used for display).
- **analysis_history** — Token usage, model, duration, and status tracking per LLM call. Enables cost monitoring and performance analysis.
- **audit_logs** — Append-only log of all actions for compliance and debugging.

## AI Analysis Pipeline

### Prompt Engineering

The main analysis prompt asks Claude to return a JSON object with four fields:

1. **classification** — One of: policy, regulation, report, memo, legislation, executive_order, guidance, correspondence, other
2. **summary** — 3-5 sentence summary capturing the document's purpose, scope, and key provisions
3. **entities** — Array of `{type, value}` objects (organizations, dates, monetary amounts, legal references)
4. **compliance_flags** — Array of `{severity, description}` objects flagging regulatory requirements, deadlines, or obligations

### Chunking Strategy

For documents exceeding 80,000 characters:

```
Full Text (e.g., 200k chars)
    │
    ├── Chunk 1 (80k chars) → Claude → Summary 1
    ├── Chunk 2 (80k chars) → Claude → Summary 2
    └── Chunk 3 (40k chars) → Claude → Summary 3
                                          │
            Combined Summaries ◀──────────┘
                    │
              Claude (final) → Classification + Summary + Entities + Flags
```

The chunk summary prompt specifically preserves dates, organizations, entities, obligations, and compliance details to avoid information loss during compression.

### Retry and Error Handling

- LLM calls use `tenacity` with exponential backoff (3 attempts max)
- JSON parsing handles markdown-wrapped responses (```json ... ```)
- Failed analyses are recorded in `analysis_history` with error messages
- Audit logs capture both successful and failed operations

## Docker Architecture

```
docker-compose.yml
├── db (postgres:16-alpine)
│   ├── Port: 5432
│   ├── Volume: pgdata (persistent)
│   ├── Database: govdoc
│   └── Healthcheck: pg_isready
├── backend (Python 3.12-slim)
│   ├── Port: 8000
│   ├── Volume: uploads (/tmp/govdoc-uploads)
│   ├── Depends: db (healthy)
│   └── Server: uvicorn
└── frontend (Node 20 build → nginx:alpine)
    ├── Port: 3000
    ├── Depends: backend
    └── Nginx: reverse proxy /api/* → backend:8000
```

The nginx reverse proxy handles routing: static files from the React build are served directly, while `/api/*` requests are proxied to the FastAPI backend on port 8000.

## Authentication

Simple API key authentication via `X-API-Key` header. The key is configured through the `API_KEY` environment variable. All document endpoints require authentication; health check does not.

This is intentionally simple for a portfolio project. A production system would use OAuth 2.0 or JWT with proper token rotation.

## Design Decisions

**Async-first backend.** FastAPI with asyncpg and SQLAlchemy async sessions. LLM calls can take 10-30 seconds — async I/O prevents blocking other requests during analysis.

**File storage on disk, not in database.** Documents are stored as files in `/tmp/govdoc-uploads` with UUID-prefixed filenames. Only the extracted text goes into PostgreSQL. This keeps the database lean and avoids BLOB overhead.

**Entities as JSON text, not normalized tables.** Government documents produce diverse entity types that evolve over time. A JSON column provides schema flexibility without migrations when new entity types appear.

**Separate analysis history from metadata.** `extracted_metadata` holds the latest analysis result for display. `analysis_history` tracks every LLM call with token counts and timing for cost monitoring. This separation keeps the display path simple while enabling detailed analytics.
