from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReceiptResponse(BaseModel):
    receipt_id: str
    status: str
    filename: str
    datetime: datetime
    company: Optional[str] = None
    date: Optional[str] = None
    total: Optional[float] = None
    address: Optional[str] = None
    confidence: Optional[float] = None
