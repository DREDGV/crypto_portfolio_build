"""
Расширенная аналитика с графиками и интерактивными диаграммами
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from nicegui import ui
from app.core.services import list_transactions, get_portfolio_stats, positions_fifo
from app.adapters.prices import get_current_price


def create_advanced_analytics_tab():
    """Создает вкладку расширенной аналитики с графиками"""
    with ui.column().classes("w-full h-full overflow-y-auto p-4"):
        ui.label("📊 Расширенная аналитика").classes("text-2xl font-bold text-gray-800 mb-4")
        
        # Кнопки управления
        with ui.row().classes("gap-3 mb-4"):
            ui.button("🔄 Обновить графики", icon="refresh").classes("bg-blue-500 text-white").on("click", lambda: refresh_all_charts())
            ui.button("📈 P&L по времени", icon="trending_up").classes("bg-green-500 text-white").on("click", lambda: show_pnl_chart())
            ui.button("📊 Распределение портфеля", icon="pie_chart").classes("bg-purple-500 text-white").on("click", lambda: show_portfolio_distribution())
            ui.button("📉 Анализ волатильности", icon="show_chart").classes("bg-orange-500 text-white").on("click", lambda: show_volatility_analysis())
        
        # Контейнер для графиков
        charts_container = ui.column().classes("w-full")
        
        def refresh_all_charts():
            """Обновляет все графики"""
            charts_container.clear()
            with charts_container:
                create_pnl_timeline_chart()
                create_portfolio_distribution_chart()
                create_volatility_analysis_chart()
        
        def show_pnl_chart():
            """Показывает график P&L по времени"""
            charts_container.clear()
            with charts_container:
                create_pnl_timeline_chart()
        
        def show_portfolio_distribution():
            """Показывает распределение портфеля"""
            charts_container.clear()
            with charts_container:
                create_portfolio_distribution_chart()
        
        def show_volatility_analysis():
            """Показывает анализ волатильности"""
            charts_container.clear()
            with charts_container:
                create_volatility_analysis_chart()
        
        # Загружаем графики при открытии
        refresh_all_charts()


def create_pnl_timeline_chart():
    """Создает график P&L по времени"""
    with ui.card().classes("p-4 bg-white shadow-sm rounded-lg mb-4"):
        ui.label("📈 P&L по времени").classes("text-lg font-semibold text-gray-800 mb-4")
        
        try:
            # Получаем данные транзакций
            transactions = list_transactions()
            
            if not transactions:
                ui.label("Нет данных для построения графика").classes("text-gray-500 text-center py-8")
                return
            
            # Создаем DataFrame для анализа
            df = pd.DataFrame(transactions)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at')
            
            # Рассчитываем кумулятивный P&L
            df['cumulative_invested'] = 0.0
            df['cumulative_value'] = 0.0
            df['cumulative_pnl'] = 0.0
            
            total_invested = 0.0
            total_value = 0.0
            
            for idx, row in df.iterrows():
                if row['type'] in ['buy', 'deposit', 'exchange_in']:
                    total_invested += row['quantity'] * row['price']
                elif row['type'] in ['sell', 'withdrawal', 'exchange_out']:
                    total_invested -= row['quantity'] * row['price']
                
                # Получаем текущую цену для расчета стоимости
                current_price = get_current_price(row['coin']) or row['price']
                if row['type'] in ['buy', 'deposit', 'exchange_in']:
                    total_value += row['quantity'] * current_price
                elif row['type'] in ['sell', 'withdrawal', 'exchange_out']:
                    total_value -= row['quantity'] * current_price
                
                df.at[idx, 'cumulative_invested'] = total_invested
                df.at[idx, 'cumulative_value'] = total_value
                df.at[idx, 'cumulative_pnl'] = total_value - total_invested
            
            # Создаем график
            fig = go.Figure()
            
            # Линия инвестиций
            fig.add_trace(go.Scatter(
                x=df['created_at'],
                y=df['cumulative_invested'],
                mode='lines+markers',
                name='Инвестировано',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            ))
            
            # Линия текущей стоимости
            fig.add_trace(go.Scatter(
                x=df['created_at'],
                y=df['cumulative_value'],
                mode='lines+markers',
                name='Текущая стоимость',
                line=dict(color='green', width=2),
                marker=dict(size=6)
            ))
            
            # Линия P&L
            fig.add_trace(go.Scatter(
                x=df['created_at'],
                y=df['cumulative_pnl'],
                mode='lines+markers',
                name='P&L',
                line=dict(color='red', width=2),
                marker=dict(size=6),
                fill='tonexty'
            ))
            
            # Настройка макета
            fig.update_layout(
                title="P&L по времени",
                xaxis_title="Дата",
                yaxis_title="Сумма ($)",
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            # Добавляем горизонтальную линию на уровне 0
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            # Отображаем график
            ui.plotly(fig).classes("w-full")
            
        except Exception as e:
            ui.label(f"Ошибка построения графика: {e}").classes("text-red-500 text-center py-8")


def create_portfolio_distribution_chart():
    """Создает график распределения портфеля"""
    with ui.card().classes("p-4 bg-white shadow-sm rounded-lg mb-4"):
        ui.label("📊 Распределение портфеля").classes("text-lg font-semibold text-gray-800 mb-4")
        
        try:
            # Получаем данные портфеля
            portfolio_stats = get_portfolio_stats()
            positions = portfolio_stats.get('top_positions', [])
            
            if not positions:
                ui.label("Нет позиций для отображения").classes("text-gray-500 text-center py-8")
                return
            
            # Подготавливаем данные для круговой диаграммы
            labels = []
            values = []
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
            
            for i, pos in enumerate(positions):
                labels.append(f"{pos['coin']} ({pos['strategy']})")
                values.append(pos['value'])
            
            # Создаем круговую диаграмму
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.3,
                marker_colors=colors[:len(labels)]
            )])
            
            fig.update_layout(
                title="Распределение по монетам",
                template='plotly_white',
                height=400,
                showlegend=True
            )
            
            # Отображаем график
            ui.plotly(fig).classes("w-full")
            
            # Дополнительная информация
            with ui.row().classes("w-full gap-4 mt-4"):
                for i, pos in enumerate(positions):
                    percentage = (pos['value'] / sum(p['value'] for p in positions)) * 100
                    with ui.card().classes("p-3 flex-1 text-center"):
                        ui.label(pos['coin']).classes("font-semibold text-gray-800")
                        ui.label(f"${pos['value']:.2f}").classes("text-lg font-bold text-blue-600")
                        ui.label(f"{percentage:.1f}%").classes("text-sm text-gray-500")
        
        except Exception as e:
            ui.label(f"Ошибка построения графика: {e}").classes("text-red-500 text-center py-8")


def create_volatility_analysis_chart():
    """Создает анализ волатильности"""
    with ui.card().classes("p-4 bg-white shadow-sm rounded-lg mb-4"):
        ui.label("📉 Анализ волатильности").classes("text-lg font-semibold text-gray-800 mb-4")
        
        try:
            # Получаем данные портфеля
            portfolio_stats = get_portfolio_stats()
            positions = portfolio_stats.get('top_positions', [])
            
            if not positions:
                ui.label("Нет позиций для анализа").classes("text-gray-500 text-center py-8")
                return
            
            # Создаем данные для анализа
            coins = []
            pnl_percentages = []
            colors = []
            
            for pos in positions:
                coins.append(pos['coin'])
                pnl_pct = pos.get('unreal_pct', 0)
                pnl_percentages.append(pnl_pct)
                
                # Цвет в зависимости от P&L
                if pnl_pct > 0:
                    colors.append('green')
                elif pnl_pct < -10:
                    colors.append('red')
                else:
                    colors.append('orange')
            
            # Создаем столбчатую диаграмму
            fig = go.Figure(data=[
                go.Bar(
                    x=coins,
                    y=pnl_percentages,
                    marker_color=colors,
                    text=[f"{pct:.1f}%" for pct in pnl_percentages],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="P&L по монетам (%)",
                xaxis_title="Монета",
                yaxis_title="P&L (%)",
                template='plotly_white',
                height=400
            )
            
            # Добавляем горизонтальную линию на уровне 0
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            # Отображаем график
            ui.plotly(fig).classes("w-full")
            
            # Статистика волатильности
            with ui.row().classes("w-full gap-4 mt-4"):
                total_pnl = sum(pnl_percentages)
                avg_pnl = total_pnl / len(pnl_percentages) if pnl_percentages else 0
                max_pnl = max(pnl_percentages) if pnl_percentages else 0
                min_pnl = min(pnl_percentages) if pnl_percentages else 0
                
                with ui.card().classes("p-3 flex-1 text-center"):
                    ui.label("Средний P&L").classes("text-sm text-gray-600")
                    ui.label(f"{avg_pnl:.1f}%").classes("text-lg font-bold text-blue-600")
                
                with ui.card().classes("p-3 flex-1 text-center"):
                    ui.label("Лучшая позиция").classes("text-sm text-gray-600")
                    ui.label(f"{max_pnl:.1f}%").classes("text-lg font-bold text-green-600")
                
                with ui.card().classes("p-3 flex-1 text-center"):
                    ui.label("Худшая позиция").classes("text-sm text-gray-600")
                    ui.label(f"{min_pnl:.1f}%").classes("text-lg font-bold text-red-600")
        
        except Exception as e:
            ui.label(f"Ошибка построения графика: {e}").classes("text-red-500 text-center py-8")
