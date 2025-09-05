# AI-Powered Communication Assistant

**A hackathon-ready end-to-end scaffold** that ingests support emails, filters and prioritizes them, extracts key information, generates context-aware draft replies (LLM/RAG ready), and displays everything on a simple web dashboard.

This README explains: what the project does, architecture, how to run it locally, how to configure LLMs and email credentials, how RAG would be added, how to demo and test, and next steps.

---

## Table of Contents
1. Project overview
2. Features
3. Architecture & data flow
4. Tech stack
5. Project structure
6. Quick start (run locally)
7. Environment variables and configuration
8. Backend: key endpoints and behavior
9. Frontend: pages & interactions
10. Data & database
11. LLM & RAG (how to plug in OpenAI or other models)
12. Gmail / Outlook ingestion (OAuth notes)
13. Testing & validation
14. Demo script (2–4 minute hackathon demo)
15. Troubleshooting & common issues
16. Next steps / roadmap
17. Security & privacy notes
18. Credits & license

---

## 1. Project overview
This project is an AI-powered assistant for handling support-style emails. It:
- Fetches / ingests emails (demo: CSV ingestion; production: Gmail/Outlook/IMAP).
- Filters support-related emails by subject keywords and saves them into a DB.
- Extracts contact details, sentiment, and other metadata.
- Computes urgency (priority) and places urgent items at the top of processing.
- Generates draft replies using either a production LLM (OpenAI) or a fallback template.
- (RAG-ready) can retrieve KB documents and include factual context in replies.
- Presents all data on a simple React dashboard where drafts can be reviewed, edited, and (simulated) sent.

This scaffold focuses on being hackathon-ready: minimal infra, reproducible, and easy to extend.

---

## 2. Features
- **Email retrieval (demo)**: CSV ingestion to simulate live inbox.
- **Filtering**: Subject-based quick filters for terms like `support|query|help|request`.
- **Extraction**: Regex-based extraction of emails and phone numbers.
- **Sentiment analysis**: Lightweight heuristic-based sentiment.
- **Priority detection**: Rule-based `Urgent` vs `Not urgent` ranking with a priority queue ordering.
- **Draft generation**: LLM-backed draft generation (OpenAI) or fallback templates if no API key.
- **Dashboard**: View emails, key metadata, generated draft (editable), simulated send.
- **Analytics**: Endpoint-driven stats for counts by sentiment and priority.

---

## 3. Architecture & data flow
1. **Ingest**: `CSV -> backend /ingest-csv` inserts rows into SQLite.
2. **Preprocess**: regex extraction (emails/phones), simple sentiment and priority heuristics applied.
3. **Store**: emails saved in SQLite (`emails.db`) with extracted metadata.
4. **Draft generation**: `/generate-draft/{id}` builds a prompt, optionally retrieves KB context, and calls the LLM (OpenAI) or uses fallback template.
5. **Dashboard**: React frontend (`/`) lists emails sorted by priority; clicking an email shows the body and draft. Users can edit and `Send` (simulated) via `/send/{id}`.

The repository includes a small demo KB (`backend/app/kb/faq.md`) that is used by the fallback prompt or can be used as the retrieval source for a RAG setup.

---

## 4. Tech stack
- Backend: **Python 3.11** + **FastAPI** + simple SQLite (via SQLModel in scaffold) for quick prototyping.
- Frontend: **React** (Vite) — minimal single-page UI to browse emails, generate drafts and simulate sending.
- LLM: **OpenAI** (optional) via `OPENAI_API_KEY` — fallback templates available if not set.
- Vector DB / RAG (optional): FAISS (local) / Chroma / Pinecone / Milvus — scaffold contains instructions to add FAISS-based retrieval.
- Dev: Docker / docker-compose files included for quick environment reproducibility.

---

## 5. Project structure
```
ai-email-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app & endpoints
│   │   ├── db.py              # DB engine & helpers
│   │   ├── models.py          # Email model
│   │   ├── email_ingest.py    # CSV ingestion script
│   │   ├── utils.py           # extraction, sentiment, priority helpers
│   │   └── kb/faq.md          # small demo knowledge base
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # main UI
│   │   └── index.jsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 6. Quick start (run locally)
> This section gets you running quickly for demo purposes.

### Prerequisites
- Python 3.10+ and Node 18+ (for frontend)
- Optional: Docker & docker-compose

### Steps (local, without Docker)
1. Copy `.env.example` to `backend/.env` and set any environment variables (see next section).
2. Install backend requirements:
```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .\.venv\Scripts\activate
pip install -r backend/requirements.txt
```
3. Start backend (from repo root):
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
4. Start frontend:
```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```
5. Ingest demo CSV (server path) into the backend DB:
```bash
curl -X POST "http://localhost:8000/ingest-csv" -H "Content-Type: application/json" -d '{"path":"/path/to/Sample_Support_Emails_Dataset.csv"}'
```
6. Open the frontend, select emails, click **Generate Draft**, edit if needed, and **Send (simulate)**.

### Steps (with Docker)
```bash
docker-compose up --build
# backend: http://localhost:8000
# frontend: http://localhost:3000
```

---

## 7. Environment variables and configuration
Edit `backend/.env` (copy `.env.example`) and set:
- `OPENAI_API_KEY` — optional but recommended for production-quality responses.
- `DATABASE_URL` — default `sqlite:///./emails.db` (works locally).
- `FRONTEND_ORIGIN` — used for CORS (default `http://localhost:3000`).

**Notes**: Keep API keys private. Do NOT commit `.env` to version control.

---

## 8. Backend: key endpoints and behavior
- `POST /ingest-csv` — body: `{ "path": "/absolute/path/to/csv" }` — ingest CSV rows into DB. The CSV shipped with the scaffold expects columns: `sender, subject, body, sent_date`.
- `GET /emails` — list emails (ordered by priority desc). Query params: `priority` (filter), `limit`.
- `GET /emails/{email_id}` — retrieve a single email with extracted metadata and draft.
- `POST /generate-draft/{email_id}` — build prompt (with optional KB context) and call the LLM (if available) or fallback template. Saves the draft to DB.
- `POST /send/{email_id}` — simulate send. In this scaffold it marks `resolved = true`. Replace with Gmail/SMTP/Graph API code for real sending.
- `GET /stats` — simple analytics counts by sentiment and priority.

**How draft generation works**
- The scaffold `build_prompt` function reads the demo KB and constructs a system + user prompt.
- `call_llm` will call OpenAI ChatCompletion if `OPENAI_API_KEY` is set. Otherwise a deterministic `fallback_reply` template is used.

---

## 9. Frontend: pages & interactions
- **Inbox list** — left panel: shows filtered support emails; columns: Sender, Subject, Priority, Sentiment.
- **Detail pane** — right panel: shows raw email, extracted metadata, KB context, AI-generated draft (editable).
- **Actions**: `Generate Draft` (calls backend), `Send (simulate)` (calls backend to mark resolved).

UX notes: The frontend is intentionally minimal — it's a quick UI for demos. You can extend it with pagination, better styling (Tailwind or Material UI), and charts.

---

## 10. Data & database
- Demo DB: `backend/app/emails.db` (SQLite). The schema contains the `emails` table with fields for extracted emails, phones, sentiment, priority, draft, and resolved.
- Example ingestion CSV: `Sample_Support_Emails_Dataset.csv` (20 rows in demo).
- Backup: create a copy of the `emails.db` file before experimental changes.

---

## 11. LLM & RAG (how to plug in OpenAI or other models)
### To enable OpenAI:
1. Add `OPENAI_API_KEY` to `backend/.env`.
2. Restart backend — `call_llm` uses `openai.ChatCompletion.create` with `gpt-4o-mini` in the scaffold (modify to `gpt-4` or other models as needed).

### To add RAG (recommended for factual answers):
1. Prepare your KB files (product docs, FAQ, SOPs) in a folder, e.g. `backend/app/kb/`.
2. Chunk the documents (e.g., 500-token chunks) and compute embeddings using OpenAI embeddings API or a local embedding model.
3. Store embeddings in a vector DB (FAISS for local or Pinecone/Chroma for managed).
4. In `generate-draft`, query the vector DB for top-k relevant chunks and include them in the prompt's `CONTEXT` section before calling the LLM.

**Fast prototype**: use `langchain` + `faiss` + `openai` embeddings. For production, use Pinecone or a hosted vector DB for persistence.

---

## 12. Gmail / Outlook ingestion (OAuth notes)
For a production-ready fetcher you should implement OAuth and the official APIs. Short notes:
- **Gmail API**: register an OAuth client in Google Cloud Console, enable Gmail API, obtain `client_id` and `client_secret`, implement OAuth consent and store refresh tokens to call Gmail `users.messages.list` and `users.messages.get` endpoints. See Google's Python quickstart.
- **Microsoft Graph (Outlook)**: register an app in Azure AD, request `Mail.Read` scopes, use MSAL for acquiring tokens, call `/me/messages`.

**Security**: store OAuth refresh tokens securely. For multi-tenant or production, use per-user credentials and a secure vault.

---

## 13. Testing & validation
- **Unit tests**: add tests for `utils.extract_emails`, `simple_sentiment`, `compute_priority` to ensure correct behavior.
- **Integration tests**: test `/ingest-csv` with a sample CSV and assert DB row counts and priority distribution.
- **Human eval**: evaluate 50–100 drafted replies for correctness, tone, and KB fidelity. Track average score.

---

## 14. Demo script (2–4 minute hackathon demo)
1. Start backend and frontend.
2. Show the CSV ingestion step (`POST /ingest-csv`) and confirm the DB count.
3. Open the dashboard. Show urgent emails at the top (highlight priority & sentiment). Click the top urgent email.
4. Click `Generate Draft` — show the AI draft (if using OpenAI, show it being generated; otherwise show fallback template).
5. Edit the draft (small change), click `Send (simulate)` and show the email marked as resolved.
6. Open `GET /stats` to show analytics (urgent vs not urgent, sentiment counts).
7. Conclude with next steps (Gmail OAuth, RAG improvements, multi-user auth).

---

## 15. Troubleshooting & common issues
- **Module import errors**: ensure you installed the backend `requirements.txt` into the active virtualenv.
- **OpenAI errors**: check `OPENAI_API_KEY`, model name compatibility and rate limits. If LLM calls fail, the scaffold falls back to the template reply.
- **Gmail OAuth**: missing or incorrect scopes -> consent screen fails. Check redirect URIs and OAuth client configuration.
- **CORS issues (frontend)**: ensure `FRONTEND_ORIGIN` in `.env` matches frontend origin (including port).

---

## 16. Next steps / roadmap
- Replace fallback template with real OpenAI / other LLM responses.
- Implement real email sending via Gmail / Microsoft Graph with proper error handling and rate limits.
- Add vector DB + LangChain RAG pipeline for KB retrieval and factual answers.
- Add authentication/authorization for multiple users and role-based access.
- Add background workers (Celery / RQ) and Redis priority queue for scalable processing.
- Add unit/integration tests and CI pipeline.

---

## 17. Security & privacy notes
- Never commit API keys or OAuth secrets to version control.
- For user emails, ensure encryption at rest and in transit in production (TLS, DB encryption, and minimal retention policies).
- Audit LLM outputs if you send customer PII to third-party APIs; consider redaction rules.

---

## 18. Credits & license
- Author: AI Assistant scaffold (you can add your name)
- Libraries: FastAPI, React, OpenAI (optional), FAISS/Chroma (optional)
- License: MIT (suggested) — add a LICENSE file if you intend to open-source the repo.

---

If you'd like, I can now:
- (A) Paste this README into the repo's root README.md file (so the zip contain the updated README). 
- (B) Generate a short 1–2 page non-AI-written architecture doc you can include in your deliverables.
- (C) Produce a short narrated demo script and a shot list for your 2–4 minute video.

Tell me which of A / B / C you want me to do next and I will perform it immediately.
