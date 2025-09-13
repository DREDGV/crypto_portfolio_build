from nicegui import ui
from app.core.services import (
    list_transactions, add_transaction, backup_database, positions_fifo,
    enrich_positions_with_market, export_transactions_csv, export_positions_csv,
    delete_transaction, get_transaction, update_transaction,
)
from app.core.models import TransactionIn
import os

CURRENCY = os.getenv('REPORT_CURRENCY', 'USD').upper()
TYPES = ['buy','sell','exchange_in','exchange_out','deposit','withdrawal']
STRATS = ['long','mid','short','scalp']

def table_row_with_actions(row):
    rid = int(row['id'])
    with ui.row().classes('gap-1'):
        ui.button('✏️', on_click=lambda: open_edit_dialog(row)).props('flat size=sm').tooltip('Редактировать')
        ui.button('🗑️', on_click=lambda: (delete_transaction(rid), ui.notify('Удалено', color='positive'), refresh())).props('flat size=sm').tooltip('Удалить')

def open_edit_dialog(row):
    data = get_transaction(int(row['id']))
    with ui.dialog() as dialog, ui.card().classes('min-w-[420px]'):
        ui.label(f'Редактировать сделку #{data["id"]}').classes('text-md font-bold')
        e_coin = ui.input('Монета').props('uppercase'); e_coin.value = data['coin']
        e_type = ui.select(TYPES, label='Тип', value=data['type'])
        e_qty = ui.input('Кол-во').props('type=number inputmode=decimal'); e_qty.value = str(data['quantity'])
        e_price = ui.input('Цена').props('type=number inputmode=decimal'); e_price.value = str(data['price'])
        e_strat = ui.select(STRATS, label='Стратегия', value=data['strategy'])
        e_src = ui.input('Источник'); e_src.value = data.get('source') or ''
        e_notes = ui.input('Заметки'); e_notes.value = data.get('notes') or ''
        with ui.row().classes('mt-2'):
            def save_changes():
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
                ui.notify('Сделка обновлена', color='positive')
                dialog.close(); refresh()
            ui.button('Сохранить', on_click=save_changes)
            ui.button('Отмена', on_click=dialog.close)
        dialog.open()

def portfolio_page():
    ui.label('Портфель').classes('text-xl font-bold')

    # Глобальные фильтры
    with ui.row().classes('gap-4 items-end'):
        coin_filter = ui.input('Фильтр по монете').props('uppercase autocomplete=off autocorrect=off autocapitalize=off spellcheck=false')
        strat_filter = ui.select(['(все)'] + STRATS, value='(все)', label='Стратегия')
        def reset_filters():
            coin_filter.value = ''
            strat_filter.value = '(все)'
            refresh()
        ui.button('Сбросить фильтры', on_click=reset_filters)

    # Вкладки
    tabs = ui.tabs().classes('mt-2')
    with ui.tab_panels(tabs, value='overview'):
        with ui.tab_panel('overview'):
            ui.label('Обзор').classes('text-lg font-bold')
            # краткая сводка
            with ui.row().classes('gap-4'):
                total_value_chip = ui.chip('Текущая стоимость: —')
                total_unreal_chip = ui.chip('Нереализ. PnL: —')
                total_real_chip = ui.chip('Реализ. PnL: —')
            # позиции снизу
            ui.label('Позиции (FIFO, цены CoinGecko)').classes('text-md mt-2')
            pos_cols = [
                {'name':'coin','label':'Монета','field':'coin'},
                {'name':'strategy','label':'Стратегия','field':'strategy'},
                {'name':'quantity','label':'Кол-во','field':'quantity'},
                {'name':'avg_cost','label':'Средняя цена','field':'avg_cost'},
                {'name':'price','label':f'Цена ({CURRENCY})','field':'price'},
                {'name':'value','label':'Текущая стоимость','field':'value'},
                {'name':'unreal_pnl','label':'Нереализ. PnL','field':'unreal_pnl'},
                {'name':'unreal_pct','label':'Нереализ. %','field':'unreal_pct'},
                {'name':'realized','label':'Реализ. PnL','field':'realized'},
            ]
            pos_table1 = ui.table(columns=pos_cols, rows=[], row_key='key').classes('w-full mt-2')

        with ui.tab_panel('positions'):
            ui.label('Позиции').classes('text-lg font-bold')
            pos_table2 = ui.table(columns=pos_cols, rows=[], row_key='key').classes('w-full mt-2')
            with ui.row().classes('mt-2'):
                ui.button('Экспорт позиций (CSV)', on_click=lambda: export_pos())

        with ui.tab_panel('transactions'):
            ui.label('Сделки').classes('text-lg font-bold')
            # форма добавления
            with ui.card().classes('w-full max-w-2xl'):
                ui.label('Добавить сделку').classes('text-md')
                coin = ui.input('Монета (BTC, ETH, ...)').props('uppercase autocomplete=off autocorrect=off autocapitalize=off spellcheck=false')
                ttype = ui.select(TYPES, label='Тип', value='buy')
                qty = ui.input('Количество').props('type=number inputmode=decimal autocomplete=off')
                price = ui.input('Цена за монету').props('type=number inputmode=decimal autocomplete=off')
                strategy = ui.select(STRATS, label='Стратегия', value='long')
                source = ui.input('Источник (биржа/кошелек)').props('autocomplete=off')
                notes = ui.input('Заметки').props('autocomplete=off')
                def on_add():
                    try:
                        data = TransactionIn(
                            coin=(coin.value or '').upper().strip(),
                            type=ttype.value, quantity=float(qty.value or 0),
                            price=float(price.value or 0), strategy=strategy.value,
                            source=(source.value or '').strip(), notes=(notes.value or '').strip()
                        )
                        add_transaction(data); ui.notify('Сделка добавлена', color='positive'); refresh()
                    except Exception as e:
                        ui.notify(f'Ошибка: {e}', color='negative')
                ui.button('Добавить', on_click=on_add).classes('mt-2')

            # таблица сделок с экшенами
            cols = [
                {'name':'id','label':'ID','field':'id'},
                {'name':'coin','label':'Монета','field':'coin'},
                {'name':'type','label':'Тип','field':'type'},
                {'name':'quantity','label':'Кол-во','field':'quantity'},
                {'name':'price','label':'Цена','field':'price'},
                {'name':'ts_local','label':'Дата/время','field':'ts_local'},
                {'name':'strategy','label':'Стратегия','field':'strategy'},
                {'name':'source','label':'Источник','field':'source'},
                {'name':'notes','label':'Заметки','field':'notes'},
                {'name':'actions','label':'Действия','field':'actions'},
            ]
            tx_table = ui.table(columns=cols, rows=[], row_key='id').classes('w-full mt-2')


            tx_table.add_slot('body-cell-actions', table_row_with_actions)

            with ui.row().classes('mt-2'):
                ui.button('Экспорт сделок (CSV)', on_click=lambda: export_tx())

        with ui.tab_panel('alerts'):
            ui.label('Алерты (скоро)').classes('text-lg')

        with ui.tab_panel('analytics'):
            ui.label('Аналитика (скоро — графики, периодический PnL)').classes('text-lg')

    # Экспорт-helpers
    def export_tx():
        path = export_transactions_csv(); ui.notify(f'Экспорт сделок: {path}', color='positive')
    def export_pos():
        base = positions_fifo()
        base = apply_filters_positions(base, coin_filter.value, strat_filter.value)
        enriched, _ = enrich_positions_with_market(base, quote=CURRENCY)
        path = export_positions_csv(enriched); ui.notify(f'Экспорт позиций: {path}', color='positive')

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

    # Обновление всех блоков
    def refresh():
        # позиции для обзора и вкладки «позиции»
        base_positions = positions_fifo()
        base_filtered = apply_filters_positions(base_positions, coin_filter.value, strat_filter.value)
        enriched, totals = enrich_positions_with_market(base_filtered, quote=CURRENCY)
        pos_table1.rows = enriched; pos_table1.update()
        pos_table2.rows = enriched; pos_table2.update()

        # сводка
        total_value_chip.text = f'Текущая стоимость: {totals["total_value"]:.2f} {CURRENCY}'
        total_unreal_chip.text = f'Нереализ. PnL: {totals["total_unreal"]:+.2f} {CURRENCY} ({totals["total_unreal_pct"]:+.2f}%)'
        total_real_chip.text = f'Реализ. PnL: {totals["total_realized"]:+.2f} {CURRENCY}'

        # сделки
        rows = list_transactions()
        rows = apply_filters_tx(rows, coin_filter.value, strat_filter.value)
        tx_table.rows = rows; tx_table.update()

    refresh()
