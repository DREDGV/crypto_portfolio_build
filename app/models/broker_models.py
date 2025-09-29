"""
Модели данных для работы с брокерами и акциями
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class BrokerBase(SQLModel):
    """Базовая модель брокера"""

    name: str = Field(max_length=100, description="Название брокера")
    api_url: Optional[str] = Field(default=None, description="URL API брокера")
    is_active: bool = Field(default=True, description="Активен ли брокер")
    description: Optional[str] = Field(default=None, description="Описание брокера")


class Broker(BrokerBase, table=True):
    """Модель брокера в базе данных"""

    __tablename__ = "brokers"

    id: str = Field(primary_key=True, description="Уникальный идентификатор брокера")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Связи
    instruments: List["StockInstrument"] = Relationship(back_populates="broker")
    transactions: List["StockTransaction"] = Relationship(back_populates="broker")


class BrokerIn(BaseModel):
    """Модель для создания брокера"""

    id: str
    name: str
    api_url: Optional[str] = None
    is_active: bool = True
    description: Optional[str] = None


class StockInstrumentBase(SQLModel):
    """Базовая модель инструмента"""

    ticker: str = Field(max_length=20, description="Тикер акции")
    name: str = Field(max_length=200, description="Полное название компании")
    sector: Optional[str] = Field(
        default=None, max_length=100, description="Сектор экономики"
    )
    lot_size: int = Field(default=1, description="Размер лота")
    currency: str = Field(default="RUB", max_length=3, description="Валюта торговли")
    is_active: bool = Field(default=True, description="Активен ли инструмент")


class StockInstrument(StockInstrumentBase, table=True):
    """Модель инструмента в базе данных"""

    __tablename__ = "stock_instruments"

    id: int = Field(primary_key=True)
    broker_id: str = Field(foreign_key="brokers.id", description="ID брокера")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Связи
    broker: Broker = Relationship(back_populates="instruments")
    transactions: List["StockTransaction"] = Relationship(back_populates="instrument")


class StockInstrumentIn(BaseModel):
    """Модель для создания инструмента"""

    ticker: str
    name: str
    broker_id: str
    sector: Optional[str] = None
    lot_size: int = 1
    currency: str = "RUB"
    is_active: bool = True


class StockTransactionBase(SQLModel):
    """Базовая модель транзакции с акциями"""

    ticker: str = Field(max_length=20, description="Тикер акции")
    quantity: int = Field(description="Количество акций")
    price: float = Field(description="Цена за акцию")
    commission: float = Field(default=0.0, description="Комиссия")
    transaction_type: str = Field(description="Тип операции: buy, sell, dividend")
    notes: Optional[str] = Field(default=None, description="Заметки")


class StockTransaction(StockTransactionBase, table=True):
    """Модель транзакции в базе данных"""

    __tablename__ = "stock_transactions"

    id: int = Field(primary_key=True)
    broker_id: str = Field(foreign_key="brokers.id", description="ID брокера")
    instrument_id: int = Field(
        foreign_key="stock_instruments.id", description="ID инструмента"
    )
    transaction_date: datetime = Field(
        default_factory=datetime.utcnow, description="Дата сделки"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Связи
    broker: Broker = Relationship(back_populates="transactions")
    instrument: StockInstrument = Relationship(back_populates="transactions")


class StockTransactionIn(BaseModel):
    """Модель для создания транзакции"""

    ticker: str
    broker_id: str
    quantity: int
    price: float
    commission: float = 0.0
    transaction_type: str
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None


class StockPosition(BaseModel):
    """Модель позиции по акции"""

    ticker: str
    broker_id: str
    broker_name: str
    quantity: int
    average_price: float
    current_price: Optional[float] = None
    total_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_percent: Optional[float] = None
    sector: Optional[str] = None
    currency: str = "RUB"
    # Новые поля для детального отчета
    first_purchase_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None
    total_invested: Optional[float] = None
    total_commission: Optional[float] = None
    transactions_count: Optional[int] = None


class BrokerStats(BaseModel):
    """Статистика по брокеру"""

    broker_id: str
    broker_name: str
    total_instruments: int
    active_instruments: int
    total_transactions: int
    total_value: float
    total_pnl: float


class StockPortfolioStats(BaseModel):
    """Общая статистика портфеля акций"""

    total_brokers: int
    total_instruments: int
    total_transactions: int
    total_value: float
    total_pnl: float
    total_pnl_percent: float
    positions: List[StockPosition]
    broker_stats: List[BrokerStats]
