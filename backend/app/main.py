from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from .db import create_db_and_tables, engine
from .models import Email
from .email_ingest import ingest_csv
from .utils import simple_sentiment, compute_priority
import os
from dotenv import load_dotenv
import openai
from typing import List
from datetime import datetime

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

app = FastAPI(title="AI Email Assistant")

# CORS - allow frontend origin
origins = [os.getenv('FRONTEND_ORIGIN', 'http://localhost:3000')]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

@app.post('/ingest-csv')
def ingest(path: str = Body(..., embed=True)):
    """Ingest CSV from path on server (for demo)."""
    with Session(engine) as session:
        try:
            ingest_csv(path, session)
            return {"status": "ok"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get('/emails')
def list_emails(priority: str = None, limit: int = 100):
    with Session(engine) as session:
        q = select(Email).order_by(Email.priority.desc())
        if priority:
            q = select(Email).where(Email.priority == priority)
        res = session.exec(q).all()
        return res[:limit]

@app.get('/emails/{email_id}')
def get_email(email_id: int):
    with Session(engine) as session:
        e = session.get(Email, email_id)
        if not e:
            raise HTTPException(404, "Email not found")
        return e

@app.post('/generate-draft/{email_id}')
def generate_draft(email_id: int):
    with Session(engine) as session:
        e = session.get(Email, email_id)
        if not e:
            raise HTTPException(404, "Email not found")
        prompt = build_prompt(e.subject, e.body, e.sender, e.sentiment)
        draft = call_llm(prompt)
        e.draft = draft
        session.add(e)
        session.commit()
        session.refresh(e)
        return {"draft": draft}

@app.post('/send/{email_id}')
def send_email(email_id: int, override_body: str = Body(None)):
    # For demo we simulate send; in prod integrate with Gmail/SMTP/Graph API
    with Session(engine) as session:
        e = session.get(Email, email_id)
        if not e:
            raise HTTPException(404, "Email not found")
        body = override_body or e.draft or ''
        # record send - here, mark resolved
        e.resolved = True
        session.add(e)
        session.commit()
        return {"status": "sent", "to": e.sender, "body": body}

@app.get('/stats')
def stats():
    with Session(engine) as session:
        total = session.exec(select(Email)).all()
        resolved = [e for e in total if e.resolved]
        pending = [e for e in total if not e.resolved]
        by_priority = {"Urgent": len([e for e in total if e.priority=='Urgent']), "Not urgent": len([e for e in total if e.priority!='Urgent'])}
        by_sentiment = {"Positive": len([e for e in total if e.sentiment=='Positive']), "Neutral": len([e for e in total if e.sentiment=='Neutral']), "Negative": len([e for e in total if e.sentiment=='Negative'])}
        return {"total": len(total), "resolved": len(resolved), "pending": len(pending), "by_priority": by_priority, "by_sentiment": by_sentiment}


# --- helper functions (simple RAG substitute & LLM call)

def build_prompt(subject, body, sender, sentiment):
    # Load small KB for demo
    kb_path = os.path.join(os.path.dirname(__file__), 'kb', 'faq.md')
    kb_text = ''
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb_text = f.read()
    except Exception:
        kb_text = ''
    system = "You are a helpful, empathetic customer support agent. Keep replies professional and friendly."
    prompt = f"{system}\n\nKB:\n{kb_text}\n\nEMAIL SUBJECT:\n{subject}\n\nEMAIL BODY:\n{body}\n\nIf the email expresses frustration, start with an apology and acknowledgement. Provide a short, actionable reply (4-6 short paragraphs).\n"
    return prompt

def call_llm(prompt: str):
    # Use OpenAI if available, otherwise return a rule-based template
    if OPENAI_KEY:
        try:
            resp = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[{"role": "system", "content": "You are a helpful support agent."}, {"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
            return resp['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"[LLM failed: {e}]\n\nSuggested reply:\n" + fallback_reply(prompt)
    else:
        return fallback_reply(prompt)

def fallback_reply(prompt):
    # Simple extraction from prompt to build safe reply
    lines = prompt.splitlines()
    subj = ''
    body = ''
    for i,l in enumerate(lines):
        if l.startswith('EMAIL SUBJECT:'):
            subj = lines[i+1] if i+1 < len(lines) else ''
        if l.startswith('EMAIL BODY:'):
            body = lines[i+1] if i+1 < len(lines) else ''
    reply = []
    reply.append("Hi,")
    if any(w in (subj+body).lower() for w in ['cannot', "can't", 'unable', 'not working', 'error', 'down']):
        reply.append("I'm really sorry you're experiencing this — I understand how frustrating that must be.")
    reply.append("Thanks for reaching out. Here's what I suggest:")
    reply.append("1. Please try restarting the app and clearing the cache.")
    reply.append("2. If that doesn't help, reply with exact error messages or screenshots and we'll escalate.")
    reply.append("Best regards,\nSupport Team")
    return '\n\n'.join(reply)
