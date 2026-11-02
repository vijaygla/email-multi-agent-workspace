# Enterprise Email Agent Workspace - Backend Service

A high-performance, real-time multi-agent backend service built with **FastAPI**, **Microsoft SQL Server (MSSQL)**, and **Nexus AI Engine** (OpenAI-compatible REST + WebSocket).

---

## 🛠️ Architecture & Tool Allocation

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Framework** | FastAPI + Uvicorn | High-throughput asynchronous REST & WebSocket API |
| **Database** | Microsoft SQL Server (MSSQL) | Relational persistence for Emails, Tasks, Proposals, Drafts, and Logs |
| **AI Brain & Intent Router** | Nexus AI Engine | Fast routing, extraction, reasoning, and drafting |
| **Real-time Streaming** | Native WebSockets (`/ws/stream`) | Live telemetry broadcasting agent steps (Observe -> Think -> Act) |
| **Ecosystem Connectors** | Microsoft Graph & MSAL | Outlook Mail & Calendar integration with automated mock fallback |
| **Security & Compliance** | Enterprise Guardrails | Prompt injection detection, PII redaction, and compliance filtering |

---

## 🎯 Supported Use Cases

### Case 1: Scheduling a Meeting from an Email (The Calendar Finder)
- **Workflow**: When an email arrives saying *"Let's meet tomorrow afternoon"*, the **Entity Extractor Agent** extracts dates, preferred time frames, and participants.
- **Calendar Integration**: Connects to the Outlook Calendar API (via Microsoft Graph / MSAL) to check free/busy status and identifies 2 to 3 optimal open slots.
- **Staging**:
  - **Stage 1**: Staged as a proposal draft for user review.
  - **Stage 2**: Automatically coordinated and confirmed on the calendar via `POST /api/scheduled-meetings/{id}/confirm`.

### Case 2: Extracting and Saving Tasks (The To-Do List Creator)
- **Workflow**: If an email states *"Send the budget deck by Friday"*, the **Task Extractor Agent** extracts structured action items:
  - `title`, `description`, `owner` (defaults to "Me" or designated assignee), `due_date`, and `urgency` (*low*, *medium*, *high*, *urgent*).
- **MSSQL Persistence**: Directly saved into the Microsoft SQL Server `Tasks` table so it is officially recorded on the to-do board.

### Case 3: Managing Mixed Intent Emails (The Multi-Task Router)
- **Workflow**: For complex emails containing both a meeting request and an action item, the **Router / Planner Agent** flags the message as `mixed_intent`.
- **Concurrent Split**: Dispatches concurrently via `asyncio.gather` to the Calendar Agent (to find open slots) and the Task Agent (to log to-do items) without blocking or sequential latency.

### Case 4: Drafting a Polished Response (The Smart Replier)
- **Workflow**: The **Reply Generator Agent** synthesizes the extracted meeting slots and logged task confirmations into a personalized, context-aware email draft.
- **Tone Profiles**: Supports customizable corporate tones: `professional`, `friendly`, `executive`, `concise`.
- **Review & Send**: Staged in MSSQL for user approval (`POST /api/drafts/{id}/approve`) and dispatch (`POST /api/drafts/{id}/send`).

### Case 5: Asking Clarifying Questions (The Double-Checker)
- **Workflow**: If an incoming email is vague or missing critical parameters (e.g., cross-timezone meeting with no time zone specified, vague date, or ambiguous assignment), the **Supervisor Agent** pauses the automated pipeline.
- **Interactive Choices**: Constructs a polite clarification email with 2 to 3 selectable options. Once the user replies via `POST /api/clarifications/{id}/reply`, the pause is resolved.

---

## ⚙️ Configuration & Environment

Environment variables are managed in `.env`:

```env
# Microsoft SQL Server (MSSQL)
MSSQL_SERVER=LIN-5CD6268KRS
MSSQL_DATABASE=EmailAgentWorkSpaceDb
MSSQL_USER=sa
MSSQL_PASSWORD=Capgemini@12345
MSSQL_DRIVER=ODBC Driver 18 for SQL Server
MSSQL_TRUST_CERT=yes

# Nexus AI Engine (OpenAI-compatible)
NEXUS_API_KEY=your_nexus_api_key
NEXUS_BASE_URL=https://openai.generative.engine.capgemini.com/v1
NEXUS_WS_URL=wss://ws.generative.engine.capgemini.com/

# Model Orchestration
MODEL_ROUTER=amazon.nova-micro-v1:0
MODEL_EXTRACTOR=amazon.nova-micro-v1:0
MODEL_REASONING=anthropic.claude-sonnet-5
MODEL_DRAFTING=anthropic.claude-sonnet-5
MODEL_FALLBACK=openai.gpt-4o
```

---

## 🚀 Running the Application

### 1. Start the FastAPI Development Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Swagger / OpenAPI Documentation
Open your browser at:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Real-time WebSocket Endpoint**: `ws://127.0.0.1:8000/ws/stream`

---

## 🧪 Testing

### Automated Pytest Suite
Run the test suite covering unit tests, integration tests, and red-team guardrails:
```bash
python -m pytest tests/ -v
```

### Interactive API Testing (`api-testing.http`)
Use VS Code REST Client or IntelliJ HTTP Client to execute requests against `api-testing.http`:
1. **Health Check & Root Status**
2. **Case 1**: Meeting scheduling email ingestion & processing
3. **Case 2**: Task extraction & MSSQL verification
4. **Case 3**: Mixed intent concurrent execution
5. **Case 4**: Draft composition, approval, and send
6. **Case 5**: Ambiguous email clarification pause & resolution
7. **Red-team**: Prompt injection detection and blocking
