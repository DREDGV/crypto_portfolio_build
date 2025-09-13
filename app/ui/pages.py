from nicegui import ui
from app.core.services import (
    list_transactions, add_transaction, backup_database, positions_fifo,
    enrich_positions_with_market, export_transactions_csv, export_positions_csv,
    delete_transaction, get_transaction, update_transaction,
    get_portfolio_stats, get_transaction_stats,
    add_alert_rule, get_alert_rules, delete_alert_rule, check_alerts, get_alert_history,
)
from app.core.models import TransactionIn
import os

CURRENCY = os.getenv('REPORT_CURRENCY', 'USD').upper()
TYPES = ['buy','sell','exchange_in','exchange_out','deposit','withdrawal']
STRATS = ['long','mid','short','scalp']

# Иконки для типов транзакций
TYPE_ICONS = {
    'buy': '📈',
    'sell': '📉', 
    'exchange_in': '↗️',
    'exchange_out': '↘️',
    'deposit': '💰',
    'withdrawal': '💸'
}

# Иконки для стратегий
STRATEGY_ICONS = {
    'long': '🦅',
    'mid': '⚖️',
    'short': '⚡',
    'scalp': '🎯'
}

# Цвета для PnL
def get_pnl_color(value):
    if value > 0:
        return 'text-green-600'
    elif value < 0:
        return 'text-red-600'
    else:
        return 'text-gray-600'

def table_row_with_actions(row, refresh_callback=None):
    rid = int(row['id'])
    with ui.row().classes('gap-1'):
        ui.button('✏️', on_click=lambda: open_edit_dialog(row, refresh_callback)).props('flat size=sm').tooltip('Редактировать')
        ui.button('🗑️', on_click=lambda: (delete_transaction(rid), ui.notify('Удалено', color='positive'), refresh_callback() if refresh_callback else None)).props('flat size=sm').tooltip('Удалить')

def open_edit_dialog(row, refresh_callback=None):
    data = get_transaction(int(row['id']))
    with ui.dialog() as dialog, ui.card().classes('min-w-[500px] p-6'):
        # Заголовок с иконкой
        with ui.row().classes('items-center gap-2 mb-4'):
            ui.icon('edit').classes('text-blue-600 text-xl')
            ui.label(f'Редактировать сделку #{data["id"]}').classes('text-lg font-bold text-gray-800')
        
        # Форма в две колонки
        with ui.grid(columns=2).classes('gap-4'):
            # Левая колонка
            with ui.column().classes('gap-3'):
                e_coin = ui.input('Монета', placeholder='BTC, ETH, SOL...').props('uppercase').classes('w-full')
                e_coin.value = data['coin']
                
                e_type = ui.select(TYPES, label='Тип операции', value=data['type']).classes('w-full')
                
                e_qty = ui.input('Количество', placeholder='0.0').props('type=number inputmode=decimal').classes('w-full')
                e_qty.value = str(data['quantity'])
                
                e_price = ui.input('Цена за монету', placeholder='0.00').props('type=number inputmode=decimal').classes('w-full')
                e_price.value = str(data['price'])
            
            # Правая колонка
            with ui.column().classes('gap-3'):
                e_strat = ui.select(STRATS, label='Стратегия', value=data['strategy']).classes('w-full')
                
                e_src = ui.input('Источник', placeholder='Binance, Coinbase...').classes('w-full')
                e_src.value = data.get('source') or ''
                
                e_notes = ui.textarea('Заметки', placeholder='Дополнительная информация...').classes('w-full')
                e_notes.value = data.get('notes') or ''
        
        # Кнопки действий
        with ui.row().classes('justify-end gap-3 mt-6'):
            def save_changes():
                try:
                    update_transaction(
                        data['id'],
                        TransactionIn(
                            coin=(e_coin.value or '').upper().strip(),
                            type=e_type.value,
                            quantity=float(e_qty.value or 0),
                            price=float(e_price.value or 0),
                            strategy=e_strat.value,
                            source=(e_src.value or '').strip(),
                            notes=(e_notes.value or '').strip(),
                        )
                    )
                    ui.notify('✅ Сделка успешно обновлена', type='positive')
                    dialog.close()
                    if refresh_callback:
                        refresh_callback()
                except Exception as e:
                    ui.notify(f'❌ Ошибка: {e}', type='negative')
            
            ui.button('Отмена', on_click=dialog.close).props('outline').classes('px-4 py-2')
            ui.button('Сохранить изменения', on_click=save_changes).props('color=primary').classes('px-4 py-2')
        
        dialog.open()

def portfolio_page():
    # Заголовок с иконкой
    with ui.row().classes('items-center gap-3 mb-6'):
        ui.icon('account_balance_wallet').classes('text-3xl text-blue-600')
        ui.label('Криптопортфель').classes('text-3xl font-bold text-gray-800')

    # Карточка с фильтрами
    with ui.card().classes('p-4 mb-6 bg-gradient-to-r from-blue-50 to-indigo-50'):
        ui.label('Фильтры').classes('text-lg font-semibold mb-3 text-gray-700')
        with ui.row().classes('gap-4 items-end'):
            with ui.column().classes('gap-1'):
                ui.label('Монета').classes('text-sm font-medium text-gray-600')
                coin_filter = ui.input(placeholder='BTC, ETH, SOL...').props('uppercase autocomplete=off autocorrect=off autocapitalize=off spellcheck=false').classes('w-48')
            
            with ui.column().classes('gap-1'):
                ui.label('Стратегия').classes('text-sm font-medium text-gray-600')
                strat_filter = ui.select(['(все)'] + STRATS, value='(все)').classes('w-32')
            
            def reset_filters():
                coin_filter.value = ''
                strat_filter.value = '(все)'
                refresh()
            ui.button('Сбросить', on_click=reset_filters).props('outline').classes('px-4 py-2')

    # Вкладки с иконками
    tabs = ui.tabs().classes('mb-4')
    with tabs:
        ui.tab('overview', '📊 Обзор')
        ui.tab('positions', '💼 Позиции') 
        ui.tab('transactions', '📝 Сделки')
        ui.tab('alerts', '🔔 Алерты')
        ui.tab('analytics', '📈 Аналитика')
    
    with ui.tab_panels(tabs, value='overview').classes('w-full'):
        with ui.tab_panel('overview'):
            # Заголовок вкладки
            with ui.row().classes('items-center gap-2 mb-4'):
                ui.icon('dashboard').classes('text-xl text-blue-600')
                ui.label('Обзор портфеля').classes('text-xl font-bold text-gray-800')
            
            # Карточки со сводкой
            with ui.row().classes('gap-4 mb-6'):
                with ui.card().classes('p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500'):
                    with ui.column().classes('gap-1'):
                        ui.label('Общая стоимость').classes('text-sm font-medium text-gray-600')
                        total_value_chip = ui.label('—').classes('text-2xl font-bold text-green-700')
                
                with ui.card().classes('p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border-l-4 border-blue-500'):
                    with ui.column().classes('gap-1'):
                        ui.label('Нереализованный PnL').classes('text-sm font-medium text-gray-600')
                        total_unreal_chip = ui.label('—').classes('text-2xl font-bold')
                
                with ui.card().classes('p-4 bg-gradient-to-r from-purple-50 to-violet-50 border-l-4 border-purple-500'):
                    with ui.column().classes('gap-1'):
                        ui.label('Реализованный PnL').classes('text-sm font-medium text-gray-600')
                        total_real_chip = ui.label('—').classes('text-2xl font-bold')
            
            # Дополнительная аналитика
            with ui.grid(columns=3).classes('gap-4 mb-6'):
                # Статистика по монетам
                with ui.card().classes('p-4 bg-gradient-to-r from-orange-50 to-red-50 border-l-4 border-orange-500'):
                    with ui.column().classes('gap-2'):
                        ui.label('📊 Статистика').classes('text-sm font-medium text-gray-600')
                        coins_count_chip = ui.label('—').classes('text-lg font-bold text-orange-700')
                        positions_count_chip = ui.label('—').classes('text-sm text-gray-600')
                
                # Топ монета
                with ui.card().classes('p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-l-4 border-indigo-500'):
                    with ui.column().classes('gap-2'):
                        ui.label('🏆 Топ позиция').classes('text-sm font-medium text-gray-600')
                        top_coin_chip = ui.label('—').classes('text-lg font-bold text-indigo-700')
                        top_pnl_chip = ui.label('—').classes('text-sm text-gray-600')
                
                # Активность
                with ui.card().classes('p-4 bg-gradient-to-r from-teal-50 to-cyan-50 border-l-4 border-teal-500'):
                    with ui.column().classes('gap-2'):
                        ui.label('⚡ Активность').classes('text-sm font-medium text-gray-600')
                        transactions_count_chip = ui.label('—').classes('text-lg font-bold text-teal-700')
                        strategies_count_chip = ui.label('—').classes('text-sm text-gray-600')
            
            # Детальная аналитика
            with ui.grid(columns=2).classes('gap-6 mb-6'):
                # Статистика по монетам
                with ui.card().classes('p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('currency_exchange').classes('text-lg text-blue-600')
                        ui.label('Распределение по монетам').classes('text-lg font-semibold text-gray-700')
                    coins_table = ui.table(
                        columns=[
                            {'name': 'coin', 'label': 'Монета', 'field': 'coin', 'align': 'left'},
                            {'name': 'value', 'label': 'Стоимость', 'field': 'value', 'align': 'right', 'format': 'currency'},
                            {'name': 'pnl', 'label': 'PnL', 'field': 'pnl', 'align': 'right', 'format': 'currency'},
                            {'name': 'count', 'label': 'Позиций', 'field': 'count', 'align': 'center'}
                        ],
                        rows=[],
                        row_key='coin'
                    ).classes('w-full').props('dense bordered')
                
                # Статистика по стратегиям
                with ui.card().classes('p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('trending_up').classes('text-lg text-green-600')
                        ui.label('Распределение по стратегиям').classes('text-lg font-semibold text-gray-700')
                    strategies_table = ui.table(
                        columns=[
                            {'name': 'strategy', 'label': 'Стратегия', 'field': 'strategy', 'align': 'left'},
                            {'name': 'value', 'label': 'Стоимость', 'field': 'value', 'align': 'right', 'format': 'currency'},
                            {'name': 'pnl', 'label': 'PnL', 'field': 'pnl', 'align': 'right', 'format': 'currency'},
                            {'name': 'count', 'label': 'Позиций', 'field': 'count', 'align': 'center'}
                        ],
                        rows=[],
                        row_key='strategy'
                    ).classes('w-full').props('dense bordered')
            
            # Заголовок таблицы позиций
            with ui.row().classes('items-center gap-2 mb-3'):
                ui.icon('table_chart').classes('text-lg text-gray-600')
                ui.label('Все позиции (FIFO, цены CoinGecko)').classes('text-lg font-semibold text-gray-700')
            pos_cols = [
                {'name':'coin','label':'💰 Монета','field':'coin','align':'left'},
                {'name':'strategy','label':'🎯 Стратегия','field':'strategy','align':'center'},
                {'name':'quantity','label':'📊 Количество','field':'quantity','align':'right','format':'number'},
                {'name':'avg_cost','label':'💵 Средняя цена','field':'avg_cost','align':'right','format':'currency'},
                {'name':'price','label':f'📈 Цена ({CURRENCY})','field':'price','align':'right','format':'currency'},
                {'name':'value','label':'💎 Стоимость','field':'value','align':'right','format':'currency'},
                {'name':'unreal_pnl','label':'📊 Нереализ. PnL','field':'unreal_pnl','align':'right','format':'currency'},
                {'name':'unreal_pct','label':'📈 Нереализ. %','field':'unreal_pct','align':'right','format':'percentage'},
                {'name':'realized','label':'💰 Реализ. PnL','field':'realized','align':'right','format':'currency'},
            ]
            pos_table1 = ui.table(columns=pos_cols, rows=[], row_key='key').classes('w-full mt-2').props('dense bordered')

        with ui.tab_panel('positions'):
            # Заголовок вкладки
            with ui.row().classes('items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('account_balance').classes('text-xl text-blue-600')
                    ui.label('Позиции').classes('text-xl font-bold text-gray-800')
                
                with ui.row().classes('gap-2'):
                    ui.button('📥 Экспорт CSV', on_click=lambda: export_pos()).props('color=primary icon=download').classes('px-4 py-2')
                    ui.button('🔄 Обновить', on_click=refresh).props('outline icon=refresh').classes('px-4 py-2')
            
            # Дополнительные фильтры для позиций
            with ui.card().classes('p-4 mb-4 bg-gradient-to-r from-gray-50 to-blue-50'):
                with ui.row().classes('gap-4 items-end'):
                    with ui.column().classes('gap-1'):
                        ui.label('Сортировка').classes('text-sm font-medium text-gray-600')
                        sort_by = ui.select([
                            {'label': 'По стоимости (убыв.)', 'value': 'value_desc'},
                            {'label': 'По стоимости (возр.)', 'value': 'value_asc'},
                            {'label': 'По PnL (убыв.)', 'value': 'pnl_desc'},
                            {'label': 'По PnL (возр.)', 'value': 'pnl_asc'},
                            {'label': 'По монете', 'value': 'coin'},
                            {'label': 'По стратегии', 'value': 'strategy'}
                        ], value='value_desc').classes('w-48')
                    
                    with ui.column().classes('gap-1'):
                        ui.label('Показать только').classes('text-sm font-medium text-gray-600')
                        show_only = ui.select([
                            {'label': 'Все позиции', 'value': 'all'},
                            {'label': 'Только прибыльные', 'value': 'profit'},
                            {'label': 'Только убыточные', 'value': 'loss'},
                            {'label': 'С нулевым PnL', 'value': 'zero'}
                        ], value='all').classes('w-40')
                    
                    ui.button('Применить', on_click=lambda: apply_position_filters()).props('color=primary').classes('px-4 py-2')
            
            pos_table2 = ui.table(columns=pos_cols, rows=[], row_key='key').classes('w-full').props('dense bordered sortable')

        with ui.tab_panel('transactions'):
            # Заголовок вкладки
            with ui.row().classes('items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('receipt_long').classes('text-xl text-blue-600')
                    ui.label('Сделки').classes('text-xl font-bold text-gray-800')
                
                ui.button('📥 Экспорт CSV', on_click=lambda: export_tx()).props('color=primary icon=download').classes('px-4 py-2')
            
            # Форма добавления сделки
            with ui.card().classes('w-full mb-6 p-6 bg-gradient-to-r from-blue-50 to-indigo-50'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('add_circle').classes('text-lg text-blue-600')
                    ui.label('Добавить новую сделку').classes('text-lg font-semibold text-gray-800')
                
                with ui.grid(columns=2).classes('gap-4'):
                    # Левая колонка
                    with ui.column().classes('gap-3'):
                        coin = ui.input('Монета', placeholder='BTC, ETH, SOL...').props('uppercase autocomplete=off autocorrect=off autocapitalize=off spellcheck=false').classes('w-full')
                        ttype = ui.select(TYPES, label='Тип операции', value='buy').classes('w-full')
                        qty = ui.input('Количество', placeholder='0.0').props('type=number inputmode=decimal autocomplete=off').classes('w-full')
                        price = ui.input('Цена за монету', placeholder='0.00').props('type=number inputmode=decimal autocomplete=off').classes('w-full')
                    
                    # Правая колонка
                    with ui.column().classes('gap-3'):
                        strategy = ui.select(STRATS, label='Стратегия', value='long').classes('w-full')
                        source = ui.input('Источник', placeholder='Binance, Coinbase...').props('autocomplete=off').classes('w-full')
                        notes = ui.textarea('Заметки', placeholder='Дополнительная информация...').classes('w-full')
                
                with ui.row().classes('justify-end mt-4'):
                    def on_add():
                        try:
                            data = TransactionIn(
                                coin=(coin.value or '').upper().strip(),
                                type=ttype.value, quantity=float(qty.value or 0),
                                price=float(price.value or 0), strategy=strategy.value,
                                source=(source.value or '').strip(), notes=(notes.value or '').strip()
                            )
                            add_transaction(data)
                            ui.notify('✅ Сделка успешно добавлена', type='positive')
                            # Очистка формы
                            coin.value = ''
                            qty.value = ''
                            price.value = ''
                            source.value = ''
                            notes.value = ''
                            refresh()
                        except Exception as e:
                            ui.notify(f'❌ Ошибка: {e}', type='negative')
                    ui.button('➕ Добавить сделку', on_click=on_add).props('color=primary').classes('px-6 py-2')

            # Дополнительные фильтры для сделок
            with ui.card().classes('p-4 mb-4 bg-gradient-to-r from-gray-50 to-green-50'):
                with ui.row().classes('gap-4 items-end'):
                    with ui.column().classes('gap-1'):
                        ui.label('Поиск').classes('text-sm font-medium text-gray-600')
                        search_input = ui.input(placeholder='Поиск по монете, источнику, заметкам...').classes('w-64')
                    
                    with ui.column().classes('gap-1'):
                        ui.label('Тип сделки').classes('text-sm font-medium text-gray-600')
                        tx_type_filter = ui.select(['(все)'] + TYPES, value='(все)').classes('w-32')
                    
                    with ui.column().classes('gap-1'):
                        ui.label('Сортировка').classes('text-sm font-medium text-gray-600')
                        tx_sort_by = ui.select([
                            {'label': 'По дате (новые)', 'value': 'date_desc'},
                            {'label': 'По дате (старые)', 'value': 'date_asc'},
                            {'label': 'По монете', 'value': 'coin'},
                            {'label': 'По типу', 'value': 'type'},
                            {'label': 'По сумме', 'value': 'amount'}
                        ], value='date_desc').classes('w-40')
                    
                    with ui.row().classes('gap-2'):
                        ui.button('🔍 Поиск', on_click=lambda: apply_transaction_filters()).props('color=primary').classes('px-4 py-2')
                        ui.button('🔄 Сбросить', on_click=lambda: reset_transaction_filters()).props('outline').classes('px-4 py-2')
            
            # Заголовок таблицы
            with ui.row().classes('items-center gap-2 mb-3'):
                ui.icon('table_rows').classes('text-lg text-gray-600')
                ui.label('История сделок').classes('text-lg font-semibold text-gray-700')
            
            # таблица сделок с экшенами
            cols = [
                {'name':'id','label':'#','field':'id','align':'center','sortable':True},
                {'name':'coin','label':'💰 Монета','field':'coin','align':'left'},
                {'name':'type','label':'📊 Тип','field':'type','align':'center'},
                {'name':'quantity','label':'📈 Количество','field':'quantity','align':'right','format':'number'},
                {'name':'price','label':'💵 Цена','field':'price','align':'right','format':'currency'},
                {'name':'ts_local','label':'📅 Дата/время','field':'ts_local','align':'center'},
                {'name':'strategy','label':'🎯 Стратегия','field':'strategy','align':'center'},
                {'name':'source','label':'🏢 Источник','field':'source','align':'left'},
                {'name':'notes','label':'📝 Заметки','field':'notes','align':'left'},
                {'name':'actions','label':'⚙️ Действия','field':'actions','align':'center'},
            ]
            tx_table = ui.table(columns=cols, rows=[], row_key='id').classes('w-full').props('dense bordered')


            # Используем строковый template для actions колонки
            tx_table.add_slot('body-cell-actions', '''
                <q-td :props="props" auto-width>
                    <q-btn flat size="sm" icon="edit" color="primary" @click="$parent.$emit('edit', props.row)" />
                    <q-btn flat size="sm" icon="delete" color="negative" @click="$parent.$emit('delete', props.row)" />
                </q-td>
            ''')
            
            # Добавляем обработчики событий
            def handle_edit(e):
                open_edit_dialog(e.args, refresh)
            
            def handle_delete(e):
                delete_transaction(int(e.args['id']))
                ui.notify('✅ Сделка удалена', type='positive')
                refresh()
            
            tx_table.on('edit', handle_edit)
            tx_table.on('delete', handle_delete)

        with ui.tab_panel('alerts'):
            # Заголовок вкладки
            with ui.row().classes('items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('notifications').classes('text-xl text-blue-600')
                    ui.label('Алерты').classes('text-xl font-bold text-gray-800')
                
                with ui.row().classes('gap-2'):
                    ui.button('🔍 Проверить', on_click=lambda: check_alerts_now()).props('color=primary icon=refresh').classes('px-4 py-2')
                    ui.button('➕ Добавить', on_click=lambda: open_alert_dialog()).props('outline icon=add').classes('px-4 py-2')
            
            # Форма добавления алерта
            with ui.card().classes('p-4 mb-6 bg-gradient-to-r from-yellow-50 to-orange-50'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('add_alert').classes('text-lg text-orange-600')
                    ui.label('Добавить новое правило алерта').classes('text-lg font-semibold text-gray-800')
                
                with ui.grid(columns=3).classes('gap-4'):
                    with ui.column().classes('gap-2'):
                        ui.label('Монета').classes('text-sm font-medium text-gray-600')
                        alert_coin = ui.input(placeholder='BTC, ETH, SOL...').props('uppercase').classes('w-full')
                    
                    with ui.column().classes('gap-2'):
                        ui.label('Стратегия').classes('text-sm font-medium text-gray-600')
                        alert_strategy = ui.select(['all'] + STRATS, value='all').classes('w-full')
                    
                    with ui.column().classes('gap-2'):
                        ui.label('Тип алерта').classes('text-sm font-medium text-gray-600')
                        alert_type = ui.select([
                            {'label': 'Цена выросла до', 'value': 'price_up'},
                            {'label': 'Цена упала до', 'value': 'price_down'},
                            {'label': 'PnL вырос до', 'value': 'pnl_up'},
                            {'label': 'PnL упал до', 'value': 'pnl_down'}
                        ], value='price_up').classes('w-full')
                
                with ui.grid(columns=2).classes('gap-4 mt-4'):
                    with ui.column().classes('gap-2'):
                        ui.label('Пороговое значение').classes('text-sm font-medium text-gray-600')
                        alert_threshold = ui.input(placeholder='0.00').props('type=number inputmode=decimal').classes('w-full')
                    
                    with ui.column().classes('gap-2'):
                        ui.label('Сообщение (необязательно)').classes('text-sm font-medium text-gray-600')
                        alert_message = ui.input(placeholder='Кастомное сообщение...').classes('w-full')
                
                with ui.row().classes('justify-end mt-4'):
                    def add_alert():
                        try:
                            if not alert_coin.value or not alert_threshold.value:
                                ui.notify('❌ Заполните монету и пороговое значение', type='negative')
                                return
                            
                            add_alert_rule(
                                coin=alert_coin.value.upper().strip(),
                                strategy=alert_strategy.value,
                                alert_type=alert_type.value,
                                threshold=float(alert_threshold.value),
                                message=alert_message.value.strip()
                            )
                            
                            ui.notify('✅ Правило алерта добавлено', type='positive')
                            alert_coin.value = ''
                            alert_threshold.value = ''
                            alert_message.value = ''
                            refresh_alerts()
                        except Exception as e:
                            ui.notify(f'❌ Ошибка: {e}', type='negative')
                    
                    ui.button('➕ Добавить правило', on_click=add_alert).props('color=primary').classes('px-6 py-2')
            
            # Список правил алертов
            with ui.card().classes('p-4 mb-6'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('rule').classes('text-lg text-blue-600')
                    ui.label('Активные правила').classes('text-lg font-semibold text-gray-700')
                
                alerts_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': '#', 'field': 'id', 'align': 'center'},
                        {'name': 'coin', 'label': 'Монета', 'field': 'coin', 'align': 'left'},
                        {'name': 'strategy', 'label': 'Стратегия', 'field': 'strategy', 'align': 'center'},
                        {'name': 'type', 'label': 'Тип', 'field': 'type', 'align': 'center'},
                        {'name': 'threshold', 'label': 'Порог', 'field': 'threshold', 'align': 'right', 'format': 'currency'},
                        {'name': 'message', 'label': 'Сообщение', 'field': 'message', 'align': 'left'},
                        {'name': 'created', 'label': 'Создан', 'field': 'created_at', 'align': 'center'},
                        {'name': 'actions', 'label': 'Действия', 'field': 'actions', 'align': 'center'}
                    ],
                    rows=[],
                    row_key='id'
                ).classes('w-full').props('dense bordered')
                
                # Добавляем слот для кнопок действий
                alerts_table.add_slot('body-cell-actions', '''
                    <q-td :props="props" auto-width>
                        <q-btn flat size="sm" icon="delete" color="negative" @click="$parent.$emit('delete', props.row)" />
                    </q-td>
                ''')
                
                def handle_alert_delete(e):
                    delete_alert_rule(int(e.args['id']))
                    ui.notify('✅ Правило удалено', type='positive')
                    refresh_alerts()
                
                alerts_table.on('delete', handle_alert_delete)
            
            # История срабатываний
            with ui.card().classes('p-4'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('history').classes('text-lg text-green-600')
                    ui.label('История срабатываний').classes('text-lg font-semibold text-gray-700')
                
                history_table = ui.table(
                    columns=[
                        {'name': 'coin', 'label': 'Монета', 'field': 'coin', 'align': 'left'},
                        {'name': 'strategy', 'label': 'Стратегия', 'field': 'strategy', 'align': 'center'},
                        {'name': 'message', 'label': 'Сообщение', 'field': 'message', 'align': 'left'},
                        {'name': 'price', 'label': 'Цена', 'field': 'price', 'align': 'right', 'format': 'currency'},
                        {'name': 'pnl', 'label': 'PnL', 'field': 'pnl', 'align': 'right', 'format': 'currency'},
                        {'name': 'triggered_at', 'label': 'Время', 'field': 'triggered_at', 'align': 'center'}
                    ],
                    rows=[],
                    row_key='rule_id'
                ).classes('w-full').props('dense bordered')
            
            # Функции для работы с алертами
            def check_alerts_now():
                try:
                    triggered = check_alerts()
                    if triggered:
                        for alert in triggered:
                            ui.notify(f'🔔 {alert["message"]}', type='warning', timeout=5000)
                        ui.notify(f'✅ Сработало {len(triggered)} алертов', type='positive')
                    else:
                        ui.notify('ℹ️ Алерты не сработали', type='info')
                    refresh_alerts()
                except Exception as e:
                    ui.notify(f'❌ Ошибка проверки: {e}', type='negative')
            
            def open_alert_dialog():
                # Диалог уже реализован выше в форме
                pass
            
            def refresh_alerts():
                try:
                    # Обновляем таблицу правил
                    rules = get_alert_rules()
                    alerts_table.rows = rules
                    alerts_table.update()
                    
                    # Обновляем историю
                    history = get_alert_history()
                    history_table.rows = history
                    history_table.update()
                except Exception as e:
                    ui.notify(f'❌ Ошибка обновления: {e}', type='negative')
            
            # Инициализация
            refresh_alerts()

        with ui.tab_panel('analytics'):
            # Заголовок вкладки
            with ui.row().classes('items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('analytics').classes('text-xl text-blue-600')
                    ui.label('Аналитика').classes('text-xl font-bold text-gray-800')
                
                ui.button('🔄 Обновить', on_click=lambda: refresh_analytics()).props('outline icon=refresh').classes('px-4 py-2')
            
            # Общая статистика
            with ui.grid(columns=4).classes('gap-4 mb-6'):
                with ui.card().classes('p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border-l-4 border-blue-500'):
                    with ui.column().classes('gap-1'):
                        ui.label('📊 Общая статистика').classes('text-sm font-medium text-gray-600')
                        total_stats_chip = ui.label('—').classes('text-lg font-bold text-blue-700')
                
                with ui.card().classes('p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500'):
                    with ui.column().classes('gap-1'):
                        ui.label('💰 Лучшая позиция').classes('text-sm font-medium text-gray-600')
                        best_position_chip = ui.label('—').classes('text-lg font-bold text-green-700')
                
                with ui.card().classes('p-4 bg-gradient-to-r from-red-50 to-pink-50 border-l-4 border-red-500'):
                    with ui.column().classes('gap-1'):
                        ui.label('📉 Худшая позиция').classes('text-sm font-medium text-gray-600')
                        worst_position_chip = ui.label('—').classes('text-lg font-bold text-red-700')
                
                with ui.card().classes('p-4 bg-gradient-to-r from-purple-50 to-violet-50 border-l-4 border-purple-500'):
                    with ui.column().classes('gap-1'):
                        ui.label('⚡ Активность').classes('text-sm font-medium text-gray-600')
                        activity_chip = ui.label('—').classes('text-lg font-bold text-purple-700')

    # Экспорт-helpers
    def export_tx():
        try:
            path = export_transactions_csv()
            ui.notify(f'✅ Экспорт сделок завершен: {path}', type='positive')
        except Exception as e:
            ui.notify(f'❌ Ошибка экспорта: {e}', type='negative')
    
    def export_pos():
        try:
            base = positions_fifo()
            base = apply_filters_positions(base, coin_filter.value, strat_filter.value)
            enriched, _ = enrich_positions_with_market(base, quote=CURRENCY)
            path = export_positions_csv(enriched)
            ui.notify(f'✅ Экспорт позиций завершен: {path}', type='positive')
        except Exception as e:
            ui.notify(f'❌ Ошибка экспорта: {e}', type='negative')

    # Применение фильтров
    def apply_filters_tx(rows, coin_val, strat_val):
        coin_val = (coin_val or '').upper().strip()
        filtered = []
        for r in rows:
            if coin_val and r['coin'] != coin_val:
                continue
            if strat_val != '(все)' and r['strategy'] != strat_val:
                continue
            filtered.append(r)
        return filtered

    def apply_filters_positions(rows, coin_val, strat_val):
        coin_val = (coin_val or '').upper().strip()
        out = []
        for r in rows:
            if coin_val and r['coin'] != coin_val:
                continue
            if strat_val != '(все)' and r['strategy'] != strat_val:
                continue
            out.append(r)
        return out
    
    def apply_position_filters():
        """Применяет дополнительные фильтры к позициям"""
        try:
            base_positions = positions_fifo()
            base_filtered = apply_filters_positions(base_positions, coin_filter.value, strat_filter.value)
            enriched, _ = enrich_positions_with_market(base_filtered, quote=CURRENCY)
            
            # Фильтрация по PnL
            if show_only.value == 'profit':
                enriched = [p for p in enriched if (p['unreal_pnl'] + p['realized']) > 0]
            elif show_only.value == 'loss':
                enriched = [p for p in enriched if (p['unreal_pnl'] + p['realized']) < 0]
            elif show_only.value == 'zero':
                enriched = [p for p in enriched if abs(p['unreal_pnl'] + p['realized']) < 0.01]
            
            # Сортировка
            if sort_by.value == 'value_desc':
                enriched.sort(key=lambda x: x['value'], reverse=True)
            elif sort_by.value == 'value_asc':
                enriched.sort(key=lambda x: x['value'])
            elif sort_by.value == 'pnl_desc':
                enriched.sort(key=lambda x: x['unreal_pnl'] + x['realized'], reverse=True)
            elif sort_by.value == 'pnl_asc':
                enriched.sort(key=lambda x: x['unreal_pnl'] + x['realized'])
            elif sort_by.value == 'coin':
                enriched.sort(key=lambda x: x['coin'])
            elif sort_by.value == 'strategy':
                enriched.sort(key=lambda x: x['strategy'])
            
            pos_table2.rows = enriched
            pos_table2.update()
            ui.notify(f'✅ Показано {len(enriched)} позиций', type='positive')
        except Exception as e:
            ui.notify(f'❌ Ошибка фильтрации: {e}', type='negative')
    
    def apply_transaction_filters():
        """Применяет фильтры к сделкам"""
        try:
            rows = list_transactions()
            rows = apply_filters_tx(rows, coin_filter.value, strat_filter.value)
            
            # Поиск по тексту
            search_text = (search_input.value or '').lower().strip()
            if search_text:
                rows = [r for r in rows if 
                       search_text in r['coin'].lower() or
                       search_text in (r['source'] or '').lower() or
                       search_text in (r['notes'] or '').lower()]
            
            # Фильтр по типу
            if tx_type_filter.value != '(все)':
                rows = [r for r in rows if r['type'] == tx_type_filter.value]
            
            # Сортировка
            if tx_sort_by.value == 'date_desc':
                rows.sort(key=lambda x: x['ts_local'], reverse=True)
            elif tx_sort_by.value == 'date_asc':
                rows.sort(key=lambda x: x['ts_local'])
            elif tx_sort_by.value == 'coin':
                rows.sort(key=lambda x: x['coin'])
            elif tx_sort_by.value == 'type':
                rows.sort(key=lambda x: x['type'])
            elif tx_sort_by.value == 'amount':
                rows.sort(key=lambda x: x['quantity'] * x['price'], reverse=True)
            
            tx_table.rows = rows
            tx_table.update()
            ui.notify(f'✅ Найдено {len(rows)} сделок', type='positive')
        except Exception as e:
            ui.notify(f'❌ Ошибка поиска: {e}', type='negative')
    
    def reset_transaction_filters():
        """Сбрасывает фильтры сделок"""
        search_input.value = ''
        tx_type_filter.value = '(все)'
        tx_sort_by.value = 'date_desc'
        apply_transaction_filters()

    # Обновление всех блоков
    def refresh():
        try:
            # позиции для обзора и вкладки «позиции»
            base_positions = positions_fifo()
            base_filtered = apply_filters_positions(base_positions, coin_filter.value, strat_filter.value)
            enriched, totals = enrich_positions_with_market(base_filtered, quote=CURRENCY)
            pos_table1.rows = enriched; pos_table1.update()
            pos_table2.rows = enriched; pos_table2.update()

            # сводка с форматированием
            total_value_chip.text = f'{totals["total_value"]:,.2f} {CURRENCY}'
            
            # Нереализованный PnL с цветом
            unreal_value = totals["total_unreal"]
            unreal_pct = totals["total_unreal_pct"]
            total_unreal_chip.text = f'{unreal_value:+,.2f} {CURRENCY} ({unreal_pct:+.2f}%)'
            total_unreal_chip.classes = f'text-2xl font-bold {get_pnl_color(unreal_value)}'
            
            # Реализованный PnL с цветом
            realized_value = totals["total_realized"]
            total_real_chip.text = f'{realized_value:+,.2f} {CURRENCY}'
            total_real_chip.classes = f'text-2xl font-bold {get_pnl_color(realized_value)}'

            # Дополнительная аналитика
            portfolio_stats = get_portfolio_stats()
            transaction_stats = get_transaction_stats()
            
            # Статистика
            coins_count_chip.text = f'{portfolio_stats["summary"]["total_coins"]} монет'
            positions_count_chip.text = f'{portfolio_stats["summary"]["total_positions"]} позиций'
            
            # Топ позиция
            if portfolio_stats["top_positions"]:
                top_pos = portfolio_stats["top_positions"][0]
                top_coin_chip.text = f'{top_pos["coin"]} ({top_pos["strategy"]})'
                top_pnl = top_pos["unreal_pnl"] + top_pos["realized"]
                top_pnl_chip.text = f'{top_pnl:+,.2f} {CURRENCY}'
            else:
                top_coin_chip.text = 'Нет данных'
                top_pnl_chip.text = '—'
            
            # Активность
            transactions_count_chip.text = f'{transaction_stats["total_transactions"]} сделок'
            strategies_count_chip.text = f'{portfolio_stats["summary"]["total_strategies"]} стратегий'
            
            # Таблицы аналитики
            coins_data = []
            for coin, stats in portfolio_stats["coin_stats"].items():
                coins_data.append({
                    'coin': coin,
                    'value': stats['total_value'],
                    'pnl': stats['total_pnl'],
                    'count': stats['positions_count']
                })
            coins_table.rows = sorted(coins_data, key=lambda x: x['value'], reverse=True)
            coins_table.update()
            
            strategies_data = []
            for strategy, stats in portfolio_stats["strategy_stats"].items():
                strategies_data.append({
                    'strategy': strategy,
                    'value': stats['total_value'],
                    'pnl': stats['total_pnl'],
                    'count': stats['positions_count']
                })
            strategies_table.rows = sorted(strategies_data, key=lambda x: x['value'], reverse=True)
            strategies_table.update()

            # сделки
            rows = list_transactions()
            rows = apply_filters_tx(rows, coin_filter.value, strat_filter.value)
            tx_table.rows = rows; tx_table.update()
            
        except Exception as e:
            ui.notify(f'❌ Ошибка обновления данных: {e}', type='negative')

    # Функция для обновления аналитики
    def refresh_analytics():
        try:
            portfolio_stats = get_portfolio_stats()
            transaction_stats = get_transaction_stats()
            
            # Общая статистика
            total_positions = portfolio_stats['summary']['total_positions']
            total_coins = portfolio_stats['summary']['total_coins']
            total_strategies = portfolio_stats['summary']['total_strategies']
            total_transactions = transaction_stats['total_transactions']
            
            total_stats_chip.text = f'{total_positions} позиций, {total_coins} монет'
            
            # Лучшая и худшая позиции
            if portfolio_stats['top_positions']:
                best_pos = portfolio_stats['top_positions'][0]
                best_pnl = best_pos['unreal_pnl'] + best_pos['realized']
                best_position_chip.text = f'{best_pos["coin"]}: {best_pnl:+.0f} {CURRENCY}'
                
                worst_pos = min(portfolio_stats['top_positions'], 
                              key=lambda x: x['unreal_pnl'] + x['realized'])
                worst_pnl = worst_pos['unreal_pnl'] + worst_pos['realized']
                worst_position_chip.text = f'{worst_pos["coin"]}: {worst_pnl:+.0f} {CURRENCY}'
            else:
                best_position_chip.text = 'Нет данных'
                worst_position_chip.text = 'Нет данных'
            
            activity_chip.text = f'{total_transactions} сделок'
            
        except Exception as e:
            ui.notify(f'❌ Ошибка обновления аналитики: {e}', type='negative')

    refresh()
