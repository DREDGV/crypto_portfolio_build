"""
Сервис для работы с акциями и брокерами
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Session, select

from app.adapters.tinkoff_adapter import BrokerManager
from app.models.broker_models import (
    Broker,
    BrokerStats,
    StockInstrument,
    StockPortfolioStats,
    StockPosition,
    StockTransaction,
    StockTransactionIn,
)
from app.storage.db import engine

logger = logging.getLogger(__name__)


class StockService:
    """Сервис для работы с акциями"""

    def __init__(self):
        self.broker_manager = BrokerManager()

    def add_broker(self, broker_data: Broker) -> bool:
        """Добавляет брокера в базу данных"""
        try:
            with Session(engine) as session:
                # Проверяем, существует ли брокер
                existing = session.exec(
                    select(Broker).where(Broker.id == broker_data.id)
                ).first()
                if existing:
                    # Обновляем существующего брокера
                    existing.name = broker_data.name
                    existing.api_url = broker_data.api_url
                    existing.is_active = broker_data.is_active
                    existing.description = broker_data.description
                    existing.updated_at = datetime.utcnow()
                else:
                    # Добавляем нового брокера
                    session.add(broker_data)

                session.commit()
                logger.info(f"Брокер {broker_data.name} добавлен/обновлен")
                return True

        except Exception as e:
            logger.error(f"Ошибка добавления брокера: {e}")
            return False

    def get_all_brokers(self) -> List[Broker]:
        """Получает всех брокеров из базы данных"""
        try:
            with Session(engine) as session:
                brokers = session.exec(
                    select(Broker).where(Broker.is_active == True)
                ).all()
                return brokers
        except Exception as e:
            logger.error(f"Ошибка получения брокеров: {e}")
            return []

    def sync_broker_instruments(self, broker_id: str) -> int:
        """Синхронизирует инструменты брокера с базой данных"""
        try:
            # Получаем инструменты от брокера
            broker_instruments = self.broker_manager.get_instruments(broker_id)

            with Session(engine) as session:
                synced_count = 0

                for instrument in broker_instruments:
                    # Проверяем, существует ли инструмент
                    existing = session.exec(
                        select(StockInstrument).where(
                            StockInstrument.ticker == instrument.ticker,
                            StockInstrument.broker_id == broker_id,
                        )
                    ).first()

                    if existing:
                        # Обновляем существующий инструмент
                        existing.name = instrument.name
                        existing.sector = instrument.sector
                        existing.lot_size = instrument.lot_size
                        existing.currency = instrument.currency
                        existing.is_active = instrument.is_active
                        existing.updated_at = datetime.utcnow()
                    else:
                        # Добавляем новый инструмент
                        instrument.broker_id = broker_id
                        session.add(instrument)

                    synced_count += 1

                session.commit()
                logger.info(
                    f"Синхронизировано {synced_count} инструментов для брокера {broker_id}"
                )
                return synced_count

        except Exception as e:
            logger.error(f"Ошибка синхронизации инструментов: {e}")
            return 0

    def get_broker_instruments(
        self, broker_id: str, search_query: Optional[str] = None
    ) -> List[StockInstrument]:
        """Получает инструменты брокера"""
        try:
            with Session(engine) as session:
                query = select(StockInstrument).where(
                    StockInstrument.broker_id == broker_id,
                    StockInstrument.is_active == True,
                )

                if search_query:
                    query = query.where(
                        StockInstrument.ticker.contains(search_query)
                        | StockInstrument.name.contains(search_query)
                    )

                instruments = session.exec(query).all()
                return instruments

        except Exception as e:
            logger.error(f"Ошибка получения инструментов: {e}")
            return []

    def add_stock_transaction(self, transaction_data: StockTransactionIn) -> bool:
        """Добавляет транзакцию с акциями"""
        try:
            with Session(engine) as session:
                # Находим инструмент
                instrument = session.exec(
                    select(StockInstrument).where(
                        StockInstrument.ticker == transaction_data.ticker,
                        StockInstrument.broker_id == transaction_data.broker_id,
                    )
                ).first()

                if not instrument:
                    # Создаем новый инструмент, если его нет
                    logger.info(f"Создаем новый инструмент {transaction_data.ticker}")
                    instrument = StockInstrument(
                        ticker=transaction_data.ticker,
                        name=transaction_data.ticker,  # Используем тикер как название
                        sector="Неизвестно",
                        lot_size=1,
                        currency="RUB",
                        is_active=True,
                        broker_id=transaction_data.broker_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(instrument)
                    session.flush()  # Получаем ID нового инструмента

                # Создаем транзакцию
                transaction = StockTransaction(
                    ticker=transaction_data.ticker,
                    broker_id=transaction_data.broker_id,
                    instrument_id=instrument.id,
                    quantity=transaction_data.quantity,
                    price=transaction_data.price,
                    commission=transaction_data.commission,
                    transaction_type=transaction_data.transaction_type,
                    notes=transaction_data.notes,
                    transaction_date=transaction_data.transaction_date
                    or datetime.utcnow(),
                )

                session.add(transaction)
                session.commit()

                logger.info(
                    f"Добавлена транзакция {transaction_data.ticker} на сумму {transaction_data.quantity * transaction_data.price}"
                )
                return True

        except Exception as e:
            logger.error(f"Ошибка добавления транзакции: {e}")
            return False

    def get_stock_transactions(
        self, broker_id: Optional[str] = None, ticker: Optional[str] = None
    ) -> List[StockTransaction]:
        """Получает транзакции с акциями"""
        try:
            with Session(engine) as session:
                query = select(StockTransaction)

                if broker_id:
                    query = query.where(StockTransaction.broker_id == broker_id)

                if ticker:
                    query = query.where(StockTransaction.ticker == ticker)

                query = query.order_by(StockTransaction.transaction_date.desc())

                transactions = session.exec(query).all()
                return transactions

        except Exception as e:
            logger.error(f"Ошибка получения транзакций: {e}")
            return []

    def calculate_stock_positions(self) -> List[StockPosition]:
        """Рассчитывает текущие позиции по акциям"""
        try:
            transactions = self.get_stock_transactions()

            # Группируем транзакции по тикеру и брокеру
            positions = defaultdict(
                lambda: {
                    "quantity": 0,
                    "total_cost": 0.0,
                    "total_commission": 0.0,
                    "broker_id": "",
                    "broker_name": "",
                    "sector": "",
                    "currency": "RUB",
                    "first_purchase_date": None,
                    "last_purchase_date": None,
                    "transactions_count": 0,
                    "transactions": [],  # Сохраняем все транзакции для анализа
                }
            )

            for transaction in transactions:
                key = f"{transaction.ticker}_{transaction.broker_id}"

                # Сохраняем транзакцию для анализа
                positions[key]["transactions"].append(transaction)
                positions[key]["transactions_count"] += 1

                if transaction.transaction_type == "buy":
                    positions[key]["quantity"] += transaction.quantity
                    positions[key]["total_cost"] += (
                        transaction.quantity * transaction.price
                        + transaction.commission
                    )
                    positions[key]["total_commission"] += transaction.commission

                    # Обновляем даты покупки
                    if not positions[key]["first_purchase_date"]:
                        positions[key][
                            "first_purchase_date"
                        ] = transaction.transaction_date
                    positions[key]["last_purchase_date"] = transaction.transaction_date

                elif transaction.transaction_type == "sell":
                    positions[key]["quantity"] -= transaction.quantity
                    positions[key]["total_cost"] -= (
                        transaction.quantity * transaction.price
                        - transaction.commission
                    )
                    positions[key]["total_commission"] += transaction.commission

                positions[key]["broker_id"] = transaction.broker_id
                positions[key]["ticker"] = transaction.ticker

            # Получаем информацию о брокерах
            brokers = {broker.id: broker.name for broker in self.get_all_brokers()}

            # Получаем информацию об инструментах
            instruments = {}
            for broker in self.get_all_brokers():
                broker_instruments = self.get_broker_instruments(broker.id)
                for instrument in broker_instruments:
                    instruments[f"{instrument.ticker}_{broker.id}"] = instrument

            # Формируем позиции
            result_positions = []
            for key, pos_data in positions.items():
                if (
                    pos_data["quantity"] > 0
                ):  # Только позиции с положительным количеством
                    ticker, broker_id = key.split("_", 1)

                    # Получаем текущую цену
                    current_price = self.broker_manager.get_current_price(
                        broker_id, ticker
                    )

                    # Получаем информацию об инструменте
                    instrument = instruments.get(key)

                    position = StockPosition(
                        ticker=ticker,
                        broker_id=broker_id,
                        broker_name=brokers.get(broker_id, broker_id),
                        quantity=pos_data["quantity"],
                        average_price=(
                            pos_data["total_cost"] / pos_data["quantity"]
                            if pos_data["quantity"] > 0
                            else 0
                        ),
                        current_price=current_price,
                        total_value=(
                            current_price * pos_data["quantity"]
                            if current_price
                            else pos_data[
                                "total_cost"
                            ]  # Используем среднюю цену если текущая недоступна
                        ),
                        unrealized_pnl=(
                            (
                                current_price
                                - pos_data["total_cost"] / pos_data["quantity"]
                            )
                            * pos_data["quantity"]
                            if current_price and pos_data["quantity"] > 0
                            else 0.0  # Если текущая цена недоступна, P&L = 0
                        ),
                        unrealized_pnl_percent=(
                            (
                                (
                                    current_price
                                    - pos_data["total_cost"] / pos_data["quantity"]
                                )
                                / (pos_data["total_cost"] / pos_data["quantity"])
                                * 100
                            )
                            if current_price and pos_data["quantity"] > 0
                            else 0.0  # Если текущая цена недоступна, P&L% = 0
                        ),
                        sector=instrument.sector if instrument else None,
                        currency=instrument.currency if instrument else "RUB",
                        # Новые поля
                        first_purchase_date=pos_data["first_purchase_date"],
                        last_purchase_date=pos_data["last_purchase_date"],
                        total_invested=pos_data["total_cost"],
                        total_commission=pos_data["total_commission"],
                        transactions_count=pos_data["transactions_count"],
                    )

                    result_positions.append(position)

            return result_positions

        except Exception as e:
            logger.error(f"Ошибка расчета позиций: {e}")
            return []

    def get_stock_portfolio_stats(self) -> StockPortfolioStats:
        """Получает общую статистику портфеля акций"""
        try:
            brokers = self.get_all_brokers()
            positions = self.calculate_stock_positions()
            transactions = self.get_stock_transactions()

            # Статистика по брокерам
            broker_stats = []
            for broker in brokers:
                broker_positions = [p for p in positions if p.broker_id == broker.id]
                broker_transactions = [
                    t for t in transactions if t.broker_id == broker.id
                ]

                total_value = sum(p.total_value or 0 for p in broker_positions)
                total_pnl = sum(p.unrealized_pnl or 0 for p in broker_positions)

                broker_stat = BrokerStats(
                    broker_id=broker.id,
                    broker_name=broker.name,
                    total_instruments=len(self.get_broker_instruments(broker.id)),
                    active_instruments=len(
                        [
                            i
                            for i in self.get_broker_instruments(broker.id)
                            if i.is_active
                        ]
                    ),
                    total_transactions=len(broker_transactions),
                    total_value=total_value,
                    total_pnl=total_pnl,
                )
                broker_stats.append(broker_stat)

            # Общая статистика
            total_value = sum(p.total_value or 0 for p in positions)
            total_pnl = sum(p.unrealized_pnl or 0 for p in positions)
            total_pnl_percent = (
                (total_pnl / total_value * 100) if total_value > 0 else 0
            )

            stats = StockPortfolioStats(
                total_brokers=len(brokers),
                total_instruments=sum(bs.total_instruments for bs in broker_stats),
                total_transactions=len(transactions),
                total_value=total_value,
                total_pnl=total_pnl,
                total_pnl_percent=total_pnl_percent,
                positions=positions,
                broker_stats=broker_stats,
            )

            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики портфеля: {e}")
            return StockPortfolioStats(
                total_brokers=0,
                total_instruments=0,
                total_transactions=0,
                total_value=0.0,
                total_pnl=0.0,
                total_pnl_percent=0.0,
                positions=[],
                broker_stats=[],
            )

    def get_popular_instruments(
        self, broker_id: str, limit: int = 20
    ) -> List[StockInstrument]:
        """Получает популярные инструменты брокера"""
        return self.broker_manager.get_popular_instruments(broker_id, limit)

    def search_instruments(self, broker_id: str, query: str) -> List[StockInstrument]:
        """Поиск инструментов у брокера"""
        return self.broker_manager.search_instruments(broker_id, query)

    def get_current_price(self, broker_id: str, ticker: str) -> Optional[float]:
        """Получает текущую цену инструмента"""
        return self.broker_manager.get_current_price(broker_id, ticker)

    def get_multiple_prices(
        self, broker_id: str, tickers: List[str]
    ) -> Dict[str, float]:
        """Получает цены для нескольких инструментов"""
        return self.broker_manager.get_multiple_prices(broker_id, tickers)

    def get_all_tinkoff_stocks(self) -> List[Dict[str, Any]]:
        """Получает все акции Тинькофф (расширенный список)"""
        try:
            # Сначала пытаемся получить данные из MOEX API
            moex_stocks = self._get_moex_stocks()
            if moex_stocks:
                logger.info(f"Получено {len(moex_stocks)} акций с MOEX")
                return moex_stocks

            # Затем пытаемся получить данные из реального API Тинькофф
            real_stocks = self._get_real_tinkoff_stocks()
            if real_stocks:
                return real_stocks

            # Если API недоступны, используем расширенный список
            logger.info("Используем локальный список акций (API недоступны)")
            all_tinkoff_stocks = [
                # Финансы
                {
                    "ticker": "SBER",
                    "name": "Сбербанк",
                    "sector": "Финансы",
                    "currency": "RUB",
                },
                {
                    "ticker": "VTB",
                    "name": "ВТБ",
                    "sector": "Финансы",
                    "currency": "RUB",
                },
                {
                    "ticker": "ALRS",
                    "name": "Алроса",
                    "sector": "Финансы",
                    "currency": "RUB",
                },
                {
                    "ticker": "QIWI",
                    "name": "Киви",
                    "sector": "Финансы",
                    "currency": "RUB",
                },
                {
                    "ticker": "MOEX",
                    "name": "Московская Биржа",
                    "sector": "Финансы",
                    "currency": "RUB",
                },
                {
                    "ticker": "CBOM",
                    "name": "Кредит Европа Банк",
                    "sector": "Финансы",
                    "currency": "RUB",
                },
                {
                    "ticker": "RENI",
                    "name": "Ренессанс Кредит",
                    "sector": "Финансы",
                    "currency": "RUB",
                },
                # Энергетика
                {
                    "ticker": "GAZP",
                    "name": "Газпром",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                {
                    "ticker": "LKOH",
                    "name": "Лукойл",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                {
                    "ticker": "NVTK",
                    "name": "Новатэк",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                {
                    "ticker": "ROSN",
                    "name": "Роснефть",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                {
                    "ticker": "TATN",
                    "name": "Татнефть",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                {
                    "ticker": "TRNFP",
                    "name": "Транснефть",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                {
                    "ticker": "BANE",
                    "name": "Башнефть",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                {
                    "ticker": "SURG",
                    "name": "Сургутнефтегаз",
                    "sector": "Энергетика",
                    "currency": "RUB",
                },
                # Металлургия
                {
                    "ticker": "NLMK",
                    "name": "НЛМК",
                    "sector": "Металлургия",
                    "currency": "RUB",
                },
                {
                    "ticker": "MAGN",
                    "name": "Магнитогорский металлургический комбинат",
                    "sector": "Металлургия",
                    "currency": "RUB",
                },
                {
                    "ticker": "CHMF",
                    "name": "Северсталь",
                    "sector": "Металлургия",
                    "currency": "RUB",
                },
                {
                    "ticker": "RUAL",
                    "name": "РУСАЛ",
                    "sector": "Металлургия",
                    "currency": "RUB",
                },
                {
                    "ticker": "MRSB",
                    "name": "Мечел",
                    "sector": "Металлургия",
                    "currency": "RUB",
                },
                {
                    "ticker": "VSMO",
                    "name": "ВСМПО-АВИСМА",
                    "sector": "Металлургия",
                    "currency": "RUB",
                },
                # Добыча полезных ископаемых
                {
                    "ticker": "PLZL",
                    "name": "Полюс",
                    "sector": "Добыча полезных ископаемых",
                    "currency": "RUB",
                },
                {
                    "ticker": "ALRS",
                    "name": "Алроса",
                    "sector": "Добыча полезных ископаемых",
                    "currency": "RUB",
                },
                {
                    "ticker": "POLY",
                    "name": "Полиметалл",
                    "sector": "Добыча полезных ископаемых",
                    "currency": "RUB",
                },
                # Технологии
                {
                    "ticker": "YNDX",
                    "name": "Яндекс",
                    "sector": "Технологии",
                    "currency": "RUB",
                },
                {
                    "ticker": "OZON",
                    "name": "Озон",
                    "sector": "Технологии",
                    "currency": "RUB",
                },
                {
                    "ticker": "VKCO",
                    "name": "VK",
                    "sector": "Технологии",
                    "currency": "RUB",
                },
                {
                    "ticker": "MAIL",
                    "name": "Mail.ru Group",
                    "sector": "Технологии",
                    "currency": "RUB",
                },
                {
                    "ticker": "TCSG",
                    "name": "TCS Group",
                    "sector": "Технологии",
                    "currency": "RUB",
                },
                # Транспорт
                {
                    "ticker": "AFLT",
                    "name": "Аэрофлот",
                    "sector": "Транспорт",
                    "currency": "RUB",
                },
                {
                    "ticker": "SMLT",
                    "name": "Самолет",
                    "sector": "Транспорт",
                    "currency": "RUB",
                },
                {
                    "ticker": "NMTP",
                    "name": "Новороссийский морской торговый порт",
                    "sector": "Транспорт",
                    "currency": "RUB",
                },
                # Ритейл
                {
                    "ticker": "MGNT",
                    "name": "Магнит",
                    "sector": "Ритейл",
                    "currency": "RUB",
                },
                {
                    "ticker": "FIVE",
                    "name": "X5 Group",
                    "sector": "Ритейл",
                    "currency": "RUB",
                },
                {
                    "ticker": "DSKY",
                    "name": "Детский мир",
                    "sector": "Ритейл",
                    "currency": "RUB",
                },
                {
                    "ticker": "LENT",
                    "name": "Лента",
                    "sector": "Ритейл",
                    "currency": "RUB",
                },
                # Девелопмент
                {
                    "ticker": "PIKK",
                    "name": "ПИК",
                    "sector": "Девелопмент",
                    "currency": "RUB",
                },
                {
                    "ticker": "LSRG",
                    "name": "ЛСР",
                    "sector": "Девелопмент",
                    "currency": "RUB",
                },
                {
                    "ticker": "RSTI",
                    "name": "Россети",
                    "sector": "Девелопмент",
                    "currency": "RUB",
                },
                # Химия
                {
                    "ticker": "PHOR",
                    "name": "ФосАгро",
                    "sector": "Химия",
                    "currency": "RUB",
                },
                {
                    "ticker": "KAZ",
                    "name": "Казаньоргсинтез",
                    "sector": "Химия",
                    "currency": "RUB",
                },
                # Телекоммуникации
                {
                    "ticker": "MTSS",
                    "name": "МТС",
                    "sector": "Телекоммуникации",
                    "currency": "RUB",
                },
                {
                    "ticker": "RTKM",
                    "name": "Ростелеком",
                    "sector": "Телекоммуникации",
                    "currency": "RUB",
                },
                {
                    "ticker": "MGTSP",
                    "name": "МГТС",
                    "sector": "Телекоммуникации",
                    "currency": "RUB",
                },
                # Потребительские товары
                {
                    "ticker": "CHMK",
                    "name": "Черкизово",
                    "sector": "Потребительские товары",
                    "currency": "RUB",
                },
                {
                    "ticker": "ABRD",
                    "name": "Абрау-Дюрсо",
                    "sector": "Потребительские товары",
                    "currency": "RUB",
                },
                # Медицина
                {
                    "ticker": "PHST",
                    "name": "Фармстандарт",
                    "sector": "Медицина",
                    "currency": "RUB",
                },
                {
                    "ticker": "RBCM",
                    "name": "Р-Фарм",
                    "sector": "Медицина",
                    "currency": "RUB",
                },
                # Утилиты
                {
                    "ticker": "HYDR",
                    "name": "РусГидро",
                    "sector": "Утилиты",
                    "currency": "RUB",
                },
                {
                    "ticker": "IRAO",
                    "name": "Интер РАО",
                    "sector": "Утилиты",
                    "currency": "RUB",
                },
                {
                    "ticker": "OGKB",
                    "name": "ОГК-2",
                    "sector": "Утилиты",
                    "currency": "RUB",
                },
                # Другое
                {
                    "ticker": "LIFE",
                    "name": "Лайф",
                    "sector": "Другое",
                    "currency": "RUB",
                },
                {
                    "ticker": "RBCM",
                    "name": "РБК",
                    "sector": "Другое",
                    "currency": "RUB",
                },
            ]

            return all_tinkoff_stocks

        except Exception as e:
            logger.error(f"Ошибка получения всех акций Тинькофф: {e}")
            return []

    def _get_real_tinkoff_stocks(self) -> Optional[List[Dict[str, Any]]]:
        """Получает реальные данные акций через API"""
        try:
            # Здесь можно добавить реальные API вызовы
            # Пока возвращаем None, чтобы использовать локальный список

            # Пример для будущей реализации:
            # import requests
            #
            # # Тинькофф API
            # url = "https://invest-public-api.tinkoff.ru/rest/"
            # headers = {"Authorization": f"Bearer {TINKOFF_TOKEN}"}
            #
            # # Или MOEX API (бесплатный)
            # moex_url = "https://iss.moex.com/iss/securities.json"
            # response = requests.get(moex_url)
            #
            # if response.status_code == 200:
            #     data = response.json()
            #     # Обработка данных...
            #     return processed_stocks

            return None

        except Exception as e:
            logger.error(f"Ошибка получения реальных данных акций: {e}")
            return None

    def _get_moex_stocks(self) -> Optional[List[Dict[str, Any]]]:
        """Получает акции с MOEX API"""
        try:
            import requests

            base_url = "https://iss.moex.com/iss"
            all_securities = []
            start = 0

            # Получаем данные с пагинацией
            while True:
                url = f"{base_url}/securities.json"
                params = {"start": start}
                response = requests.get(url, params=params, timeout=10)

                if response.status_code != 200:
                    break

                data = response.json()
                securities = data.get("securities", {}).get("data", [])

                if not securities:
                    break

                all_securities.extend(securities)
                start += len(securities)

                # Ограничиваем количество для производительности
                if start > 2000:
                    break

            if all_securities:
                columns = data.get("securities", {}).get("columns", [])
                result = []

                for security in all_securities:
                    security_dict = dict(zip(columns, security))

                    # Фильтруем только акции на основной доске
                    security_type = security_dict.get("type", "").lower()
                    board = security_dict.get("primary_boardid", "")

                    is_share = (
                        "share" in security_type
                        or security_type == "common_share"
                        or security_type == "preferred_share"
                    )

                    if is_share and board == "TQBR":
                        result.append(
                            {
                                "ticker": security_dict.get("secid", ""),
                                "name": security_dict.get("name", ""),
                                "sector": security_dict.get("group", ""),
                                "currency": "RUB",
                                "lot_size": 1,
                                "is_active": security_dict.get("is_traded", False),
                                "source": "MOEX",
                            }
                        )

                logger.info(f"Получено {len(result)} акций с MOEX")
                return result
            else:
                return None

        except Exception as e:
            logger.error(f"Ошибка получения данных с MOEX: {e}")
            return None
