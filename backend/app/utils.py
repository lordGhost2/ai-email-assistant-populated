import re
from datetime import datetime

URGENT_KEYWORDS = [
    "immediately","urgent","asap","critical","cannot access","down","outage","right now","payment failed","unable to","broken","cannot login","can't login","not working"
]

POSITIVE_WORDS = ["thank", "great", "awesome", "happy", "good", "resolved", "thanks"]
NEGATIVE_WORDS = ["not", "can't", "cannot", "bad", "frustrat", "angry", "upset", "disappoint", "problem", "issue", "error"]

email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
phone_regex = re.compile(r"(\+\d{1,3}[- ]?)?\d{10}|\(\d{3}\)\s?\d{3}-\d{4}")

def extract_emails(text: str):
    return list(set(email_regex.findall(text or "")))

def extract_phones(text: str):
    return list(set(phone_regex.findall(text or "")))

def simple_sentiment(text: str):
    t = (text or "").lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    if neg > pos:
        return "Negative"
    if pos > neg:
        return "Positive"
    return "Neutral"

def compute_priority(subject: str, body: str, sentiment: str):
    text = ((subject or "") + " " + (body or "")).lower()
    kscore = sum(1 for k in URGENT_KEYWORDS if k in text)
    sscore = 1 if sentiment == "Negative" and kscore >= 1 else 0
    score = kscore*2 + sscore
    return "Urgent" if score >= 2 else "Not urgent"

def parse_datetime(s: str):
    # best-effort parse for common ISO formats
    try:
        return datetime.fromisoformat(s)
    except Exception:
        try:
            # fallback simple parse
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.utcnow()
