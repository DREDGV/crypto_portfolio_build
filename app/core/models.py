from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    coin: str
    type: str  # trade_buy/trade_sell/transfer_in/transfer_out/fiat_deposit/fiat_withdrawal/income_.../expense_...
    quantity: float
    price: float
    ts_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    strategy: str  # long_term/swing/scalp/arbitrage/hedge/income_hold
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


class SourceMeta(SQLModel, table=True):
    """Персистентные настройки источников (название/порядок/скрыт)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    original_name: str = Field(index=True)
    custom_name: Optional[str] = Field(default=None)
    order_index: Optional[int] = Field(default=None, index=True)
    hidden: bool = Field(default=False, index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PriceAlert(SQLModel, table=True):
    """Алерты по ценам криптовалют."""
    id: Optional[int] = Field(default=None, primary_key=True)
    coin: str = Field(index=True)
    target_price: float
    alert_type: str = Field(index=True)  # "above", "below", "change_percent"
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    triggered_at: Optional[datetime] = None
    notes: Optional[str] = None


class PriceAlertIn(BaseModel):
    """Входящие данные для создания алерта."""
    coin: str
    target_price: float
    alert_type: str  # "above", "below", "change_percent"
    notes: Optional[str] = None