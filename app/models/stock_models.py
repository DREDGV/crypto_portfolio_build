#!/usr/bin/env python3
"""Модели данных для акций"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class StockTransactionType(str, Enum):
    """Типы операций с акциями"""

    BUY = "buy"  # Покупка
    SELL = "sell"  # Продажа
    DIVIDEND = "dividend"  # Дивиденды
    SPLIT = "split"  # Сплит акций
    BONUS = "bonus"  # Бонусные акции


class StockTransactionIn(BaseModel):
    """Входящие данные для транзакции с акциями"""

    symbol: str = Field(..., description="Символ акции (AAPL, MSFT, etc.)")
    company_name: str = Field(..., description="Название компании")
    transaction_type: StockTransactionType = Field(..., description="Тип операции")
    quantity: Decimal = Field(..., gt=0, description="Количество акций")
    price_per_share: Decimal = Field(..., gt=0, description="Цена за акцию")
    total_amount: Optional[Decimal] = Field(
        None, description="Общая сумма (автоматически вычисляется)"
    )
    commission: Decimal = Field(default=Decimal("0"), ge=0, description="Комиссия")
    currency: str = Field(default="USD", description="Валюта")
    exchange: str = Field(default="NASDAQ", description="Биржа")
    date: datetime = Field(default_factory=datetime.now, description="Дата операции")
    notes: Optional[str] = Field(None, description="Заметки")

    @validator("symbol")
    def validate_symbol(cls, v):
        return v.upper().strip()

    @validator("company_name")
    def validate_company_name(cls, v):
        return v.strip()

    @validator("total_amount", always=True)
    def calculate_total_amount(cls, v, values):
        if v is None and "quantity" in values and "price_per_share" in values:
            return values["quantity"] * values["price_per_share"]
        return v


class StockTransaction(StockTransactionIn):
    """Модель транзакции с акциями в базе данных"""

    id: int = Field(..., description="ID транзакции")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class StockPosition(BaseModel):
    """Позиция по акции"""

    symbol: str
    company_name: str
    total_quantity: Decimal
    average_price: Decimal
    total_invested: Decimal
    current_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    unrealized_pnl_percent: Optional[Decimal] = None
    exchange: str = "NASDAQ"
    currency: str = "USD"
    last_updated: Optional[datetime] = None


class StockPrice(BaseModel):
    """Текущая цена акции"""

    symbol: str
    price: Decimal
    currency: str = "USD"
    exchange: str = "NASDAQ"
    change_24h: Optional[Decimal] = None
    change_percent_24h: Optional[Decimal] = None
    volume: Optional[int] = None
    market_cap: Optional[Decimal] = None
    last_updated: datetime = Field(default_factory=datetime.now)


class StockDividend(BaseModel):
    """Дивиденды по акции"""

    symbol: str
    amount_per_share: Decimal
    currency: str = "USD"
    ex_dividend_date: datetime
    payment_date: datetime
    record_date: datetime
    frequency: str = "quarterly"  # quarterly, annual, monthly


class StockNews(BaseModel):
    """Новости по акции"""

    symbol: str
    title: str
    summary: str
    url: str
    published_at: datetime
    source: str
    sentiment: Optional[str] = None  # positive, negative, neutral


class StockAnalysis(BaseModel):
    """Анализ акции"""

    symbol: str
    recommendation: str  # buy, hold, sell, strong_buy, strong_sell
    target_price: Optional[Decimal] = None
    current_price: Decimal
    upside_potential: Optional[Decimal] = None
    risk_level: str = "medium"  # low, medium, high
    analyst: str
    analysis_date: datetime = Field(default_factory=datetime.now)
    reasoning: Optional[str] = None
