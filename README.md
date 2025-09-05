# AI-Powered Communication Assistant (Hackathon scaffold)

## Quick start (local)

1. Install Python 3.10+ and Node 18+.
2. Copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY` if available.
3. From project root, create a virtualenv and install backend requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

4. Run backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. In another terminal, run frontend (in `frontend`):

```bash
npm install
npm run dev
```

6. Use the `ingest-csv` endpoint to import sample data (server path):

```bash
curl -X POST "http://localhost:8000/ingest-csv" -H "Content-Type: application/json" -d '{"path":"/mnt/data/68b1acd44f393_Sample_Support_Emails_Dataset.csv"}'
```

7. Open frontend at `http://localhost:3000`.


## Notes
- This scaffold is intentionally minimal and focused on hackathon speed. Replace the mocked send logic with Gmail/Graph API for production. Add a proper vector DB + embeddings for a full RAG flow.
- For LLM usage, set `OPENAI_API_KEY` in the `.env`. The backend will attempt to call OpenAI if the key is present.
