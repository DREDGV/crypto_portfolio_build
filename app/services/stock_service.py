#!/usr/bin/env python3
"""Сервис для работы с акциями"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests
from sqlalchemy.orm import Session

from app.adapters.prices import PriceAdapter
from app.core.database import get_db
from app.models.stock_models import (
    StockAnalysis,
    StockDividend,
    StockNews,
    StockPosition,
    StockPrice,
    StockTransaction,
    StockTransactionIn,
)


class StockService:
    """Сервис для работы с акциями"""

    def __init__(self):
        self.price_adapter = PriceAdapter()

    def add_stock_transaction(
        self, transaction: StockTransactionIn
    ) -> StockTransaction:
        """Добавляет новую транзакцию с акцией"""
        db = next(get_db())
        try:
            # Создаем транзакцию
            db_transaction = StockTransaction(
                symbol=transaction.symbol,
                company_name=transaction.company_name,
                transaction_type=transaction.transaction_type,
                quantity=transaction.quantity,
                price_per_share=transaction.price_per_share,
                total_amount=transaction.total_amount,
                commission=transaction.commission,
                currency=transaction.currency,
                exchange=transaction.exchange,
                date=transaction.date,
                notes=transaction.notes,
            )

            db.add(db_transaction)
            db.commit()
            db.refresh(db_transaction)

            return db_transaction

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_stock_transactions(
        self, symbol: Optional[str] = None
    ) -> List[StockTransaction]:
        """Получает список транзакций с акциями"""
        db = next(get_db())
        try:
            query = db.query(StockTransaction)
            if symbol:
                query = query.filter(StockTransaction.symbol == symbol.upper())

            return query.order_by(StockTransaction.date.desc()).all()

        finally:
            db.close()

    def get_stock_positions(self) -> List[StockPosition]:
        """Получает текущие позиции по акциям"""
        db = next(get_db())
        try:
            # Получаем все транзакции
            transactions = db.query(StockTransaction).all()

            # Группируем по символам
            positions = {}

            for tx in transactions:
                symbol = tx.symbol
                if symbol not in positions:
                    positions[symbol] = {
                        "symbol": symbol,
                        "company_name": tx.company_name,
                        "total_quantity": Decimal("0"),
                        "total_invested": Decimal("0"),
                        "transactions": [],
                    }

                positions[symbol]["transactions"].append(tx)

            # Вычисляем позиции
            result = []
            for symbol, data in positions.items():
                total_quantity = Decimal("0")
                total_invested = Decimal("0")

                for tx in data["transactions"]:
                    if tx.transaction_type in ["buy", "bonus"]:
                        total_quantity += tx.quantity
                        total_invested += tx.total_amount + tx.commission
                    elif tx.transaction_type in ["sell", "split"]:
                        total_quantity -= tx.quantity
                        total_invested -= tx.total_amount - tx.commission

                if total_quantity > 0:
                    average_price = total_invested / total_quantity

                    position = StockPosition(
                        symbol=symbol,
                        company_name=data["company_name"],
                        total_quantity=total_quantity,
                        average_price=average_price,
                        total_invested=total_invested,
                        exchange=data["transactions"][0].exchange,
                        currency=data["transactions"][0].currency,
                    )

                    result.append(position)

            return result

        finally:
            db.close()

    def get_stock_price(self, symbol: str) -> Optional[StockPrice]:
        """Получает текущую цену акции"""
        try:
            # Используем существующий адаптер цен
            price_data = self.price_adapter.get_price(symbol.upper())

            if price_data:
                return StockPrice(
                    symbol=symbol.upper(),
                    price=Decimal(str(price_data.get("price", 0))),
                    currency=price_data.get("currency", "USD"),
                    exchange=price_data.get("exchange", "NASDAQ"),
                    change_24h=Decimal(str(price_data.get("change_24h", 0))),
                    change_percent_24h=Decimal(
                        str(price_data.get("change_percent_24h", 0))
                    ),
                    volume=price_data.get("volume"),
                    market_cap=(
                        Decimal(str(price_data.get("market_cap", 0)))
                        if price_data.get("market_cap")
                        else None
                    ),
                    last_updated=datetime.now(),
                )

            return None

        except Exception as e:
            print(f"Ошибка получения цены акции {symbol}: {e}")
            return None

    def update_stock_prices(self, symbols: List[str]) -> Dict[str, StockPrice]:
        """Обновляет цены для списка акций"""
        prices = {}

        for symbol in symbols:
            price = self.get_stock_price(symbol)
            if price:
                prices[symbol] = price

        return prices

    def get_stock_dividends(self, symbol: str) -> List[StockDividend]:
        """Получает информацию о дивидендах по акции"""
        # Заглушка - в реальном приложении здесь будет API для получения дивидендов
        return []

    def get_stock_news(self, symbol: str, limit: int = 10) -> List[StockNews]:
        """Получает новости по акции"""
        # Заглушка - в реальном приложении здесь будет API для получения новостей
        return []

    def get_stock_analysis(self, symbol: str) -> Optional[StockAnalysis]:
        """Получает анализ акции"""
        # Заглушка - в реальном приложении здесь будет API для получения анализа
        return None

    def calculate_portfolio_value(self) -> Dict[str, Any]:
        """Вычисляет общую стоимость портфеля акций"""
        positions = self.get_stock_positions()
        total_value = Decimal("0")
        total_invested = Decimal("0")

        for position in positions:
            # Получаем текущую цену
            current_price = self.get_stock_price(position.symbol)
            if current_price:
                position.current_price = current_price.price
                position.current_value = position.total_quantity * current_price.price
                position.unrealized_pnl = (
                    position.current_value - position.total_invested
                )
                position.unrealized_pnl_percent = (
                    position.unrealized_pnl / position.total_invested
                ) * 100
                position.last_updated = current_price.last_updated

            total_value += position.current_value or Decimal("0")
            total_invested += position.total_invested

        total_pnl = total_value - total_invested
        total_pnl_percent = (
            (total_pnl / total_invested * 100) if total_invested > 0 else Decimal("0")
        )

        return {
            "total_value": total_value,
            "total_invested": total_invested,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "positions_count": len(positions),
            "positions": positions,
        }
