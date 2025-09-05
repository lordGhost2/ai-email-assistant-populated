import pandas as pd
from .models import Email
from .db import engine, Session
from .utils import extract_emails, extract_phones, simple_sentiment, compute_priority, parse_datetime

def ingest_csv(path: str, session: Session):
    df = pd.read_csv(path)
    # Expect columns: Sender, Subject, Body, Date
    for _, row in df.iterrows():
        sender = row.get('sender') or row.get('From') or ''
        subject = row.get('subject') or ''
        body = row.get('body') or row.get('BodyText') or row.get('Message') or ''
        date = parse_datetime(row.get('sent_date') or row.get('Date') or row.get('Received') or '')
        emails = extract_emails(str(body) + ' ' + str(sender))
        phones = extract_phones(str(body))
        sentiment = simple_sentiment(subject + ' ' + body)
        priority = compute_priority(subject, body, sentiment)
        e = Email(
            sender=sender,
            subject=subject,
            body=body,
            received_at=date,
            extracted_emails=','.join(emails),
            extracted_phones=','.join([p[0] if isinstance(p, tuple) else p for p in phones]),
            sentiment=sentiment,
            priority=priority
        )
        session.add(e)
    session.commit()
