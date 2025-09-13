from nicegui import ui
from app.core.services import (
    list_transactions, add_transaction, positions_fifo,
    enrich_positions_with_market, export_transactions_csv, export_positions_csv,
    delete_transaction, get_transaction, update_transaction,
)
from app.core.models import TransactionIn
import os

CURRENCY = os.getenv('REPORT_CURRENCY', 'USD').upper()
TYPES = ['buy','sell','exchange_in','exchange_out','deposit','withdrawal']
STRATS = ['long','mid','short','scalp']

def get_pnl_color(value):
    if value > 0:
        return 'text-green-600'
    elif value < 0:
        return 'text-red-600'
    else:
        return 'text-gray-600'

def open_edit_dialog(row, refresh_callback=None):
    data = get_transaction(int(row['id']))
    with ui.dialog() as dialog, ui.card().classes('min-w-[500px] p-6'):
        ui.label(f'Редактировать сделку #{data["id"]}').classes('text-lg font-bold mb-4')
        
        e_coin = ui.input('Монета').props('uppercase').classes('w-full mb-3')
        e_coin.value = data['coin']
        
        e_type = ui.select(TYPES, label='Тип операции', value=data['type']).classes('w-full mb-3')
        
        e_qty = ui.input('Количество').props('type=number inputmode=decimal').classes('w-full mb-3')
        e_qty.value = str(data['quantity'])
        
        e_price = ui.input('Цена за монету').props('type=number inputmode=decimal').classes('w-full mb-3')
        e_price.value = str(data['price'])
        
        e_strat = ui.select(STRATS, label='Стратегия', value=data['strategy']).classes('w-full mb-3')
        
        e_src = ui.input('Источник').classes('w-full mb-3')
        e_src.value = data.get('source') or ''
        
        e_notes = ui.textarea('Заметки').classes('w-full mb-4')
        e_notes.value = data.get('notes') or ''
        
        with ui.row().classes('justify-end gap-3'):
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
                    ui.notify('✅ Сделка обновлена', type='positive')
                    dialog.close()
                    if refresh_callback:
                        refresh_callback()
                except Exception as e:
                    ui.notify(f'❌ Ошибка: {e}', type='negative')
            
            ui.button('Отмена', on_click=dialog.close).props('outline')
            ui.button('Сохранить', on_click=save_changes).props('color=primary')
        
        dialog.open()

def portfolio_page():
    # Заголовок
    with ui.row().classes('items-center gap-3 mb-6'):
        ui.icon('account_balance_wallet').classes('text-3xl text-blue-600')
        ui.label('Криптопортфель').classes('text-3xl font-bold text-gray-800')

    # Фильтры
    with ui.card().classes('p-4 mb-6 bg-gradient-to-r from-blue-50 to-indigo-50'):
        ui.label('Фильтры').classes('text-lg font-semibold mb-3 text-gray-700')
        with ui.row().classes('gap-4 items-end'):
            coin_filter = ui.input('Монета', placeholder='BTC, ETH, SOL...').props('uppercase').classes('w-48')
            strat_filter = ui.select(['(все)'] + STRATS, value='(все)', label='Стратегия').classes('w-32')
            
            def reset_filters():
                coin_filter.value = ''
                strat_filter.value = '(все)'
                refresh()
            ui.button('Сбросить', on_click=reset_filters).props('outline')

    # Вкладки
    tabs = ui.tabs().classes('mb-4')
    with tabs:
        ui.tab('overview', '📊 Обзор')
        ui.tab('positions', '💼 Позиции') 
        ui.tab('transactions', '📝 Сделки')
    
    with ui.tab_panels(tabs, value='overview').classes('w-full'):
        with ui.tab_panel('overview'):
            ui.label('Обзор портфеля').classes('text-xl font-bold mb-4')
            
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
            
            # Таблица позиций
            ui.label('Позиции (FIFO, цены CoinGecko)').classes('text-lg font-semibold mb-3')
            pos_cols = [
                {'name':'coin','label':'💰 Монета','field':'coin','align':'left'},
                {'name':'strategy','label':'🎯 Стратегия','field':'strategy','align':'center'},
                {'name':'quantity','label':'📊 Количество','field':'quantity','align':'right'},
                {'name':'avg_cost','label':'💵 Средняя цена','field':'avg_cost','align':'right'},
                {'name':'price','label':f'📈 Цена ({CURRENCY})','field':'price','align':'right'},
                {'name':'value','label':'💎 Стоимость','field':'value','align':'right'},
                {'name':'unreal_pnl','label':'📊 Нереализ. PnL','field':'unreal_pnl','align':'right'},
                {'name':'unreal_pct','label':'📈 Нереализ. %','field':'unreal_pct','align':'right'},
                {'name':'realized','label':'💰 Реализ. PnL','field':'realized','align':'right'},
            ]
            pos_table1 = ui.table(columns=pos_cols, rows=[], row_key='key').classes('w-full').props('dense bordered')

        with ui.tab_panel('positions'):
            ui.label('Позиции').classes('text-xl font-bold mb-4')
            with ui.row().classes('justify-end mb-4'):
                ui.button('📥 Экспорт CSV', on_click=lambda: export_pos()).props('color=primary icon=download')
            pos_table2 = ui.table(columns=pos_cols, rows=[], row_key='key').classes('w-full').props('dense bordered')

        with ui.tab_panel('transactions'):
            ui.label('Сделки').classes('text-xl font-bold mb-4')
            
            # Форма добавления
            with ui.card().classes('p-4 mb-6 bg-gradient-to-r from-blue-50 to-indigo-50'):
                ui.label('Добавить сделку').classes('text-lg font-semibold mb-4')
                
                with ui.grid(columns=2).classes('gap-4'):
                    coin = ui.input('Монета', placeholder='BTC, ETH, SOL...').props('uppercase').classes('w-full')
                    ttype = ui.select(TYPES, label='Тип операции', value='buy').classes('w-full')
                    qty = ui.input('Количество', placeholder='0.0').props('type=number inputmode=decimal').classes('w-full')
                    price = ui.input('Цена за монету', placeholder='0.00').props('type=number inputmode=decimal').classes('w-full')
                    strategy = ui.select(STRATS, label='Стратегия', value='long').classes('w-full')
                    source = ui.input('Источник', placeholder='Binance, Coinbase...').classes('w-full')
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
                            ui.notify('✅ Сделка добавлена', type='positive')
                            coin.value = ''
                            qty.value = ''
                            price.value = ''
                            source.value = ''
                            notes.value = ''
                            refresh()
                        except Exception as e:
                            ui.notify(f'❌ Ошибка: {e}', type='negative')
                    ui.button('➕ Добавить сделку', on_click=on_add).props('color=primary')
            
            # Таблица сделок
            with ui.row().classes('justify-between items-center mb-4'):
                ui.label('История сделок').classes('text-lg font-semibold')
                ui.button('📥 Экспорт CSV', on_click=lambda: export_tx()).props('color=primary icon=download')
            
            cols = [
                {'name':'id','label':'#','field':'id','align':'center'},
                {'name':'coin','label':'💰 Монета','field':'coin','align':'left'},
                {'name':'type','label':'📊 Тип','field':'type','align':'center'},
                {'name':'quantity','label':'📈 Количество','field':'quantity','align':'right'},
                {'name':'price','label':'💵 Цена','field':'price','align':'right'},
                {'name':'ts_local','label':'📅 Дата/время','field':'ts_local','align':'center'},
                {'name':'strategy','label':'🎯 Стратегия','field':'strategy','align':'center'},
                {'name':'source','label':'🏢 Источник','field':'source','align':'left'},
                {'name':'notes','label':'📝 Заметки','field':'notes','align':'left'},
                {'name':'actions','label':'⚙️ Действия','field':'actions','align':'center'},
            ]
            tx_table = ui.table(columns=cols, rows=[], row_key='id').classes('w-full').props('dense bordered')

            # Добавляем слот для действий
            tx_table.add_slot('body-cell-actions', '''
                <q-td :props="props" auto-width>
                    <q-btn flat size="sm" icon="edit" color="primary" @click="$parent.$emit('edit', props.row)" />
                    <q-btn flat size="sm" icon="delete" color="negative" @click="$parent.$emit('delete', props.row)" />
                </q-td>
            ''')
            
            def handle_edit(e):
                open_edit_dialog(e.args, refresh)
            
            def handle_delete(e):
                delete_transaction(int(e.args['id']))
                ui.notify('✅ Сделка удалена', type='positive')
                refresh()
            
            tx_table.on('edit', handle_edit)
            tx_table.on('delete', handle_delete)

    # Функции
    def export_tx():
        try:
            path = export_transactions_csv()
            ui.notify(f'✅ Экспорт сделок: {path}', type='positive')
        except Exception as e:
            ui.notify(f'❌ Ошибка экспорта: {e}', type='negative')
    
    def export_pos():
        try:
            base = positions_fifo()
            base = apply_filters_positions(base, coin_filter.value, strat_filter.value)
            enriched, _ = enrich_positions_with_market(base, quote=CURRENCY)
            path = export_positions_csv(enriched)
            ui.notify(f'✅ Экспорт позиций: {path}', type='positive')
        except Exception as e:
            ui.notify(f'❌ Ошибка экспорта: {e}', type='negative')

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

    def refresh():
        try:
            # Позиции
            base_positions = positions_fifo()
            base_filtered = apply_filters_positions(base_positions, coin_filter.value, strat_filter.value)
            enriched, totals = enrich_positions_with_market(base_filtered, quote=CURRENCY)
            pos_table1.rows = enriched
            pos_table1.update()
            pos_table2.rows = enriched
            pos_table2.update()

            # Сводка
            total_value_chip.text = f'{totals["total_value"]:,.2f} {CURRENCY}'
            
            unreal_value = totals["total_unreal"]
            unreal_pct = totals["total_unreal_pct"]
            total_unreal_chip.text = f'{unreal_value:+,.2f} {CURRENCY} ({unreal_pct:+.2f}%)'
            total_unreal_chip.classes = f'text-2xl font-bold {get_pnl_color(unreal_value)}'
            
            realized_value = totals["total_realized"]
            total_real_chip.text = f'{realized_value:+,.2f} {CURRENCY}'
            total_real_chip.classes = f'text-2xl font-bold {get_pnl_color(realized_value)}'

            # Сделки
            rows = list_transactions()
            tx_table.rows = rows
            tx_table.update()
            
        except Exception as e:
            ui.notify(f'❌ Ошибка обновления: {e}', type='negative')

    refresh()
