"""
Модуль расширенной аналитики портфеля
Включает P&L, ROI, статистику по стратегиям
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

from app.core.services import list_transactions, get_portfolio_stats, positions_fifo, enrich_positions_with_market
from app.core.models import Transaction
from app.core.taxonomy import INBOUND_POSITION_TYPES, OUTBOUND_POSITION_TYPES, normalize_transaction_type


def calculate_realized_pnl() -> Dict[str, Any]:
    """Расчет реализованной прибыли/убытка"""
    transactions = list_transactions()
    
    # Группируем транзакции по монетам
    coin_transactions = defaultdict(list)
    for tx in transactions:
        coin_transactions[tx['coin']].append(tx)
    
    realized_pnl = {}
    total_realized_pnl = 0.0
    
    for coin, txs in coin_transactions.items():
        
        # Сортируем по дате
        txs.sort(key=lambda x: x['created_at'])
        
        # Применяем FIFO для расчета реализованного P&L
        buy_queue = []
        realized_pnl_coin = 0.0
        total_bought = 0.0
        total_sold = 0.0
        
        for tx in txs:
        tx_type = normalize_transaction_type(tx['type'])
        if tx_type in INBOUND_POSITION_TYPES:
                qty = tx.get('quantity', 0)
                buy_queue.append({
                    'qty': qty,
                    'price': tx['price'],
                    'date': tx['created_at']
                })
                total_bought += qty * tx['price']
        elif tx_type in OUTBOUND_POSITION_TYPES:
                qty = tx.get('quantity', 0)
                remaining_sell = qty
                sell_price = tx['price']
                
                while remaining_sell > 0 and buy_queue:
                    buy_order = buy_queue[0]
                    
                    if buy_order['qty'] <= remaining_sell:
                        # Полностью закрываем покупку
                        pnl = (sell_price - buy_order['price']) * buy_order['qty']
                        realized_pnl_coin += pnl
                        remaining_sell -= buy_order['qty']
                        buy_queue.pop(0)
                    else:
                        # Частично закрываем покупку
                        pnl = (sell_price - buy_order['price']) * remaining_sell
                        realized_pnl_coin += pnl
                        buy_order['qty'] -= remaining_sell
                        remaining_sell = 0
                
                total_sold += qty * tx['price']
        
        if total_bought > 0 or total_sold > 0:
            realized_pnl[coin] = {
                'realized_pnl': realized_pnl_coin,
                'total_bought': total_bought,
                'total_sold': total_sold,
                'realized_pnl_percent': (realized_pnl_coin / total_bought * 100) if total_bought > 0 else 0,
                'transactions_count': len(txs)
            }
            total_realized_pnl += realized_pnl_coin
    
    return {
        'total_realized_pnl': total_realized_pnl,
        'by_coin': realized_pnl,
        'coins_count': len(realized_pnl)
    }


def calculate_unrealized_pnl() -> Dict[str, Any]:
    """Расчет нереализованной прибыли/убытка"""
    positions = positions_fifo()
    enriched_positions, totals = enrich_positions_with_market(positions)
    
    unrealized_pnl = {}
    total_unrealized_pnl = 0.0
    
    for position in enriched_positions:
        coin = position['coin']
        current_price = position.get('price', 0)
        avg_cost = position.get('avg_cost', 0)
        qty = position.get('quantity', 0)
        
        if current_price > 0 and avg_cost > 0 and qty > 0:
            unrealized_pnl_amount = (current_price - avg_cost) * qty
            unrealized_pnl_percent = ((current_price - avg_cost) / avg_cost) * 100
            
            unrealized_pnl[coin] = {
                'unrealized_pnl': unrealized_pnl_amount,
                'current_price': current_price,
                'avg_cost': avg_cost,
                'qty': qty,
                'current_value': current_price * qty,
                'cost_basis': avg_cost * qty,
                'unrealized_pnl_percent': unrealized_pnl_percent
            }
            total_unrealized_pnl += unrealized_pnl_amount
    
    return {
        'total_unrealized_pnl': total_unrealized_pnl,
        'by_coin': unrealized_pnl,
        'coins_count': len(unrealized_pnl)
    }


def calculate_roi_metrics() -> Dict[str, Any]:
    """Расчет метрик ROI"""
    transactions = list_transactions()
    portfolio_stats = get_portfolio_stats()
    
    # Общие инвестиции
    total_invested = 0.0
    total_withdrawn = 0.0
    
    for tx in transactions:
        qty = tx.get('quantity', tx.get('qty', 0))
        if tx['type'] in ['buy', 'deposit', 'exchange_in']:
            total_invested += qty * tx['price']
        elif tx['type'] in ['sell', 'withdrawal', 'exchange_out']:
            total_withdrawn += qty * tx['price']
    
    # Текущая стоимость портфеля
    current_value = portfolio_stats.get('totals', {}).get('total_value', 0)
    
    # ROI расчеты
    net_invested = total_invested - total_withdrawn
    total_return = current_value - net_invested
    
    roi_percent = (total_return / net_invested * 100) if net_invested > 0 else 0
    roi_absolute = total_return
    
    # ROI по периодам
    roi_by_period = calculate_roi_by_periods()
    
    return {
        'total_invested': total_invested,
        'total_withdrawn': total_withdrawn,
        'net_invested': net_invested,
        'current_value': current_value,
        'total_return': total_return,
        'roi_percent': roi_percent,
        'roi_absolute': roi_absolute,
        'by_periods': roi_by_period
    }


def calculate_roi_by_periods() -> Dict[str, Any]:
    """Расчет ROI по временным периодам"""
    transactions = list_transactions()
    
    if not transactions:
        return {}
    
    # Определяем периоды
    now = datetime.now()
    periods = {
        '1d': now - timedelta(days=1),
        '7d': now - timedelta(days=7),
        '30d': now - timedelta(days=30),
        '90d': now - timedelta(days=90),
        '1y': now - timedelta(days=365)
    }
    
    roi_by_period = {}
    
    for period_name, start_date in periods.items():
        # Фильтруем транзакции по периоду
        period_txs = [
            tx for tx in transactions 
            if datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00')) >= start_date
        ]
        
        if not period_txs:
            continue
        
        # Рассчитываем инвестиции за период
        period_invested = 0.0
        period_withdrawn = 0.0
        
        for tx in period_txs:
            qty = tx.get('quantity', tx.get('qty', 0))
        tx_type = normalize_transaction_type(tx['type'])
        if tx_type in INBOUND_POSITION_TYPES:
                period_invested += qty * tx['price']
        elif tx_type in OUTBOUND_POSITION_TYPES:
                period_withdrawn += qty * tx['price']
        
        period_net = period_invested - period_withdrawn
        
        # Упрощенный расчет ROI за период (только по сделкам)
        if period_net > 0:
            period_roi = ((period_withdrawn - period_invested) / period_invested) * 100
        else:
            period_roi = 0
        
        roi_by_period[period_name] = {
            'invested': period_invested,
            'withdrawn': period_withdrawn,
            'net': period_net,
            'roi_percent': period_roi,
            'transactions_count': len(period_txs)
        }
    
    return roi_by_period


def calculate_strategy_performance() -> Dict[str, Any]:
    """Расчет эффективности стратегий"""
    transactions = list_transactions()
    
    # Группируем по стратегиям
    strategy_stats = defaultdict(lambda: {
        'transactions': [],
        'total_invested': 0.0,
        'total_returned': 0.0,
        'avg_hold_time': 0.0,
        'win_rate': 0.0
    })
    
    for tx in transactions:
        strategy = tx.get('strategy', 'unknown')
        strategy_stats[strategy]['transactions'].append(tx)
        
        qty = tx.get('quantity', tx.get('qty', 0))
        if tx['type'] in ['buy', 'deposit', 'exchange_in']:
            strategy_stats[strategy]['total_invested'] += qty * tx['price']
        elif tx['type'] in ['sell', 'withdrawal', 'exchange_out']:
            strategy_stats[strategy]['total_returned'] += qty * tx['price']
    
    # Рассчитываем метрики для каждой стратегии
    strategy_performance = {}
    
    for strategy, stats in strategy_stats.items():
        txs = stats['transactions']
        if not txs:
            continue
        
        # ROI стратегии
        net_invested = stats['total_invested'] - stats['total_returned']
        roi_percent = (stats['total_returned'] / stats['total_invested'] * 100) if stats['total_invested'] > 0 else 0
        
        # Время удержания позиций
        hold_times = []
        for i, tx in enumerate(txs):
            if tx['type'] in ['buy', 'deposit', 'exchange_in']:
                # Ищем соответствующую продажу
                for j in range(i + 1, len(txs)):
                    if (txs[j]['type'] in ['sell', 'withdrawal', 'exchange_out'] and 
                        txs[j]['coin'] == tx['coin']):
                        buy_date = datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00'))
                        sell_date = datetime.fromisoformat(txs[j]['created_at'].replace('Z', '+00:00'))
                        hold_time = (sell_date - buy_date).days
                        hold_times.append(hold_time)
                        break
        
        avg_hold_time = statistics.mean(hold_times) if hold_times else 0
        
        # Win rate (упрощенный расчет)
        profitable_trades = sum(1 for time in hold_times if time > 0)  # Упрощение
        win_rate = (profitable_trades / len(hold_times) * 100) if hold_times else 0
        
        strategy_performance[strategy] = {
            'transactions_count': len(txs),
            'total_invested': stats['total_invested'],
            'total_returned': stats['total_returned'],
            'net_invested': net_invested,
            'roi_percent': roi_percent,
            'avg_hold_time_days': avg_hold_time,
            'win_rate_percent': win_rate,
            'coins_traded': len(set(tx['coin'] for tx in txs))
        }
    
    return strategy_performance


def calculate_risk_metrics() -> Dict[str, Any]:
    """Расчет метрик риска"""
    transactions = list_transactions()
    portfolio_stats = get_portfolio_stats()
    
    if not transactions:
        return {}
    
    # Волатильность портфеля (упрощенный расчет)
    daily_returns = []
    transaction_dates = []
    
    for tx in transactions:
        date = datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00')).date()
        transaction_dates.append(date)
    
    # Группируем по дням
    daily_pnl = defaultdict(float)
    for tx in transactions:
        date = datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00')).date()
        qty = tx.get('quantity', tx.get('qty', 0))
        if tx['type'] in ['sell', 'withdrawal', 'exchange_out']:
            daily_pnl[date] += qty * tx['price']
        elif tx['type'] in ['buy', 'deposit', 'exchange_in']:
            daily_pnl[date] -= qty * tx['price']
    
    # Рассчитываем волатильность
    if len(daily_pnl) > 1:
        pnl_values = list(daily_pnl.values())
        volatility = statistics.stdev(pnl_values) if len(pnl_values) > 1 else 0
    else:
        volatility = 0
    
    # Максимальная просадка (упрощенный расчет)
    cumulative_pnl = 0
    max_drawdown = 0
    peak = 0
    
    for date in sorted(daily_pnl.keys()):
        cumulative_pnl += daily_pnl[date]
        if cumulative_pnl > peak:
            peak = cumulative_pnl
        drawdown = peak - cumulative_pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return {
        'volatility': volatility,
        'max_drawdown': max_drawdown,
        'max_drawdown_percent': (max_drawdown / peak * 100) if peak > 0 else 0,
        'trading_days': len(daily_pnl),
        'avg_daily_pnl': statistics.mean(list(daily_pnl.values())) if daily_pnl else 0
    }


def get_comprehensive_analytics() -> Dict[str, Any]:
    """Полная аналитика портфеля"""
    return {
        'realized_pnl': calculate_realized_pnl(),
        'unrealized_pnl': calculate_unrealized_pnl(),
        'roi_metrics': calculate_roi_metrics(),
        'strategy_performance': calculate_strategy_performance(),
        'risk_metrics': calculate_risk_metrics(),
        'generated_at': datetime.now().isoformat()
    }


def get_analytics_summary() -> Dict[str, Any]:
    """Краткая сводка аналитики"""
    analytics = get_comprehensive_analytics()
    
    return {
        'total_pnl': (
            analytics['realized_pnl']['total_realized_pnl'] + 
            analytics['unrealized_pnl']['total_unrealized_pnl']
        ),
        'roi_percent': analytics['roi_metrics']['roi_percent'],
        'best_strategy': max(
            analytics['strategy_performance'].items(),
            key=lambda x: x[1]['roi_percent']
        )[0] if analytics['strategy_performance'] else 'N/A',
        'risk_level': 'High' if analytics['risk_metrics']['volatility'] > 1000 else 'Medium' if analytics['risk_metrics']['volatility'] > 500 else 'Low',
        'total_transactions': sum(
            strategy['transactions_count'] 
            for strategy in analytics['strategy_performance'].values()
        )
    }
