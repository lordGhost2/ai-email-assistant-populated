from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Email(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender: str
    subject: str
    body: str
    received_at: datetime
    sender_name: Optional[str] = None
    extracted_emails: Optional[str] = None
    extracted_phones: Optional[str] = None
    sentiment: Optional[str] = None
    priority: Optional[str] = None  # 'Urgent' or 'Not urgent'
    metadata: Optional[str] = None
    draft: Optional[str] = None
    resolved: bool = False
