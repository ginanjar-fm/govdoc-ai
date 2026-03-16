# API Reference

Base URL: `http://localhost:8000` (direct) or `http://localhost:3000/api` (via nginx proxy)

Interactive documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

## Authentication

All document endpoints require the `X-API-Key` header.

```bash
curl -H "X-API-Key: dev-api-key-change-me" http://localhost:8000/api/documents
```

The health check endpoint does not require authentication.

---

## Endpoints

### Health Check

```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Upload Document

```
POST /api/documents/upload
Content-Type: multipart/form-data
X-API-Key: {api_key}
```

**Request:** Multipart form with `file` field. Accepted types: `application/pdf`, `text/plain`. Max size: 10MB.

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "X-API-Key: dev-api-key-change-me" \
  -F "file=@document.pdf"
```

**Response (201):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "a1b2c3d4_document.pdf",
  "message": "Document uploaded successfully"
}
```

**Errors:**
- `400` — Invalid file type or file too large
- `401` — Invalid or missing API key

---

### Analyze Document

```
POST /api/documents/{document_id}/analyze
X-API-Key: {api_key}
```

Triggers AI analysis of an uploaded document. This may take 10-30 seconds depending on document size.

**Response (200):**
```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "classification": "regulation",
  "summary": "This document establishes new reporting requirements for federal agencies regarding cybersecurity incidents. It mandates quarterly reporting to CISA and sets minimum response time thresholds. The regulation applies to all executive branch agencies effective Q3 2026.",
  "entities": [
    { "type": "organization", "value": "CISA" },
    { "type": "organization", "value": "Executive Branch Agencies" },
    { "type": "date", "value": "Q3 2026" },
    { "type": "requirement", "value": "Quarterly cybersecurity incident reporting" }
  ],
  "compliance_flags": [
    {
      "severity": "high",
      "description": "Mandatory quarterly reporting deadline — agencies must submit by the 15th of each quarter"
    },
    {
      "severity": "medium",
      "description": "New data classification requirements for incident reports — may require updated handling procedures"
    }
  ]
}
```

**Errors:**
- `404` — Document not found
- `401` — Invalid or missing API key
- `500` — LLM analysis failed (recorded in analysis_history)

---

### List Documents

```
GET /api/documents?search={query}&skip={offset}&limit={count}
X-API-Key: {api_key}
```

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| search | string | — | Filter by filename (partial match) |
| skip | integer | 0 | Pagination offset |
| limit | integer | 20 | Results per page (max 100) |

**Response (200):**
```json
{
  "documents": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "filename": "a1b2c3d4_document.pdf",
      "original_filename": "document.pdf",
      "content_type": "application/pdf",
      "file_size": 245760,
      "uploaded_by": "api_user",
      "created_at": "2026-03-16T08:00:00.000Z",
      "metadata_records": [
        {
          "classification": "regulation",
          "summary": "This document establishes...",
          "entities": "[...]",
          "compliance_flags": "[...]",
          "created_at": "2026-03-16T08:01:00.000Z"
        }
      ]
    }
  ],
  "count": 1
}
```

---

### Get Document

```
GET /api/documents/{document_id}
X-API-Key: {api_key}
```

Returns a single document with its latest analysis metadata.

**Response (200):** Same shape as individual items in the list response.

**Errors:**
- `404` — Document not found
- `401` — Invalid or missing API key

---

### Get Document Text

```
GET /api/documents/{document_id}/text
X-API-Key: {api_key}
```

Returns the extracted text content of a document.

**Response (200):**
```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "text_content": "SECTION 1. PURPOSE\n\nThis regulation establishes..."
}
```

---

## Data Types

### Document

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| filename | string | Stored filename (UUID-prefixed) |
| original_filename | string | User-provided filename |
| content_type | string | MIME type (`application/pdf` or `text/plain`) |
| file_size | integer | File size in bytes |
| text_content | string | Extracted text (available via `/text` endpoint) |
| uploaded_by | string | Actor who uploaded (default: `api_user`) |
| created_at | string (ISO 8601) | Upload timestamp |
| metadata_records | MetadataRecord[] | Analysis results (latest first) |

### MetadataRecord

| Field | Type | Description |
|---|---|---|
| classification | string | Document type (see Classification Types) |
| summary | string | 3-5 sentence AI-generated summary |
| entities | string (JSON) | Array of `{type, value}` objects |
| compliance_flags | string (JSON) | Array of `{severity, description}` objects |
| created_at | string (ISO 8601) | Analysis timestamp |

### Classification Types

| Type | Description |
|---|---|
| policy | Organizational or governmental policies |
| regulation | Regulatory rules and requirements |
| report | Reports, assessments, evaluations |
| memo | Internal memoranda |
| legislation | Laws, statutes, bills |
| executive_order | Presidential or executive directives |
| guidance | Advisory or instructional documents |
| correspondence | Letters, communications |
| other | Documents not matching above categories |

### Entity

| Field | Type | Description |
|---|---|---|
| type | string | Entity category (organization, date, monetary, legal_reference, requirement, etc.) |
| value | string | Extracted entity text |

### Compliance Flag

| Field | Type | Description |
|---|---|---|
| severity | string | `high`, `medium`, or `low` |
| description | string | Description of the compliance issue or obligation |
