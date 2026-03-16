# GovDoc AI

AI-powered government document processor. Upload PDFs or text files, and Claude AI classifies, summarizes, extracts entities, and flags compliance issues.

Built with FastAPI, React, PostgreSQL, and Anthropic Claude.

## Overview

GovDoc AI automates the analysis of government documents — policies, regulations, memos, legislation, and more. Upload a document, click analyze, and within seconds you get a structured classification, a concise summary, extracted entities (organizations, dates, legal references), and compliance flags with severity ratings. The system handles large documents by chunking text and chaining summaries before final analysis.

## Features

- **Document classification** — Categorizes into 9 government document types (policy, regulation, report, memo, legislation, executive order, guidance, correspondence, other)
- **AI summarization** — 3-5 sentence summaries capturing key points
- **Entity extraction** — Identifies organizations, dates, monetary amounts, legal references, and other structured data
- **Compliance flagging** — Detects compliance issues with severity levels (high/medium/low)
- **Large document support** — Chunks documents exceeding 80k characters, summarizes each chunk, then analyzes the combined summaries
- **PDF and text support** — Extracts text from PDFs (PyPDF2) and plain text files
- **Audit trail** — Logs every upload, analysis, and error with timestamps and actors
- **Token tracking** — Records input/output token usage per analysis for cost monitoring
- **API key authentication** — Header-based auth on all document endpoints

## Tech Stack

| Technology | Purpose | Version |
|---|---|---|
| FastAPI | Backend API framework | 0.115.6 |
| Python | Backend language | 3.12 |
| SQLAlchemy | Async ORM | 2.0.36 |
| PostgreSQL | Document and analysis storage | 16 |
| asyncpg | Async PostgreSQL driver | 0.30.0 |
| Anthropic Claude | AI document analysis | Sonnet 4 |
| PyPDF2 | PDF text extraction | 3.0.1 |
| React | Frontend UI | 18.3.1 |
| TypeScript | Frontend language | 5.7.2 |
| Tailwind CSS | Styling | 3.4.17 |
| react-dropzone | File upload UI | 14.3.5 |
| Axios | HTTP client | 1.7.9 |
| Docker + docker-compose | Container orchestration | — |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │  FileUpload   │  │ DocumentList  │  │ AnalysisPanel    │ │
│  │  (drag-drop)  │  │ (search/list) │  │ (results view)   │ │
│  └──────┬───────┘  └───────┬───────┘  └────────┬─────────┘ │
│         └──────────────────┼───────────────────┘           │
│                            │ Axios                          │
└────────────────────────────┼────────────────────────────────┘
                             │ /api/*
┌────────────────────────────┼────────────────────────────────┐
│                    FastAPI Backend                           │
│                            │                                │
│  ┌─────────────────────────▼──────────────────────────────┐ │
│  │              Document Router                            │ │
│  │  POST /upload  POST /analyze  GET /  GET /:id  GET /text│ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                  │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │            Document Service                             │ │
│  │  Upload → Extract Text → Store → Analyze → Save Results │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                  │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │              LLM Service                                │ │
│  │  Chunk Text → Summarize Chunks → Final Analysis         │ │
│  │                    │                                     │ │
│  │              Claude Sonnet 4                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                  │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │             PostgreSQL                                  │ │
│  │  documents | extracted_metadata | analysis_history      │ │
│  │  audit_logs                                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed data flow and design decisions.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ginanjar-fm/govdoc-ai.git
cd govdoc-ai

# Copy environment variables
cp .env.example .env

# Add your Anthropic API key
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# Start everything
docker-compose up --build
```

Open [http://localhost:3000](http://localhost:3000). Upload a PDF or text file, then click "Analyze with AI."

API docs (Swagger UI) available at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Reference

All document endpoints require the `X-API-Key` header (default: `dev-api-key-change-me`).

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check (no auth) |
| POST | `/api/documents/upload` | Upload a document (PDF or text, max 10MB) |
| POST | `/api/documents/{id}/analyze` | Analyze document with Claude AI |
| GET | `/api/documents` | List documents (with search and pagination) |
| GET | `/api/documents/{id}` | Get document with latest analysis |
| GET | `/api/documents/{id}/text` | Get extracted text content |

See [docs/API.md](docs/API.md) for full request/response schemas.

## How Document Analysis Works

The analysis pipeline processes documents in three stages:

**1. Text Extraction.** When a document is uploaded, text is extracted immediately — PyPDF2 reads all pages from PDFs, plain text files are decoded as UTF-8. The extracted text is stored alongside the document record in PostgreSQL.

**2. Chunking (for large documents).** If the extracted text exceeds 80,000 characters (~20k tokens), it's split into chunks. Each chunk is sent to Claude with a summarization prompt that preserves key details: dates, organizations, entities, obligations, and compliance information. The chunk summaries are then concatenated for the final analysis step. Documents under 80k characters skip this step entirely.

**3. AI Analysis.** The text (or combined chunk summaries) is sent to Claude Sonnet 4 with a structured prompt requesting four outputs: document classification (one of 9 government document types), a 3-5 sentence summary, extracted entities with types and values, and compliance flags with severity ratings. The LLM response is parsed as JSON, stored in the `extracted_metadata` table, and returned to the frontend. Token usage and analysis duration are tracked in `analysis_history` for cost monitoring.

**Retry logic.** LLM calls use exponential backoff with up to 3 attempts via the `tenacity` library, handling transient API errors gracefully.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `API_KEY` | Yes | API authentication key (change from default in production) |
| `DATABASE_URL` | Yes | Async PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `DATABASE_URL_SYNC` | Yes | Sync PostgreSQL connection string (for migrations) |
| `LLM_MODEL` | No | Claude model to use (default: `claude-sonnet-4-20250514`) |
| `MAX_FILE_SIZE_MB` | No | Maximum upload file size in MB (default: 10) |
| `VITE_API_KEY` | Yes | API key for frontend requests |

## Project Structure

```
govdoc-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, routers
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy async engine
│   │   ├── auth.py              # API key verification
│   │   ├── models/
│   │   │   └── document.py      # SQLAlchemy models (4 tables)
│   │   ├── routers/
│   │   │   ├── documents.py     # Document endpoints
│   │   │   └── health.py        # Health check
│   │   └── services/
│   │       ├── document_service.py  # Upload, analysis, query logic
│   │       └── llm_service.py       # Claude integration, chunking
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main app with state management
│   │   ├── components/
│   │   │   ├── FileUpload.tsx   # Drag-drop upload
│   │   │   ├── AnalysisPanel.tsx # Analysis results display
│   │   │   └── DocumentList.tsx # Document sidebar with search
│   │   ├── services/
│   │   │   └── api.ts           # Axios API client
│   │   └── types/
│   │       └── document.ts      # TypeScript interfaces
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml
└── docs/
    ├── ARCHITECTURE.md
    └── API.md
```

## Design Decisions

**Why FastAPI?** Native async support, automatic OpenAPI/Swagger generation, and Pydantic validation. For a document processing service with LLM calls, async I/O is critical — the backend can handle other requests while waiting for Claude's response.

**Why character-based chunking at 80k?** Claude's context window is large, but very long prompts increase latency and cost. 80k characters (~20k tokens) keeps each LLM call fast while preserving enough context for meaningful analysis. The summarize-then-analyze pattern maintains document coherence across chunks.

**Why store entities as JSON text?** Government documents produce varied entity types. A flexible JSON column avoids rigid schema changes when new entity types emerge. PostgreSQL's text column with JSON content is simple to query and evolve.

**Why audit logging?** Government document processing demands accountability. Every upload, analysis, and error is logged with actor and timestamp, supporting compliance requirements and debugging.

## Development

```bash
# Backend (requires PostgreSQL running)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Backend runs on port 8000, frontend on port 5173 (Vite dev server with API proxy).

## License

MIT
