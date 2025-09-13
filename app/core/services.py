from sqlmodel import Session, select
from app.core.models import Transaction, TransactionIn
from app.storage.db import engine, DB_PATH
from app.adapters.prices import get_current_price
import shutil, os, time, datetime as dt
from collections import defaultdict, deque

def add_transaction(data: TransactionIn) -> int:
    if not data.coin: raise ValueError('coin is required')
    if data.quantity <= 0: raise ValueError('quantity must be > 0')
    if data.price < 0: raise ValueError('price must be >= 0')
    with Session(engine) as session:
        t = Transaction(**data.model_dump())
        session.add(t); session.commit(); session.refresh(t)
        return t.id

def get_transaction(tx_id: int) -> dict | None:
    with Session(engine) as session:
        t = session.get(Transaction, tx_id)
        if not t: return None
        return {
            'id': t.id, 'coin': t.coin, 'type': t.type, 'quantity': t.quantity,
            'price': t.price, 'strategy': t.strategy, 'source': t.source or '', 'notes': t.notes or '',
            'ts_utc': t.ts_utc,
        }

def update_transaction(tx_id: int, data: TransactionIn) -> None:
    with Session(engine) as session:
        t = session.get(Transaction, tx_id)
        if not t: return
        t.coin = data.coin; t.type = data.type; t.quantity = data.quantity; t.price = data.price
        t.strategy = data.strategy; t.source = data.source; t.notes = data.notes
        session.add(t); session.commit()

def delete_transaction(tx_id: int) -> None:
    with Session(engine) as session:
        t = session.get(Transaction, tx_id)
        if t:
            session.delete(t); session.commit()

def list_transactions() -> list[dict]:
    with Session(engine) as session:
        items = session.exec(select(Transaction).order_by(Transaction.id.desc())).all()
    rows = []
    for t in items:
        ts_local = dt.datetime.fromtimestamp(t.ts_utc.timestamp())
        rows.append({
            'id': t.id, 'coin': t.coin, 'type': t.type,
            'quantity': t.quantity, 'price': t.price,
            'ts_local': ts_local.strftime('%Y-%m-%d %H:%M:%S'),
            'strategy': t.strategy, 'source': t.source or '', 'notes': t.notes or '',
        })
    return rows

def positions_fifo() -> list[dict]:
    with Session(engine) as session:
        items = session.exec(select(Transaction).order_by(Transaction.ts_utc.asc(), Transaction.id.asc())).all()
    lots: dict[tuple[str,str], deque] = defaultdict(deque)
    realized: dict[tuple[str,str], float] = defaultdict(float)
    for t in items:
        key = (t.coin.upper(), t.strategy)
        if t.type in ('buy','exchange_in','deposit'):
            lots[key].append({'qty': float(t.quantity), 'price': float(t.price)})
        elif t.type in ('sell','exchange_out','withdrawal'):
            qty_left = float(t.quantity); sell_price = float(t.price)
            while qty_left > 0 and lots[key]:
                lot = lots[key][0]; take = min(qty_left, lot['qty'])
                realized[key] += take * (sell_price - lot['price'])
                lot['qty'] -= take; qty_left -= take
                if lot['qty'] <= 1e-12: lots[key].popleft()
    positions = []
    for key, queue in lots.items():
        coin, strat = key
        qty = sum(l['qty'] for l in queue); cost = sum(l['qty'] * l['price'] for l in queue)
        avg = (cost / qty) if qty > 0 else 0.0
        positions.append({
            'key': f'{coin}:{strat}', 'coin': coin, 'strategy': strat,
            'quantity': round(qty, 8), 'avg_cost': round(avg, 8),
            'cost_basis': round(cost, 2), 'realized': round(realized[key], 2),
        })
    for key, rpnl in realized.items():
        if rpnl != 0 and all(p['key'] != f'{key[0]}:{key[1]}' for p in positions):
            positions.append({
                'key': f'{key[0]}:{key[1]}', 'coin': key[0], 'strategy': key[1],
                'quantity': 0.0, 'avg_cost': 0.0, 'cost_basis': 0.0, 'realized': round(rpnl, 2),
            })
    return positions

def enrich_positions_with_market(positions: list[dict], quote: str='USD'):
    total_value = 0.0; total_unreal = 0.0; total_realized = 0.0
    enriched = []
    for p in positions:
        price = get_current_price(p['coin'], quote=quote) or 0.0
        value = p['quantity'] * price
        unreal = value - p['cost_basis']
        unreal_pct = (price - p['avg_cost']) / p['avg_cost'] * 100 if p['avg_cost'] > 0 else 0.0
        total_value += value; total_unreal += unreal; total_realized += p['realized']
        enriched.append({**p, 'price': round(price, 6), 'value': round(value, 2),
                         'unreal_pnl': round(unreal, 2), 'unreal_pct': round(unreal_pct, 2)})
    totals = {
        'total_value': round(total_value, 2),
        'total_unreal': round(total_unreal, 2),
        'total_unreal_pct': round((total_unreal / (total_value - total_unreal) * 100) if (total_value - total_unreal) > 0 else 0.0, 2),
        'total_realized': round(total_realized, 2),
    }
    return enriched, totals

def backup_database() -> str:
    backup_dir = os.path.join(os.path.dirname(DB_PATH), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    target = os.path.join(backup_dir, "portfolio_backup_" + time.strftime("%Y%m%d_%H%M%S") + ".db")
    shutil.copy(DB_PATH, target)
    return target

def export_transactions_csv() -> str:
    """Экспортирует все сделки в CSV файл"""
    export_dir = os.path.join(os.path.dirname(DB_PATH), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f"transactions_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_dir, filename)
    
    transactions = list_transactions()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        if not transactions:
            f.write("id,coin,type,quantity,price,ts_local,strategy,source,notes\n")
        else:
            # Заголовки
            headers = list(transactions[0].keys())
            f.write(','.join(headers) + '\n')
            
            # Данные
            for tx in transactions:
                row = []
                for header in headers:
                    value = tx.get(header, '')
                    # Экранируем запятые в значениях
                    if ',' in str(value):
                        value = f'"{value}"'
                    row.append(str(value))
                f.write(','.join(row) + '\n')
    
    return filepath

def export_positions_csv(positions: list[dict]) -> str:
    """Экспортирует позиции в CSV файл"""
    export_dir = os.path.join(os.path.dirname(DB_PATH), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f"positions_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(export_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        if not positions:
            f.write("coin,strategy,quantity,avg_cost,price,value,unreal_pnl,unreal_pct,realized\n")
        else:
            # Заголовки
            headers = list(positions[0].keys())
            f.write(','.join(headers) + '\n')
            
            # Данные
            for pos in positions:
                row = []
                for header in headers:
                    value = pos.get(header, '')
                    # Экранируем запятые в значениях
                    if ',' in str(value):
                        value = f'"{value}"'
                    row.append(str(value))
                f.write(','.join(row) + '\n')
    
    return filepath
