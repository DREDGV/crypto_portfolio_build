import datetime as dt
import os
import shutil
import time
from collections import defaultdict, deque

from sqlmodel import Session, select

from app.adapters.prices import get_current_price
from app.core.models import Transaction, TransactionIn
from app.storage.db import DB_PATH, engine

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
                "ts_local": ts_local.strftime("%Y-%m-%d %H:%M:%S"),
                "strategy": t.strategy,
                "source": t.source or "",
                "notes": t.notes or "",
            }
        )
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

    return {
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
