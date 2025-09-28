import os

from sqlmodel import SQLModel, create_engine

# Импортируем все модели для создания таблиц
from app.core.models import Transaction, PriceAlert, SourceMeta
from app.models.broker_models import Broker, StockInstrument, StockTransaction

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "portfolio.db")
)
DB_URI = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URI, echo=False)


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    SQLModel.metadata.create_all(engine)
