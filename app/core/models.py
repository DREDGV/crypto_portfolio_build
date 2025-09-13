from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime, timezone

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    coin: str
    type: str  # buy/sell/exchange_in/exchange_out/deposit/withdrawal
    quantity: float
    price: float
    ts_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    strategy: str  # long/mid/short/scalp
    source: Optional[str] = None
    notes: Optional[str] = None

class TransactionIn(BaseModel):
    coin: str
    type: str
    quantity: float
    price: float
    strategy: str
    source: Optional[str] = None
    notes: Optional[str] = None
