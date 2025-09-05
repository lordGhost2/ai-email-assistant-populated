# 🚀 AI‑Powered Communication Assistant

> **Hackathon-ready** demo for automating support email triage, prioritization and empathetic reply generation — built to impress interviewers with clarity, impact, and production-ready thinking.

---

[![Project: AI Email Assistant](https://img.shields.io/badge/project-AI--Email--Assistant-blue)](#)
[![Status](https://img.shields.io/badge/status-demo%20ready-green)](#)
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20SQLite-yellow)](#)
![Made with ❤️](https://img.shields.io/badge/made_with-%E2%9D%A4-red)

---

## TL;DR — What this does
- Automatically **fetches support emails**, **filters** them, **extracts** contact & intent, **scores urgency**, and **drafts empathetic replies** using an LLM + RAG-ready pipeline.  
- Comes with a **clean dashboard** (React) to review, edit, and send replies (send is simulated in the scaffold).  
- Designed for a 4-day hackathon: minimal infra, high-impact demo, and clear extension path to production.

---

## Why this will impress interviewers 🎯
- **End-to-end thinking**: from ingestion → extraction → priority queue → LLM-driven responses → UI and analytics.  
- **Practical RAG design**: built so factual KBs can be incorporated (FAISS / Pinecone) to avoid hallucinations.  
- **Production-aware**: includes OAuth integration notes, background-worker roadmap (Redis/Celery), and security considerations.  
- **Demo-first**: local SQLite + CSV ingestion allows a reliable offline demo without cloud credentials.

---

## Features (at-a-glance)
- 🔎 **Email filtering** by subject keywords (`support`, `help`, `request`, `query`)  
- 🧾 **Extraction**: sender, alt emails, phone numbers, order IDs (regex + NER plug-in ready)  
- ❤️ **Empathy-aware replies**: negative sentiment triggers empathetic opening lines  
- ⚡ **Priority queue**: urgent items bubble to the top for immediate action  
- 🧠 **RAG-ready**: includes small KB and instructions to add vector DB + embeddings  
- 📊 **Dashboard analytics**: last-24h counts, sentiment breakdown, resolved vs pending  
- ⚙️ **Extensible**: switch fallback replies to OpenAI with `OPENAI_API_KEY`

---

## Quick demo commands (run locally)
```bash
# Backend (virtualenv)
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
# open http://localhost:3000

# Ingest demo CSV (server-accessible path)
curl -X POST "http://localhost:8000/ingest-csv" -H "Content-Type: application/json" -d '{"path":"/mnt/data/68b1acd44f393_Sample_Support_Emails_Dataset.csv"}'
```

---

## Interviewer Talking Points (short, copy-paste)
- **Design choice**: used SQLite + SQLModel for speed and reproducibility; easy to swap to Postgres.  
- **Safety**: fallback templates when LLM unavailable; KB retrieval reduces hallucinations.  
- **Scalability plan**: move vector index to Pinecone / Qdrant, and email processing to worker queues (Redis + Celery).  
- **Privacy**: redact PII before sending to third-party APIs; store secrets in vaults, rotate keys regularly.

---

## Architecture (simple diagram)
```
[ Gmail / IMAP / CSV ] --> [ Ingest Service (FastAPI) ] --> [ Preprocess: extract, sentiment, priority ]
                                              |
                                              v
                                    [ SQLite / Emails table ]
                                              |
                     +------------------------+------------------------+
                     |                         |                        |
                     v                         v                        v
          [ RAG Retriever (FAISS) ]   [ LLM Draft Generator ]   [ Dashboard (React) ]
```

---

## Core implementation notes
- **Draft generation**: `POST /generate-draft/{id}` builds a prompt with optional KB context and calls the LLM. If `OPENAI_API_KEY` missing, the app uses a deterministic fallback template (good for offline demos).  
- **Priority detection**: rule-based scoring using urgent keyword set + negative sentiment. Easy to replace with an ML classifier if labeled data available.  
- **RAG**: add document chunking + embeddings then query top-k chunks and add to prompt's `CONTEXT` section.

---

## What I implemented for the hackathon demo (list)
- Full project scaffold: backend (FastAPI), frontend (React/Vite), Dockerfiles, docker-compose.  
- CSV ingestion script + DB seeder.  
- Extraction (emails & phones), simple sentiment heuristics, priority scoring.  
- Draft generation (LLM call if key provided; deterministic fallback otherwise).  
- Populated demo DB and packaged downloadable zip with demo data.

---

## Suggested metrics to show during interview
- Filtering accuracy (precision/recall) on a labeled subset.  
- Priority detection F1 on test set.  
- Average response generation latency (with and without RAG).  
- Demo KPI: time-to-first-reply reduction (simulated).

---

## Roadmap (next 30–90 days)
1. Integrate OpenAI (production prompts + safety guardrails).  
2. Add vector DB (Pinecone/FAISS) and LangChain for RAG with provenance.  
3. Real email integration (Gmail/Outlook OAuth + per-user refresh tokens).  
4. Background workers for scale (Redis, Celery) and real sending with retry logic.  
5. Add user authentication and role-based access + audit logs.

---

## Appendix — Useful snippets & prompts
**Empathetic prompt skeleton**
```
SYSTEM: You are a professional customer support agent. Be empathetic and concise.
CONTEXT: {top_k_kb_chunks}
EMAIL: {email_body}
TASK: Acknowledge, summarize the issue, propose 2 clear steps, provide a timeline if escalation needed.
```

**Urgency scoring snippet (pseudo)**
```python
urgent_keywords = ["immediately","urgent","asap","cannot access","payment failed","outage"]
score = sum(k in text for k in urgent_keywords)
priority = "Urgent" if score >= 2 else "Not urgent"
```

---

## Contact & attribution
- Author: *Your name here* — replace in repo for credit.  
- Repo / Demo: contains `backend/` + `frontend/` + `docker-compose.yml`.  
- License: MIT (suggest adding LICENSE file).

---

If you want, I can now:
1. **Insert this fancy README into the project root** and repackage the populated zip.  
2. **Generate a one-page, interview-friendly architecture PDF** (downloadable).  
3. **Write a 60–90 second scripted pitch** you can use to introduce the project during interviews or demo day.

Pick 1, 2, or 3 and I’ll do it right away.
