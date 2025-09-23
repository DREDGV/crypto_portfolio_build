import datetime as dt
import os
import shutil
import time
from collections import defaultdict, deque
import json

from sqlmodel import Session, select

from app.adapters.prices import get_current_price
from app.core.models import Transaction, TransactionIn, SourceMeta, PriceAlert, PriceAlertIn
from app.storage.db import DB_PATH, engine
from app.core.cache import (
    cached, cache_portfolio_stats, get_cached_portfolio_stats,
    cache_transactions, get_cached_transactions,
    cache_sources, get_cached_sources,
    cache_price_alerts, get_cached_price_alerts,
    invalidate_data_cache
)

CURRENCY = os.getenv("REPORT_CURRENCY", "USD").upper()


def add_transaction(data: TransactionIn) -> int:
    if not data.coin:
        raise ValueError("coin is required")
    if data.quantity <= 0:
        raise ValueError("quantity must be > 0")
    if data.price < 0:
        raise ValueError("price must be >= 0")
    with Session(engine) as session:
        t = Transaction(**data.model_dump())
        session.add(t)
        session.commit()
        session.refresh(t)
        
        # Инвалидируем кэш после добавления транзакции
        invalidate_data_cache()
        
        return t.id


def get_transaction(tx_id: int) -> dict | None:
    with Session(engine) as session:
        t = session.get(Transaction, tx_id)
        if not t:
            return None
        return {
            "id": t.id,
            "coin": t.coin,
            "type": t.type,
            "quantity": t.quantity,
            "price": t.price,
            "strategy": t.strategy,
            "source": t.source or "",
            "notes": t.notes or "",
            "ts_utc": t.ts_utc,
        }


def update_transaction(tx_id: int, data: TransactionIn) -> None:
    with Session(engine) as session:
        t = session.get(Transaction, tx_id)
        if not t:
            return
        t.coin = data.coin
        t.type = data.type
        t.quantity = data.quantity
        t.price = data.price
        t.strategy = data.strategy
        t.source = data.source
        t.notes = data.notes
        session.add(t)
        session.commit()


def delete_transaction(tx_id: int) -> None:
    with Session(engine) as session:
        t = session.get(Transaction, tx_id)
        if t:
            session.delete(t)
            session.commit()


def list_transactions() -> list[dict]:
    # Пытаемся получить из кэша
    cached_result = get_cached_transactions()
    if cached_result is not None:
        return cached_result
    
    with Session(engine) as session:
        items = session.exec(select(Transaction).order_by(Transaction.id.desc())).all()
    rows = []
    for t in items:
        ts_local = dt.datetime.fromtimestamp(t.ts_utc.timestamp())
        rows.append(
            {
                "id": t.id,
                "coin": t.coin,
                "type": t.type,
                "quantity": t.quantity,
                "price": t.price,
                "created_at": ts_local.strftime("%Y-%m-%d %H:%M:%S"),  # Исправлено: было ts_local
                "strategy": t.strategy,
                "source": t.source or "",  # Уже правильно
                "notes": t.notes or "",
            }
        )
    
    # Кэшируем результат
    cache_transactions(rows)
    
    return rows


def positions_fifo() -> list[dict]:
    with Session(engine) as session:
        items = session.exec(
            select(Transaction).order_by(Transaction.ts_utc.asc(), Transaction.id.asc())
        ).all()
    lots: dict[tuple[str, str], deque] = defaultdict(deque)
    realized: dict[tuple[str, str], float] = defaultdict(float)
    for t in items:
        key = (t.coin.upper(), t.strategy)
        if t.type in ("buy", "exchange_in", "deposit"):
            lots[key].append({"qty": float(t.quantity), "price": float(t.price)})
        elif t.type in ("sell", "exchange_out", "withdrawal"):
            qty_left = float(t.quantity)
            sell_price = float(t.price)
            while qty_left > 0 and lots[key]:
                lot = lots[key][0]
                take = min(qty_left, lot["qty"])
                realized[key] += take * (sell_price - lot["price"])
                lot["qty"] -= take
                qty_left -= take
                if lot["qty"] <= 1e-12:
                    lots[key].popleft()
    positions = []
    for key, queue in lots.items():
        coin, strat = key
        qty = sum(lot["qty"] for lot in queue)
        cost = sum(lot["qty"] * lot["price"] for lot in queue)
        avg = (cost / qty) if qty > 0 else 0.0
        positions.append(
            {
                "key": f"{coin}:{strat}",
                "coin": coin,
                "strategy": strat,
                "quantity": round(qty, 8),
                "avg_cost": round(avg, 8),
                "cost_basis": round(cost, 2),
                "realized": round(realized[key], 2),
            }
        )
    for key, rpnl in realized.items():
        if rpnl != 0 and all(p["key"] != f"{key[0]}:{key[1]}" for p in positions):
            positions.append(
                {
                    "key": f"{key[0]}:{key[1]}",
                    "coin": key[0],
                    "strategy": key[1],
                    "quantity": 0.0,
                    "avg_cost": 0.0,
                    "cost_basis": 0.0,
                    "realized": round(rpnl, 2),
                }
            )
    return positions


def enrich_positions_with_market(positions: list[dict], quote: str = "USD"):
    total_value = 0.0
    total_unreal = 0.0
    total_realized = 0.0
    enriched = []
    for p in positions:
        price = get_current_price(p["coin"], quote=quote) or 0.0
        value = p["quantity"] * price
        unreal = value - p["cost_basis"]
        unreal_pct = (
            (price - p["avg_cost"]) / p["avg_cost"] * 100 if p["avg_cost"] > 0 else 0.0
        )
        total_value += value
        total_unreal += unreal
        total_realized += p["realized"]
        enriched.append(
            {
                **p,
                "price": round(price, 6),
                "value": round(value, 2),
                "unreal_pnl": round(unreal, 2),
                "unreal_pct": round(unreal_pct, 2),
            }
        )
    totals = {
        "total_value": round(total_value, 2),
        "total_unreal": round(total_unreal, 2),
        "total_unreal_pct": round(
            (
                (total_unreal / (total_value - total_unreal) * 100)
                if (total_value - total_unreal) > 0
                else 0.0
            ),
            2,
        ),
        "total_realized": round(total_realized, 2),
    }
    return enriched, totals


def backup_database() -> str:
    backup_dir = os.path.join(os.path.dirname(DB_PATH), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    target = os.path.join(
        backup_dir, "portfolio_backup_" + time.strftime("%Y%m%d_%H%M%S") + ".db"
    )
    shutil.copy(DB_PATH, target)
    return target


def export_transactions_csv() -> str:
    """Экспортирует все сделки в CSV файл"""
    export_dir = os.path.join(os.path.dirname(DB_PATH), "exports")
    os.makedirs(export_dir, exist_ok=True)

    filename = f"transactions_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_dir, filename)

    transactions = list_transactions()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        if not transactions:
            f.write("id,coin,type,quantity,price,ts_local,strategy,source,notes\n")
        else:
            # Заголовки
            headers = list(transactions[0].keys())
            f.write(",".join(headers) + "\n")

            # Данные
            for tx in transactions:
                row = []
                for header in headers:
                    value = tx.get(header, "")
                    # Экранируем запятые в значениях
                    if "," in str(value):
                        value = f'"{value}"'
                    row.append(str(value))
                f.write(",".join(row) + "\n")

    return filepath


def export_positions_csv(positions: list[dict]) -> str:
    """Экспортирует позиции в CSV файл"""
    export_dir = os.path.join(os.path.dirname(DB_PATH), "exports")
    os.makedirs(export_dir, exist_ok=True)

    filename = f"positions_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        if not positions:
            f.write(
                "coin,strategy,quantity,avg_cost,price,value,unreal_pnl,unreal_pct,realized\n"
            )
        else:
            # Заголовки
            headers = list(positions[0].keys())
            f.write(",".join(headers) + "\n")

            # Данные
            for pos in positions:
                row = []
                for header in headers:
                    value = pos.get(header, "")
                    # Экранируем запятые в значениях
                    if "," in str(value):
                        value = f'"{value}"'
                    row.append(str(value))
                f.write(",".join(row) + "\n")

    return filepath


def get_portfolio_stats() -> dict:
    """Возвращает детальную статистику портфеля"""
    # Пытаемся получить из кэша
    cached_result = get_cached_portfolio_stats()
    if cached_result is not None:
        return cached_result
    
    positions = positions_fifo()
    enriched, totals = enrich_positions_with_market(positions)

    # Статистика по монетам
    coin_stats = {}
    for pos in enriched:
        coin = pos["coin"]
        if coin not in coin_stats:
            coin_stats[coin] = {
                "total_value": 0,
                "total_pnl": 0,
                "positions_count": 0,
                "strategies": set(),
            }
        coin_stats[coin]["total_value"] += pos["value"]
        coin_stats[coin]["total_pnl"] += pos["unreal_pnl"] + pos["realized"]
        coin_stats[coin]["positions_count"] += 1
        coin_stats[coin]["strategies"].add(pos["strategy"])

    # Конвертируем set в list для JSON сериализации
    for coin in coin_stats:
        coin_stats[coin]["strategies"] = list(coin_stats[coin]["strategies"])

    # Статистика по стратегиям
    strategy_stats = {}
    for pos in enriched:
        strategy = pos["strategy"]
        if strategy not in strategy_stats:
            strategy_stats[strategy] = {
                "total_value": 0,
                "total_pnl": 0,
                "positions_count": 0,
            }
        strategy_stats[strategy]["total_value"] += pos["value"]
        strategy_stats[strategy]["total_pnl"] += pos["unreal_pnl"] + pos["realized"]
        strategy_stats[strategy]["positions_count"] += 1

    # Топ позиции по PnL
    top_positions = sorted(
        enriched, key=lambda x: x["unreal_pnl"] + x["realized"], reverse=True
    )[:5]

    # Общая статистика
    total_positions = len(enriched)
    total_coins = len(coin_stats)
    total_strategies = len(strategy_stats)

    result = {
        "totals": totals,
        "coin_stats": coin_stats,
        "strategy_stats": strategy_stats,
        "top_positions": top_positions,
        "summary": {
            "total_positions": total_positions,
            "total_coins": total_coins,
            "total_strategies": total_strategies,
        },
    }
    
    # Кэшируем результат
    cache_portfolio_stats(result)
    
    return result


def get_transaction_stats() -> dict:
    """Возвращает статистику по сделкам"""
    transactions = list_transactions()

    if not transactions:
        return {
            "total_transactions": 0,
            "transactions_by_type": {},
            "transactions_by_coin": {},
            "transactions_by_strategy": {},
            "recent_transactions": [],
        }

    # Статистика по типам
    type_stats = {}
    coin_stats = {}
    strategy_stats = {}

    for tx in transactions:
        # По типам
        tx_type = tx["type"]
        type_stats[tx_type] = type_stats.get(tx_type, 0) + 1

        # По монетам
        coin = tx["coin"]
        coin_stats[coin] = coin_stats.get(coin, 0) + 1

        # По стратегиям
        strategy = tx["strategy"]
        strategy_stats[strategy] = strategy_stats.get(strategy, 0) + 1

    # Последние 5 сделок
    recent_transactions = transactions[:5]

    return {
        "total_transactions": len(transactions),
        "transactions_by_type": type_stats,
        "transactions_by_coin": coin_stats,
        "transactions_by_strategy": strategy_stats,
        "recent_transactions": recent_transactions,
    }


# Простая система алертов (в памяти)
_alert_rules = []
_alert_history = []


def add_alert_rule(
    coin: str, strategy: str, alert_type: str, threshold: float, message: str = ""
) -> int:
    """Добавляет правило алерта"""
    rule_id = len(_alert_rules) + 1
    rule = {
        "id": rule_id,
        "coin": coin.upper(),
        "strategy": strategy,
        "type": alert_type,  # 'price_up', 'price_down', 'pnl_up', 'pnl_down'
        "threshold": threshold,
        "message": message,
        "active": True,
        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    _alert_rules.append(rule)
    return rule_id


def get_alert_rules() -> list:
    """Возвращает все правила алертов"""
    return _alert_rules


def delete_alert_rule(rule_id: int) -> bool:
    """Удаляет правило алерта"""
    global _alert_rules
    _alert_rules = [r for r in _alert_rules if r["id"] != rule_id]
    return True


def check_alerts() -> list:
    """Проверяет все активные алерты"""
    triggered = []
    positions = positions_fifo()
    enriched, _ = enrich_positions_with_market(positions)

    for rule in _alert_rules:
        if not rule["active"]:
            continue

        # Находим позиции, соответствующие правилу
        matching_positions = [
            p
            for p in enriched
            if p["coin"] == rule["coin"]
            and (rule["strategy"] == "all" or p["strategy"] == rule["strategy"])
        ]

        for pos in matching_positions:
            triggered_this_pos = False

            if rule["type"] == "price_up" and pos["price"] >= rule["threshold"]:
                triggered_this_pos = True
                message = f"Цена {pos['coin']} выросла до {pos['price']:.2f} {CURRENCY}"
            elif rule["type"] == "price_down" and pos["price"] <= rule["threshold"]:
                triggered_this_pos = True
                message = f"Цена {pos['coin']} упала до {pos['price']:.2f} {CURRENCY}"
            elif rule["type"] == "pnl_up" and pos["unreal_pnl"] >= rule["threshold"]:
                triggered_this_pos = True
                message = (
                    f"PnL {pos['coin']} вырос до {pos['unreal_pnl']:+.2f} {CURRENCY}"
                )
            elif rule["type"] == "pnl_down" and pos["unreal_pnl"] <= rule["threshold"]:
                triggered_this_pos = True
                message = (
                    f"PnL {pos['coin']} упал до {pos['unreal_pnl']:+.2f} {CURRENCY}"
                )

            if triggered_this_pos:
                alert = {
                    "rule_id": rule["id"],
                    "coin": pos["coin"],
                    "strategy": pos["strategy"],
                    "message": rule["message"] or message,
                    "triggered_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "price": pos["price"],
                    "pnl": pos["unreal_pnl"],
                }
                triggered.append(alert)
                _alert_history.append(alert)

    return triggered


def get_alert_history() -> list:
    """Возвращает историю срабатываний алертов"""
    return sorted(_alert_history, key=lambda x: x["triggered_at"], reverse=True)


# ===== УПРАВЛЕНИЕ ИСТОЧНИКАМИ =====

POPULAR_SOURCES = [
    "Binance",
    "Coinbase",
    "Kraken",
    "OKX",
    "Bybit",
    "KuCoin",
    "Huobi",
    "Gate.io",
]

def _get_source_meta_map(session: Session) -> dict[str, SourceMeta]:
    metas = session.exec(select(SourceMeta)).all()
    return {m.original_name: m for m in metas}


def export_sources_meta() -> str:
    """Экспортирует метаданные источников в JSON-файл и возвращает путь."""
    export_dir = os.path.join(os.path.dirname(DB_PATH), "exports")
    os.makedirs(export_dir, exist_ok=True)
    filename = f"sources_meta_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join(export_dir, filename)
    with Session(engine) as session:
        metas = session.exec(select(SourceMeta)).all()
        data = [
            {
                "original_name": m.original_name,
                "custom_name": m.custom_name,
                "order_index": m.order_index,
                "hidden": bool(m.hidden),
                "updated_at": m.updated_at.isoformat(),
            }
            for m in metas
        ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def import_sources_meta_from_json_str(json_str: str) -> bool:
    """Импортирует метаданные источников из JSON-строки."""
    try:
        items = json.loads(json_str)
        if not isinstance(items, list):
            return False
        with Session(engine) as session:
            for item in items:
                orig = item.get("original_name")
                if not orig:
                    continue
                meta = session.exec(select(SourceMeta).where(SourceMeta.original_name == orig)).first()
                if not meta:
                    meta = SourceMeta(original_name=orig)
                meta.custom_name = item.get("custom_name")
                meta.order_index = item.get("order_index")
                meta.hidden = bool(item.get("hidden", False))
                meta.updated_at = dt.datetime.now()
                session.add(meta)
            session.commit()
        return True
    except Exception as _:  # noqa: BLE001
        return False

def get_sources_with_frequency() -> list[tuple[str, int]]:
    """Получает источники с частотой использования"""
    # Пытаемся получить из кэша
    cached_result = get_cached_sources()
    if cached_result is not None:
        return cached_result
    
    try:
        with Session(engine) as session:
            # Получаем все источники из транзакций
            statement = select(Transaction.source).where(Transaction.source.isnot(None))
            sources = session.exec(statement).all()
            
            # Подсчитываем частоту
            source_counts = {}
            for source in sources:
                if source and source.strip():
                    source_counts[source.strip()] = source_counts.get(source.strip(), 0) + 1
            
            # Применяем пользовательские названия и скрытые из таблицы SourceMeta
            meta_map = _get_source_meta_map(session)
            for original_name in POPULAR_SOURCES:
                meta = meta_map.get(original_name)
                if meta and meta.hidden:
                    continue
                custom_name = (meta.custom_name if meta and meta.custom_name else original_name)
                if custom_name not in source_counts:
                    source_counts[custom_name] = 0
            
            # Сортируем по частоте использования, затем по пользовательскому порядку
            def sort_key(item):
                name, frequency = item
                # Сначала по частоте (по убыванию)
                freq_priority = -frequency
                # Затем по пользовательскому порядку из метаданных
                order_priority = 999
                # Поиск order_index по custom_name или original_name
                for meta in meta_map.values():
                    if (meta.custom_name or meta.original_name) == name:
                        order_priority = meta.order_index if meta.order_index is not None else 999
                        break
                return (freq_priority, order_priority)
            
            sorted_sources = sorted(source_counts.items(), key=sort_key)
            
            # Кэшируем результат
            cache_sources(sorted_sources)
            
            return sorted_sources
    except Exception as e:
        print(f"Ошибка получения источников: {e}")
        return [("Binance", 0), ("Coinbase", 0), ("Kraken", 0), ("OKX", 0), ("Bybit", 0), ("KuCoin", 0), ("Huobi", 0), ("Gate.io", 0)]


def update_source_name(old_name: str, new_name: str) -> bool:
    """Обновляет название источника во всех транзакциях и в пользовательских названиях"""
    try:
        with Session(engine) as session:
            # Обновляем/создаем метаданные
            meta = session.exec(select(SourceMeta).where(SourceMeta.original_name == old_name)).first()
            if not meta:
                meta = SourceMeta(original_name=old_name)
            meta.custom_name = new_name
            meta.updated_at = dt.datetime.now()
            session.add(meta)
            # Находим все транзакции с старым названием источника
            statement = select(Transaction).where(Transaction.source == old_name)
            transactions = session.exec(statement).all()
            
            
            # Обновляем название источника в транзакциях
            for tx in transactions:
                tx.source = new_name
            
            session.commit()
            
            # Инвалидируем кэш после изменения источников
            invalidate_data_cache()
            
            return True
    except Exception as e:
        print(f"Ошибка обновления источника: {e}")
        return False


def delete_source_from_transactions(source_name: str) -> bool:
    """Удаляет источник из всех транзакций и скрывает его"""
    try:
        with Session(engine) as session:
            # Определяем original_name через метаданные
            original_name = source_name
            meta_by_custom = session.exec(
                select(SourceMeta).where(SourceMeta.custom_name == source_name)
            ).first()
            if meta_by_custom:
                original_name = meta_by_custom.original_name
            # Обновляем/создаем метаданные и скрываем
            meta = session.exec(select(SourceMeta).where(SourceMeta.original_name == original_name)).first()
            if not meta:
                meta = SourceMeta(original_name=original_name)
            meta.hidden = True
            meta.updated_at = dt.datetime.now()
            session.add(meta)
            # Находим все транзакции с указанным источником
            statement = select(Transaction).where(Transaction.source == source_name)
            transactions = session.exec(statement).all()
            
            
            # Удаляем источник (устанавливаем в None)
            for tx in transactions:
                tx.source = None
            
            session.commit()
            
            # Инвалидируем кэш после удаления источника
            invalidate_data_cache()
            
            return True
    except Exception as e:
        print(f"Ошибка удаления источника: {e}")
        return False


def move_source_up(source_name: str) -> bool:
    """Перемещает источник вверх в списке"""
    try:
        sources = get_sources_with_frequency()
        current_index = None
        
        # Находим текущий индекс источника
        for i, (name, freq) in enumerate(sources):
            if name == source_name:
                current_index = i
                break
        
        if current_index is None or current_index == 0:
            return False
        
        # Меняем порядок в метаданных
        with Session(engine) as session:
            # Присваиваем индексы текущему и соседу
            prev_source = sources[current_index - 1][0]
            for name, idx in [(source_name, current_index - 1), (prev_source, current_index)]:
                # Ищем мету по original_name или custom_name
                meta = session.exec(select(SourceMeta).where((SourceMeta.custom_name == name) | (SourceMeta.original_name == name))).first()
                if not meta:
                    meta = SourceMeta(original_name=name if name in POPULAR_SOURCES else name, custom_name=None)
                meta.order_index = idx
                meta.updated_at = dt.datetime.now()
                session.add(meta)
            session.commit()
        
        return True
    except Exception as e:
        print(f"Ошибка перемещения источника вверх: {e}")
        return False

def move_source_down(source_name: str) -> bool:
    """Перемещает источник вниз в списке"""
    try:
        sources = get_sources_with_frequency()
        current_index = None
        
        # Находим текущий индекс источника
        for i, (name, freq) in enumerate(sources):
            if name == source_name:
                current_index = i
                break
        
        if current_index is None or current_index == len(sources) - 1:
            return False
        
        # Меняем порядок в метаданных
        with Session(engine) as session:
            next_source = sources[current_index + 1][0]
            for name, idx in [(source_name, current_index + 1), (next_source, current_index)]:
                meta = session.exec(select(SourceMeta).where((SourceMeta.custom_name == name) | (SourceMeta.original_name == name))).first()
                if not meta:
                    meta = SourceMeta(original_name=name if name in POPULAR_SOURCES else name, custom_name=None)
                meta.order_index = idx
                meta.updated_at = dt.datetime.now()
                session.add(meta)
            session.commit()
        
        return True
    except Exception as e:
        print(f"Ошибка перемещения источника вниз: {e}")
        return False

def get_source_statistics() -> dict:
    """Возвращает статистику по источникам"""
    try:
        sources_with_freq = get_sources_with_frequency()
        total_transactions = sum(freq for _, freq in sources_with_freq)
        
        return {
            "total_transactions": total_transactions,
            "unique_sources": len(sources_with_freq),
            "sources_with_frequency": sources_with_freq,
            "top_sources": sources_with_freq[:10]  # Топ-10
        }
    except Exception as e:
        print(f"Ошибка получения статистики источников: {e}")
        return {
            "total_transactions": 0,
            "unique_sources": 0,
            "sources_with_frequency": [],
            "top_sources": []
        }


# ==================== СИСТЕМА АЛЕРТОВ ПО ЦЕНАМ ====================

def add_price_alert(data: PriceAlertIn) -> int:
    """Добавляет новый алерт по цене."""
    try:
        with Session(engine) as session:
            alert = PriceAlert(**data.model_dump())
            session.add(alert)
            session.commit()
            session.refresh(alert)
            return alert.id
    except Exception as e:
        print(f"Ошибка создания алерта: {e}")
        raise


def get_price_alerts(active_only: bool = True) -> list[PriceAlert]:
    """Получает список алертов."""
    try:
        with Session(engine) as session:
            query = select(PriceAlert)
            if active_only:
                query = query.where(PriceAlert.is_active == True)
            query = query.order_by(PriceAlert.created_at.desc())
            return session.exec(query).all()
    except Exception as e:
        print(f"Ошибка получения алертов: {e}")
        return []


def update_price_alert(alert_id: int, **updates) -> bool:
    """Обновляет алерт."""
    try:
        with Session(engine) as session:
            alert = session.get(PriceAlert, alert_id)
            if not alert:
                return False
            
            for key, value in updates.items():
                if hasattr(alert, key):
                    setattr(alert, key, value)
            
            session.add(alert)
            session.commit()
            return True
    except Exception as e:
        print(f"Ошибка обновления алерта: {e}")
        return False


def delete_price_alert(alert_id: int) -> bool:
    """Удаляет алерт."""
    try:
        with Session(engine) as session:
            alert = session.get(PriceAlert, alert_id)
            if not alert:
                return False
            
            session.delete(alert)
            session.commit()
            return True
    except Exception as e:
        print(f"Ошибка удаления алерта: {e}")
        return False


def check_price_alerts() -> list[dict]:
    """Проверяет все активные алерты и возвращает сработавшие."""
    triggered_alerts = []
    
    try:
        with Session(engine) as session:
            active_alerts = session.exec(
                select(PriceAlert).where(PriceAlert.is_active == True)
            ).all()
            
            for alert in active_alerts:
                try:
                    current_price = get_current_price(alert.coin)
                    if current_price is None:
                        continue
                    
                    triggered = False
                    if alert.alert_type == "above" and current_price >= alert.target_price:
                        triggered = True
                    elif alert.alert_type == "below" and current_price <= alert.target_price:
                        triggered = True
                    
                    if triggered:
                        # Помечаем алерт как сработавший
                        alert.triggered_at = dt.datetime.now()
                        alert.is_active = False
                        session.add(alert)
                        
                        triggered_alerts.append({
                            "alert_id": alert.id,
                            "coin": alert.coin,
                            "target_price": alert.target_price,
                            "current_price": current_price,
                            "alert_type": alert.alert_type,
                            "notes": alert.notes
                        })
                        
                
                except Exception as e:
                    print(f"Ошибка проверки алерта {alert.id}: {e}")
                    continue
            
            session.commit()
            return triggered_alerts
            
    except Exception as e:
        print(f"Ошибка проверки алертов: {e}")
        return []


def get_alert_statistics() -> dict:
    """Возвращает статистику по алертам."""
    try:
        with Session(engine) as session:
            total_alerts = session.exec(select(PriceAlert)).all()
            active_alerts = [a for a in total_alerts if a.is_active]
            triggered_alerts = [a for a in total_alerts if a.triggered_at is not None]
            
            return {
                "total_alerts": len(total_alerts),
                "active_alerts": len(active_alerts),
                "triggered_alerts": len(triggered_alerts),
                "alerts_by_coin": {},
                "alerts_by_type": {}
            }
    except Exception as e:
        print(f"Ошибка получения статистики алертов: {e}")
        return {
            "total_alerts": 0,
            "active_alerts": 0,
            "triggered_alerts": 0,
            "alerts_by_coin": {},
            "alerts_by_type": {}
        }