# Enterprise Email Agent Workspace

A production-grade, multi-agent AI workspace designed for corporate email automation. Powered by **Nexus AI Engine** (multi-model orchestration), **FastAPI**, **Microsoft SQL Server (MSSQL)**, **Microsoft Graph (Outlook)**, and an **Angular 19** executive dashboard with real-time **WebSocket telemetry**.

---

## 🌟 Key Capabilities & 5 Core Business Cases

| Case | Title | Description | Key Agent(s) |
| :--- | :--- | :--- | :--- |
| **Case 1** | **The Calendar Finder** | Detects meeting scheduling requests, extracts dates/times, connects to Outlook Calendar to check free/busy availability, and creates Staged Meeting Proposals. | `EntityExtractorAgent`, `OutlookCalendarClient` |
| **Case 2** | **The To-Do List Creator** | Identifies concrete deliverables, owners, deadlines, and urgency levels, saving them directly into Microsoft SQL Server `Tasks` table. | `TaskExtractorAgent` |
| **Case 3** | **The Multi-Task Router** | Flags mixed-intent emails (containing both a meeting and an action item) and executes concurrent branches via `asyncio.gather` with zero sequential latency. | `RouterAgent`, `Orchestrator` |
| **Case 4** | **The Smart Replier** | Synthesizes open calendar slots and tracked tasks into personalized email drafts with customizable corporate tones (`professional`, `friendly`, `concise`, `executive`). | `ReplyGeneratorAgent`, `OutlookMailClient` |
| **Case 5** | **The Double-Checker** | Evaluates incomplete or vague requests (e.g., "let's connect sometime"), pauses automated processing, and presents interactive multiple-choice options for clarification. | `SupervisorAgent` |

---

## 🏛️ System Architecture

```
                                      ┌────────────────────────────────┐
                                      │   Angular 19 Executive UI      │
                                      │  (Inbox, Tasks, Telemetry)     │
                                      └───────▲────────────────▲───────┘
                                              │ HTTP REST      │ WebSockets (/ws/stream)
                                      ┌───────▼────────────────┴───────┐
                                      │   FastAPI Gateway Microservice │
                                      │  (Enterprise Safety Guardrails)│
                                      └───────────────┬────────────────┘
                                                      │
                                    ┌─────────────────▼─────────────────┐
                                    │    Multi-Agent Orchestrator       │
                                    │   (Observe -> Think -> Act)       │
                                    └────┬──────┬──────┬──────┬─────┬───┘
                                         │      │      │      │     │
                 ┌───────────────────────┘      │      │      │     └────────────────────────┐
                 ▼                              ▼      ▼      ▼                              ▼
          [Reader Agent]                  [Router]  [Entity] [Task]                    [Supervisor]
       (Payload Normalizer)               (Intent)  (Slots)  (To-Do)                   (Completeness)
                 │                              │      │      │                              │
                 └───────────────┬──────────────┴──────┴──────┴──────────────────────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │    Reply Generator Agent      │
                 │   (Multi-Tone Context Replier)│
                 └───────────────┬───────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────┐
│  Microsoft SQL   │   │  Microsoft Graph │   │   Nexus Generative   │
│  Server (MSSQL)  │   │ (Outlook / MSAL) │   │ Engine (Multi-Model) │
└──────────────────┘   └──────────────────┘   └──────────────────────┘
```

---

## 📚 Project Documentation

- 📐 **[HLD.md](HLD.md)**: High-Level Design document covering system context, sequence diagrams, enterprise actors, and governance.
- 🔬 **[LLD.md](LLD.md)**: Low-Level Design document containing agent class diagrams, MSSQL ER schemas, API endpoint specifications, and Angular architecture.
- 📝 **[PROMPT.md](PROMPT.md)**: Prompt Engineering reference catalog with system prompts, output schemas, corporate tone guidelines, guardrail patterns, and heuristic fallbacks.
- 🎨 **[Poster.html](Poster.html)**: Interactive visual executive architecture poster & system infographic (open directly in browser or export as PDF).

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: v18.x or higher & npm
- **Database**: Microsoft SQL Server (MSSQL) with ODBC Driver 18
- **ODBC Driver**: ODBC Driver 18 for SQL Server installed on host

---

### 1. Backend Setup & Startup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** in `backend/.env`:
   ```env
   # Microsoft SQL Server (MSSQL)
   MSSQL_SERVER=LIN-5CD6268KRS
   MSSQL_DATABASE=EmailAgentWorkSpaceDb
   MSSQL_USER=sa
   MSSQL_PASSWORD=YourPasswordHere
   MSSQL_DRIVER=ODBC Driver 18 for SQL Server
   MSSQL_TRUST_CERT=yes

   # Nexus Generative Engine
   NEXUS_API_KEY=your_nexus_api_key
   NEXUS_BASE_URL=https://openai.generative.engine.capgemini.com/v1
   NEXUS_WS_URL=wss://ws.generative.engine.capgemini.com/

   # Multi-Model Orchestration
   MODEL_ROUTER=amazon.nova-micro-v1:0
   MODEL_EXTRACTOR=amazon.nova-micro-v1:0
   MODEL_REASONING=anthropic.claude-sonnet-5
   MODEL_DRAFTING=anthropic.claude-sonnet-5
   MODEL_FALLBACK=openai.gpt-4o

   # Ecosystem Connectors (Optional - Uses Mock Fallback if empty)
   USE_MOCK_OUTLOOK=true
   ```

5. **Start the FastAPI backend server**:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Redoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
   - **WebSocket Stream**: `ws://127.0.0.1:8000/ws/stream`

---

### 2. Frontend Setup & Startup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Run the Angular application**:
   ```bash
   npm start
   ```

4. **Access the application**:
   Open [http://localhost:4200](http://localhost:4200) in your browser.

---

## 🧪 Testing & Validation

### Automated Pytest Suite
Run unit tests, integration tests, and guardrail red-team attack simulations:
```bash
cd backend
python -m pytest tests/ -v
```

### Interactive REST Client (`backend/api-testing.http`)
Use VS Code REST Client or IntelliJ HTTP Client to execute end-to-end scenarios directly against the live backend:
1. **Health Check**: Root status & Nexus engine connectivity.
2. **Case 1**: Meeting scheduling email ingestion, slot query, and calendar confirmation.
3. **Case 2**: Task extraction and direct MSSQL table verification.
4. **Case 3**: Mixed-intent concurrent execution.
5. **Case 4**: Draft tone generation, human approval, and dispatch.
6. **Case 5**: Ambiguous email clarification pause and user resolution.
7. **Red-team**: Prompt injection mitigation verification.

---

## 🛡️ Enterprise Safety & Guardrails

The platform includes active security policies:
- **Prompt Injection Defense**: Evaluates input payloads against privilege escalation signatures (`ignore previous instructions`, `developer mode`, `drop table`), blocking malicious requests before they reach the LLM.
- **PII Redaction**: Automatically scrubs Social Security Numbers, credit card numbers, and exposed passwords from email bodies.
- **Leak Prevention**: Scans generated outputs to prevent leakage of internal credentials or API keys.

---

## 📁 Repository Structure

```
email-agent-workspace/
├── HLD.md                  # High-Level Design Document
├── LLD.md                  # Low-Level Design Document
├── PROMPT.md               # Prompt Engineering Reference & System Prompts
├── README.md               # Master Project Readme
├── backend/                # FastAPI Asynchronous Microservice
│   ├── app/                # Application source code
│   │   ├── adapters/       # LLM & Graph API connectors
│   │   ├── agents/         # Autonomous agents (Router, Extractor, Supervisor, etc.)
│   │   ├── api/            # REST API endpoints & routers
│   │   ├── core/           # Config, database, guardrails & telemetry
│   │   ├── db/             # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic validation schemas
│   │   └── main.py         # Application entry point & WebSocket handler
│   ├── api-testing.http    # Comprehensive REST client test suite
│   ├── requirements.txt    # Python dependencies
│   └── tests/              # Pytest test suite
├── deployment/             # Deployment configurations
└── frontend/               # Angular 19 Standalone Frontend
    ├── src/
    │   ├── app/
    │   │   ├── core/       # API & WebSocket client services
    │   │   ├── features/   # Inbox, AI analysis, Task board, Telemetry, Modals
    │   │   └── shared/     # Component interfaces, toast, models
    │   ├── index.html      # Shell HTML
    │   ├── main.ts         # Bootstrap entry point
    │   └── styles.css      # Design system & dark theme styles
    └── package.json        # NPM dependencies & scripts
```
# Command to run the backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Command to run the frontend
npm start
