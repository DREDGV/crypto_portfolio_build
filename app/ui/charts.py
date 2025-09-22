"""
Модуль для создания графиков и визуализации портфеля.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

from app.core.services import list_transactions, get_current_price


def create_portfolio_distribution_chart() -> str:
    """Создает круговую диаграмму распределения портфеля по монетам."""
    try:
        transactions = list_transactions()
        if not transactions:
            return _create_empty_chart("Нет данных для отображения")
        
        # Подсчитываем общее количество каждой монеты
        coin_balances = {}
        for tx in transactions:
            coin = tx['coin']
            quantity = tx['quantity']
            tx_type = tx['type']
            
            if coin not in coin_balances:
                coin_balances[coin] = 0
            
            if tx_type in ['buy', 'exchange_in', 'deposit']:
                coin_balances[coin] += quantity
            elif tx_type in ['sell', 'exchange_out', 'withdrawal']:
                coin_balances[coin] -= quantity
        
        # Фильтруем только положительные балансы
        positive_balances = {coin: balance for coin, balance in coin_balances.items() if balance > 0}
        
        if not positive_balances:
            return _create_empty_chart("Нет активных позиций")
        
        # Создаем круговую диаграмму
        fig = go.Figure(data=[go.Pie(
            labels=list(positive_balances.keys()),
            values=list(positive_balances.values()),
            hole=0.3,
            textinfo='label+percent',
            textfont_size=12
        )])
        
        fig.update_layout(
            title="Распределение портфеля по монетам",
            title_x=0.5,
            font=dict(size=12),
            height=400,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="portfolio-distribution")
        
    except Exception as e:
        print(f"Ошибка создания диаграммы распределения: {e}")
        return _create_empty_chart(f"Ошибка: {e}")


def create_transactions_timeline_chart() -> str:
    """Создает график временной линии транзакций."""
    try:
        transactions = list_transactions()
        if not transactions:
            return _create_empty_chart("Нет данных для отображения")
        
        # Подготавливаем данные
        df_data = []
        for tx in transactions:
            df_data.append({
                'date': datetime.strptime(tx['created_at'], '%Y-%m-%d %H:%M:%S'),
                'coin': tx['coin'],
                'type': tx['type'],
                'quantity': tx['quantity'],
                'price': tx['price'],
                'value': tx['quantity'] * tx['price']
            })
        
        df = pd.DataFrame(df_data)
        df = df.sort_values('date')
        
        # Создаем график
        fig = go.Figure()
        
        # Группируем по типам транзакций
        colors = {
            'buy': '#2E8B57',      # Зеленый для покупок
            'sell': '#DC143C',     # Красный для продаж
            'exchange_in': '#4169E1',  # Синий для входящих обменов
            'exchange_out': '#FF8C00', # Оранжевый для исходящих обменов
            'deposit': '#32CD32',  # Лайм для депозитов
            'withdrawal': '#FF6347' # Томат для выводов
        }
        
        for tx_type in df['type'].unique():
            type_data = df[df['type'] == tx_type]
            fig.add_trace(go.Scatter(
                x=type_data['date'],
                y=type_data['value'],
                mode='markers',
                name=tx_type,
                marker=dict(
                    color=colors.get(tx_type, '#888888'),
                    size=8,
                    line=dict(width=1, color='white')
                ),
                text=[f"{row['coin']}: {row['quantity']:.4f}" for _, row in type_data.iterrows()],
                hovertemplate='<b>%{text}</b><br>Дата: %{x}<br>Стоимость: %{y:.2f} USD<extra></extra>'
            ))
        
        fig.update_layout(
            title="Временная линия транзакций",
            title_x=0.5,
            xaxis_title="Дата",
            yaxis_title="Стоимость (USD)",
            font=dict(size=12),
            height=400,
            margin=dict(t=50, b=40, l=60, r=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="transactions-timeline")
        
    except Exception as e:
        print(f"Ошибка создания графика временной линии: {e}")
        return _create_empty_chart(f"Ошибка: {e}")


def create_strategy_performance_chart() -> str:
    """Создает график производительности по стратегиям."""
    try:
        transactions = list_transactions()
        if not transactions:
            return _create_empty_chart("Нет данных для отображения")
        
        # Группируем по стратегиям
        strategy_data = {}
        for tx in transactions:
            strategy = tx['strategy']
            if strategy not in strategy_data:
                strategy_data[strategy] = {'buy': 0, 'sell': 0, 'count': 0}
            
            strategy_data[strategy]['count'] += 1
            if tx['type'] in ['buy', 'exchange_in', 'deposit']:
                strategy_data[strategy]['buy'] += tx['quantity'] * tx['price']
            elif tx['type'] in ['sell', 'exchange_out', 'withdrawal']:
                strategy_data[strategy]['sell'] += tx['quantity'] * tx['price']
        
        # Подготавливаем данные для графика
        strategies = list(strategy_data.keys())
        buy_values = [strategy_data[s]['buy'] for s in strategies]
        sell_values = [strategy_data[s]['sell'] for s in strategies]
        counts = [strategy_data[s]['count'] for s in strategies]
        
        # Создаем комбинированный график
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Объемы по стратегиям', 'Количество сделок'),
            vertical_spacing=0.1
        )
        
        # График объемов
        fig.add_trace(
            go.Bar(name='Покупки', x=strategies, y=buy_values, marker_color='#2E8B57'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Продажи', x=strategies, y=sell_values, marker_color='#DC143C'),
            row=1, col=1
        )
        
        # График количества сделок
        fig.add_trace(
            go.Bar(name='Сделки', x=strategies, y=counts, marker_color='#4169E1'),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Производительность по стратегиям",
            title_x=0.5,
            font=dict(size=12),
            height=500,
            margin=dict(t=50, b=40, l=60, r=20),
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Стратегия", row=2, col=1)
        fig.update_yaxes(title_text="Объем (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Количество", row=2, col=1)
        
        return fig.to_html(include_plotlyjs='cdn', div_id="strategy-performance")
        
    except Exception as e:
        print(f"Ошибка создания графика стратегий: {e}")
        return _create_empty_chart(f"Ошибка: {e}")


def create_source_activity_chart() -> str:
    """Создает график активности по источникам."""
    try:
        transactions = list_transactions()
        if not transactions:
            return _create_empty_chart("Нет данных для отображения")
        
        # Подсчитываем активность по источникам
        source_data = {}
        for tx in transactions:
            source = tx['source'] or 'Не указан'
            if source not in source_data:
                source_data[source] = 0
            source_data[source] += 1
        
        # Сортируем по количеству транзакций
        sorted_sources = sorted(source_data.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_sources:
            return _create_empty_chart("Нет данных по источникам")
        
        sources, counts = zip(*sorted_sources)
        
        # Создаем горизонтальную столбчатую диаграмму
        fig = go.Figure(data=[
            go.Bar(
                y=sources,
                x=counts,
                orientation='h',
                marker_color='#4169E1',
                text=counts,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Активность по источникам",
            title_x=0.5,
            xaxis_title="Количество сделок",
            yaxis_title="Источник",
            font=dict(size=12),
            height=400,
            margin=dict(t=50, b=40, l=100, r=20)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="source-activity")
        
    except Exception as e:
        print(f"Ошибка создания графика источников: {e}")
        return _create_empty_chart(f"Ошибка: {e}")


def _create_empty_chart(message: str) -> str:
    """Создает пустой график с сообщением."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False, font_size=16
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=300,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    return fig.to_html(include_plotlyjs='cdn', div_id="empty-chart")


def get_portfolio_summary() -> Dict[str, Any]:
    """Возвращает сводку по портфелю для отображения в карточках."""
    try:
        transactions = list_transactions()
        if not transactions:
            return {
                'total_transactions': 0,
                'unique_coins': 0,
                'total_volume': 0,
                'avg_transaction_size': 0
            }
        
        # Подсчитываем метрики
        total_transactions = len(transactions)
        unique_coins = len(set(tx['coin'] for tx in transactions))
        
        total_volume = sum(tx['quantity'] * tx['price'] for tx in transactions)
        avg_transaction_size = total_volume / total_transactions if total_transactions > 0 else 0
        
        # Подсчитываем активные позиции
        coin_balances = {}
        for tx in transactions:
            coin = tx['coin']
            quantity = tx['quantity']
            tx_type = tx['type']
            
            if coin not in coin_balances:
                coin_balances[coin] = 0
            
            if tx_type in ['buy', 'exchange_in', 'deposit']:
                coin_balances[coin] += quantity
            elif tx_type in ['sell', 'exchange_out', 'withdrawal']:
                coin_balances[coin] -= quantity
        
        active_positions = len([balance for balance in coin_balances.values() if balance > 0])
        
        return {
            'total_transactions': total_transactions,
            'unique_coins': unique_coins,
            'active_positions': active_positions,
            'total_volume': total_volume,
            'avg_transaction_size': avg_transaction_size
        }
        
    except Exception as e:
        print(f"Ошибка получения сводки портфеля: {e}")
        return {
            'total_transactions': 0,
            'unique_coins': 0,
            'active_positions': 0,
            'total_volume': 0,
            'avg_transaction_size': 0
        }
